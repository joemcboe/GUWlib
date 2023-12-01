import guwlib.guw_objects as guw_objects
import math

from abaqus import *
from abaqusConstants import *

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
import step

# constant names used throughout all functions
MODEL_NAME = 'guw_model'
PLATE_PART_NAME = 'plate'
REFERENCE_PLATE_PART_NAME = 'reference_plate'


# PART MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def create_plate_part(plate):
    """
    Creates the plate as an Abaqus part by solid extrusion.
    :param guw_objects.IsotropicPlate plate: Plate instance to be modelled in Abaqus.
    :return: None
    """
    # rename the model
    mdb.models.changeKey(fromName='Model-1', toName=MODEL_NAME)

    # create an extrusion from two-dimensional shape
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    s.rectangle(point1=(0, 0), point2=(plate.width, plate.length))
    p = mdb.models[MODEL_NAME].Part(name=PLATE_PART_NAME, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s, depth=plate.thickness)
    del s

    # define datum objects and store abaqus id
    plate.datum_xy_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=plate.thickness).id
    plate.datum_y_axis_id = p.DatumAxisByTwoPoint(point1=(0, 0, plate.thickness), point2=(0, 1, plate.thickness)).id
    plate.datum_z_axis_id = p.DatumAxisByTwoPoint(point1=(0, 0, 0), point2=(0, 0, plate.thickness)).id

    # store plate cell in sets
    p.Set(cells=p.cells, name=plate.cell_set_name)  # contains the plate without the bounding boxes
    p.Set(cells=p.cells, faces=p.faces, name=plate.material_cell_set_name)  # contains the whole plate
    p.Set(faces=p.faces.getByBoundingBox(zMin=plate.thickness / 2), name=plate.top_surf_face_set_name)
    p.Set(faces=p.faces.getByBoundingBox(zMin=plate.thickness / 2), name=plate.field_output_face_set_name)


def create_reference_mesh_plate(plate, element_size):
    """
    Creates and meshes a temporary reference plate without any defects or piezoelectric transducers. The reference mesh
    is used to create suitable partitions on the actual plate part for a better mesh quality.
    :param plate:
    :param element_size:
    :return:
    """
    # create an extrusion from two-dimensional shape
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    s.rectangle(point1=(0, 0), point2=(plate.width, plate.length))
    p = mdb.models[MODEL_NAME].Part(name=REFERENCE_PLATE_PART_NAME, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    p.BaseShell(sketch=s)
    del s

    # seed and mesh part with desired element size
    p.setMeshControls(regions=p.cells, technique=STRUCTURED)
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()


def remove_reference_mesh_plate():
    """
    Removes the temporary reference plate part.
    :return: None
    """
    del mdb.models[MODEL_NAME].parts[REFERENCE_PLATE_PART_NAME]


def create_circ_hole_in_plate(plate, hole, element_size):
    """
    Adds a cut extrude hole to an existing plate part in Abaqus and partitions the region so that structured meshing can
    be applied. The hole position must be on the plate and must not intersect other features already added to the plate.
    :param IsotropicPlate plate: Plate to which the hole is to be added.
    :param Hole hole: Hole that is to be added.
    :param element_size: Desired element size of the FE mesh, needed to determine a suitable position of the partition.
    :return:
    """
    # decompose hole attributes
    circle_pos_x = hole.position_x
    circle_pos_y = hole.position_y
    circle_radius = hole.radius

    # bounding box scaling and name TODO
    boundbox_scale = 2.5

    # add a sketch of the circle on the plate top surface and cut extrude through the plate
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, gridSpacing=0.08, transform=t)
    s.CircleByCenterPerimeter(center=(circle_pos_x, circle_pos_y),
                              point1=(circle_pos_x + circle_radius, circle_pos_y))
    p.CutExtrude(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                 sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # the area around the circular hole needs to be a separate partition, otherwise Abaqus can't mesh the part
    # create a rectangular partition (bounding box) around the hole and adjust the corner coordinates so that they lie
    # on the nodes of a reference structured mesh
    boundbox_radius = boundbox_scale * circle_radius
    x_left, x_right, y_lower, y_upper, x_center, y_center = (
        __get_bounding_box_coordinates_from_reference_mesh(circle_pos_x, circle_pos_y, boundbox_radius,
                                                           element_size))
    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    __add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, hole.bounding_box_cell_set_name)

    # the geometry inside the bounding box needs further partitioning so Abaqus can mesh the region w structured meshing
    # draw a sketch to add four face partitions to the bounding box top surface
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=1.84, gridSpacing=0.04, transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.Line(point1=(x_left, y_center), point2=(circle_pos_x - circle_radius, circle_pos_y))
    s.Line(point1=(circle_pos_x + circle_radius, circle_pos_y), point2=(x_right, y_center))
    s.Line(point1=(x_center, y_lower), point2=(circle_pos_x, circle_pos_y - circle_radius))
    s.Line(point1=(circle_pos_x, circle_pos_y + circle_radius), point2=(x_center, y_upper))

    # find the face of the bounding box with findAt() method and partition the face by the sketch
    x_click = circle_pos_x
    y_click = 0.5 * (circle_pos_y + circle_radius + y_upper)
    picked_faces = p.faces.findAt(((x_click, y_click, plate.thickness),))
    p.PartitionFaceBySketch(sketchUpEdge=p.datums[sketch_up_edge_id], faces=picked_faces, sketch=s)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # use the four generated faces to create cell partitions
    for phi in [i * math.pi for i in [0.25, 0.75, 1.25]]:
        x_click, y_click = (circle_pos_x + 1.2 * circle_radius * math.cos(phi),
                            circle_pos_y + 1.2 * circle_radius * math.sin(phi))
        picked_face = p.faces.findAt(((x_click, y_click, plate.thickness),))
        e = picked_face[0].getEdges()
        cell_to_partition = p.sets[hole.bounding_box_cell_set_name].cells[:]
        p.PartitionCellByExtrudeEdge(cells=cell_to_partition,
                                     line=p.datums[plate.datum_z_axis_id],
                                     edges=[p.edges[i] for i in e],
                                     sense=REVERSE)

    # return the coordinates of the bounding box
    return [x_left, y_lower, x_right, y_upper]


def __add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, bounding_box_cell_name):
    """
    Creates a rectangular cell partition around a defect or piezoelectric transducer and adds it to a set.
    :param plate:
    :param lower_left_coord:
    :param upper_right_coord:
    :param bounding_box_cell_name:
    :return:
    """
    # retrieve Abaqus part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # partition the plate to get a rectangular bounding box around the piezo element position
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, gridSpacing=0.08, transform=t)
    s.rectangle(point1=lower_left_coord, point2=upper_right_coord)

    plate_faces = p.sets[plate.top_surf_face_set_name].faces[0]
    f = p.PartitionFaceBySketch(faces=plate_faces, sketch=s)
    e = p.sets[plate.top_surf_face_set_name].faces[1].getEdges()
    p.PartitionCellByExtrudeEdge(cells=p.sets[plate.cell_set_name].cells[0:1],
                                 line=p.datums[plate.datum_z_axis_id],
                                 edges=[p.edges[i] for i in e[0:4]],
                                 sense=REVERSE)

    # update sets for plate top surface, bounding box, plate, and plate cell
    p.Set(faces=p.sets[plate.top_surf_face_set_name].faces[0:1], name=plate.top_surf_face_set_name)
    boundbox_cell = p.sets[plate.cell_set_name].cells.getByBoundingBox(zMin=0,
                                                                       zMax=plate.thickness,
                                                                       xMin=lower_left_coord[0],
                                                                       yMin=lower_left_coord[1],
                                                                       xMax=upper_right_coord[0],
                                                                       yMax=upper_right_coord[1])
    p.Set(cells=boundbox_cell, name=bounding_box_cell_name)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[plate.cell_set_name], p.sets[bounding_box_cell_name]],
                   name=plate.cell_set_name)


def __get_bounding_box_coordinates_from_reference_mesh(x, y, bounding_box_radius, element_size):
    """
    Returns corner- and edge-center-coordinates that snap to the nearest node of a reference mesh.
    :param x:
    :param y:
    :param bounding_box_radius:
    :param element_size:
    :return:
    """
    p = mdb.models[MODEL_NAME].parts[REFERENCE_PLATE_PART_NAME]

    # lower left corner
    lower_left_corner = p.nodes.getClosest((x - bounding_box_radius, y - bounding_box_radius), numToFind=1,
                                           searchTolerance=element_size * 3)
    if lower_left_corner:
        x_left = lower_left_corner.coordinates[0]
        y_lower = lower_left_corner.coordinates[1]
    else:
        x_left = x - bounding_box_radius
        y_lower = y - bounding_box_radius

    # upper right corner
    upper_right_corner = p.nodes.getClosest((x + bounding_box_radius, y + bounding_box_radius), numToFind=1,
                                            searchTolerance=element_size * 2)
    if upper_right_corner:
        x_right = upper_right_corner.coordinates[0]
        y_upper = upper_right_corner.coordinates[1]
    else:
        x_right = x + bounding_box_radius
        y_upper = y + bounding_box_radius

    # center coordinates
    center_node = p.nodes.getClosest((x, y), numToFind=1,
                                     searchTolerance=element_size * 3)
    if center_node:
        x_center = center_node.coordinates[0]
        y_center = center_node.coordinates[1]
    else:
        x_center = x + bounding_box_radius
        y_center = y + bounding_box_radius

    return x_left, x_right, y_lower, y_upper, x_center, y_center

#
def create_transducer_as_point_load(plate, transducer, element_size):
    """
    Creates a line intersection on the plate part, to ensure that a node is generated at the exact position of the piezo
    element during meshing.

    :param IsotropicPlate plate:
    :param transducer:
    :param element_size:
    :return:
    """
    # decompose piezo attributes
    piezo_pos_x = transducer.position_x
    piezo_pos_y = transducer.position_y
    piezo_radius = transducer.radius

    # constants
    boundbox_scale = 1.0

    # retrieve Abaqus part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # partition the plate to get a rectangular bounding box around the piezo element position
    boundbox_radius = piezo_radius * boundbox_scale
    x_left, x_right, y_lower, y_upper, x_center, y_center = \
        (__get_bounding_box_coordinates_from_reference_mesh(piezo_pos_x, piezo_pos_y, boundbox_radius, element_size))

    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    __add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, transducer.bounding_box_cell_set_name)

    # add line intersection at piezo center location by face partitioning (inside bounding box)
    # draw the lines as a sketch to the top surface
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, gridSpacing=0.08, transform=t)
    s.Line(point1=(x_left, y_center), point2=(piezo_pos_x, piezo_pos_y))
    s.Line(point1=(piezo_pos_x, piezo_pos_y), point2=(x_right, y_center))
    s.Line(point1=(x_center, y_lower), point2=(piezo_pos_x, piezo_pos_y))
    s.Line(point1=(piezo_pos_x, piezo_pos_y), point2=(x_center, y_upper))

    # partition the face
    sketch_face = p.faces.findAt(((piezo_pos_x, piezo_pos_y, plate.thickness),), )
    p.PartitionFaceBySketchThruAll(faces=sketch_face, sketchPlane=p.datums[sketch_plane_id],
                                   sketchUpEdge=p.datums[sketch_up_edge_id], sketchPlaneSide=SIDE1, sketch=s)

    # add line intersection point to piezo node set
    intersection_point = p.vertices.findAt(((piezo_pos_x, piezo_pos_y, plate.thickness),))
    p.Set(name=transducer.cell_set_name, vertices=intersection_point)

    return [x_left, y_lower, x_right, y_upper]


def add_rectangular_partition_to_plate(plate, left, lower, right, top):
    """
    Creates a rectangular cell partition from the plate that can be meshed using structured meshing.
    :param plate:
    :param left:
    :param lower:
    :param right:
    :param top:
    :param cell_name:
    :return:
    """
    status = 0
    warning = ""

    # retrieve Abaqus part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # partition the plate to get a rectangular partition that cen be meshed using structured meshing
    # draw the rectangular region
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, gridSpacing=0.08, transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.rectangle(point1=(left, lower), point2=(right, top))

    # create a face partition from the sketch on the plates top surface
    plate_faces = p.sets[plate.top_surf_face_set_name].faces.findAt((((left + right) / 2, (lower + top) / 2, plate.thickness),))
    try:
        f = p.PartitionFaceBySketch(faces=plate_faces[0], sketch=s)
        del mdb.models[MODEL_NAME].sketches['__profile__']
    except Exception as e:
        warning = ("Face partition could not be created: {}. "
                   "Probably the target region is already rectangular.".format(e))
        status = 1
        return status, warning

    # get the rectangular regions face and use its edges to create a cell partition
    rectangular_face = p.sets[plate.top_surf_face_set_name].faces.getByBoundingBox(zMin=plate.thickness, zMax=plate.thickness,
                                                                          xMin=left, yMin=lower, xMax=right, yMax=top)
    e = rectangular_face[0].getEdges()
    cell_to_partition = p.sets[plate.cell_set_name].cells.findAt(
        ((left + right) / 2, (lower + top) / 2, plate.thickness / 2), )
    try:
        p.PartitionCellByExtrudeEdge(cells=cell_to_partition, line=p.datums[plate.datum_z_axis_id],
                                     edges=[p.edges[i] for i in e], sense=REVERSE)
    except Exception as e:
        warning = ("Cell partition could not be created: {}. "
                   "Probably the target region is already rectangular.".format(e))
        status = 1
        return status, warning

    return status, warning
#
#
#
#
#
#
# # PROPERTY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
# def create_material(material_name):
#     try:
#         material_properties = get_material_properties(material_name)
#
#         type_of_material = material_properties["type"]
#         if type_of_material == "isotropic":
#             mdb.models[MODEL_NAME].Material(name=material_name)
#             mdb.models[MODEL_NAME].materials[material_name].Density(table=((material_properties["density"],),))
#             mdb.models[MODEL_NAME].materials[material_name].Elastic(table=((material_properties["youngs_modulus"],
#                                                                             material_properties["poissons_ratio"]),))
#         if type_of_material == "piezo_electric":
#             mdb.models[MODEL_NAME].Material(name=material_name)
#             mdb.models[MODEL_NAME].materials[material_name].Density(table=((material_properties["density"],),))
#             mdb.models[MODEL_NAME].materials[material_name].Elastic(type=ENGINEERING_CONSTANTS,
#                                                                     table=material_properties[
#                                                                         "elastic_engineering_constants_table"])
#             mdb.models[MODEL_NAME].materials[material_name].Dielectric(type=ORTHOTROPIC, table=material_properties[
#                 "dielectric_orthotropic_table"])
#             mdb.models[MODEL_NAME].materials[material_name].Piezoelectric(type=STRAIN, table=material_properties[
#                 "piezo_electric_strain_table"])
#     except ValueError as e:
#         log_error(e)
#
#
# def assign_material(set_name, material, use_continuum_shell_elements=False, shell_thickness=None):
#     if use_continuum_shell_elements:
#         # create new homogenous shell section
#         section_name = set_name + '_shell_section_homogenous_' + material
#         mdb.models[MODEL_NAME].HomogeneousShellSection(name=section_name,
#                                                        preIntegrate=ON, material=material, thicknessType=UNIFORM,
#                                                        thickness=shell_thickness, thicknessField='',
#                                                        nodalThicknessField='', idealization=NO_IDEALIZATION,
#                                                        poissonDefinition=DEFAULT, thicknessModulus=None, useDensity=OFF)
#         p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
#         p.SectionAssignment(region=p.sets[set_name], sectionName=section_name, offset=0.0,
#                             offsetType=MIDDLE_SURFACE, offsetField='',
#                             thicknessAssignment=FROM_SECTION)
#     else:
#         # create new homogenous continuum section
#         section_name = set_name + '_continuum_section_homogenous_' + material
#         mdb.models[MODEL_NAME].HomogeneousSolidSection(name=section_name, material=material, thickness=None)
#
#         # create new set containing all cells and assign section to set
#         p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
#         p.SectionAssignment(region=p.sets[set_name], sectionName=section_name, offset=0.0, offsetType=MIDDLE_SURFACE,
#                             offsetField='', thicknessAssignment=FROM_SECTION)
#
#
# # MESH MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
# def mesh_part_point_force_approach(element_size_in_plane, element_size_thru_thickness, plate, phased_array, defects,
#                                    use_continuum_shell_elements=False):
#     # continuum shell element type
#     element_type_1 = mesh.ElemType(elemCode=SC8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF,  ## todo
#                                    hourglassControl=DEFAULT)
#     element_type_2 = mesh.ElemType(elemCode=SC6R, elemLibrary=EXPLICIT)
#     element_type_3 = mesh.ElemType(elemCode=UNKNOWN_TET, elemLibrary=EXPLICIT)
#
#     # set meshing algorithm for plate
#     p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
#     p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)
#
#     # set element type to continuum shell elements, if requested
#     if use_continuum_shell_elements:
#         p.setElementType(regions=(p.cells,),
#                          elemTypes=(element_type_1, element_type_2, element_type_3))
#         p.assignStackDirection(referenceRegion=p.sets[plate.top_surf_face_set_name].faces[0], cells=p.cells)
#
#     # set meshing algorithm for piezo elements
#     for i in range(len(phased_array)):
#         boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, i, BOUNDBOX_CELL_NAME)
#         p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=MEDIAL_AXIS)
#
#     for i in range(len(defects)):
#         boundbox_cell_name = '{}_{}_{}'.format(DEFECT_CELL_NAME, i, BOUNDBOX_CELL_NAME)
#         p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=MEDIAL_AXIS)
#
#     # seed and mesh part with desired in-plane element size
#     p.seedPart(size=element_size_in_plane, deviationFactor=0.1, minSizeFactor=0.1)
#
#     # seed all vertical edges with through-thickness element size
#     vertical_edge_indices = []
#     for edge in p.edges:
#         vertex_indices = edge.getVertices()
#         if len(vertex_indices) == 2:
#             x1, y1 = p.vertices[vertex_indices[0]].pointOn[0][0:2]
#             x2, y2 = p.vertices[vertex_indices[1]].pointOn[0][0:2]
#             if (x2 - x1) == 0 and (y2 - y1) == 0:
#                 vertical_edge_indices.append(edge.index)
#     if len(vertical_edge_indices) > 0:
#         p.seedEdgeBySize(edges=[p.edges[i] for i in vertical_edge_indices], size=element_size_thru_thickness)
#     else:
#         log_warning("Something is wrong - no vertical edges found!")
#
#     p.generateMesh()
#
#     mesh_stats = p.getMeshStats()
#     log_info("The FE model has {} nodes.".format(mesh_stats.numNodes))
#
#     return mesh_stats.numNodes
#
#
# def create_dispersion_2d_fft_node_set(plate, piezo, element_size_in_plane, element_size_thru_thickness, set_name):
#     x_left, x_right, y_lower, y_upper, x_center, y_center = \
#         __get_bounding_box_coordinates_from_reference_mesh(piezo.position_x, piezo.position_y,
#                                                            piezo.radius, element_size_in_plane)
#     x_min = x_right - element_size_in_plane / 2
#     y_min = y_center - element_size_in_plane / 2
#     x_max = plate.width + element_size_in_plane / 2
#     y_max = y_center + element_size_in_plane / 2
#     z_min = plate.thickness - element_size_thru_thickness / 2
#     z_max = plate.thickness + element_size_thru_thickness / 2
#
#     p = p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
#     nodes = p.nodes.getByBoundingBox(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max, zMax=z_max, zMin=z_min)
#     p.Set(nodes=nodes, name=set_name)
#
#
# # ASSEMBLY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
# def assemble():
#     p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
#     a = mdb.models[MODEL_NAME].rootAssembly
#     a.DatumCsysByDefault(CARTESIAN)
#     a.Instance(name=INSTANCE_NAME, part=p, dependent=ON)
#     session.viewports['Viewport: 1'].setValues(displayedObject=a)
#     session.viewports['Viewport: 1'].assemblyDisplay.setValues(optimizationTasks=OFF, geometricRestrictions=OFF,
#                                                                stopConditions=OFF)
#
#
# def make_datums_invisible():
#     # function to hide all datum objects and set the projection to PARALLEL
#     v = session.viewports['Viewport: 1']
#     v.view.setProjection(projection=PARALLEL)
#     v.partDisplay.geometryOptions.setValues(datumPoints=OFF, datumAxes=OFF, datumPlanes=OFF, datumCoordSystems=OFF)
#     v.assemblyDisplay.geometryOptions.setValues(datumPoints=OFF, datumAxes=OFF, datumPlanes=OFF, datumCoordSystems=OFF)
#
#
# # STEP / LOAD MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------
# def remove_all_steps():
#     model = mdb.models[MODEL_NAME]
#     for step_name in reversed(model.steps.keys()):
#         if step_name != 'Initial':
#             del model.steps[step_name]
#
#
# def create_step_dynamic_explicit(step_name, previous_step_name, time_period, max_increment):
#     # create dynamic, explicit step
#     m = mdb.models[MODEL_NAME]
#     m.ExplicitDynamicsStep(name=step_name,
#                            previous=previous_step_name if previous_step_name is not None else 'Initial',
#                            description='',
#                            timePeriod=time_period,
#                            maxIncrement=max_increment,
#                            nlgeom=OFF)
#
#
# def remove_standard_field_output_request():
#     # delete standard field output request
#     if hasattr(mdb.models[MODEL_NAME], 'fieldOutputRequests'):
#         if 'F-Output-1' in mdb.models[MODEL_NAME].fieldOutputRequests:
#             del mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1']
#
#
# def add_piezo_signal_history_output_request(phased_array, create_step_name):
#     for i, piezo in enumerate(phased_array):
#         a = mdb.models[MODEL_NAME].rootAssembly
#         region_def = a.instances[INSTANCE_NAME].sets[piezo.cell_set_name]
#         mdb.models[MODEL_NAME].HistoryOutputRequest(name='piezo_{}_out'.format(i),
#                                                     createStepName=create_step_name,
#                                                     variables=('U1', 'U2', 'U3'),
#                                                     frequency=1,
#                                                     region=region_def,
#                                                     sectionPoints=DEFAULT,
#                                                     rebar=EXCLUDE)
#
#
# def add_field_output_request(plate, create_step_name, time_interval):
#     region = mdb.models[MODEL_NAME].rootAssembly.allInstances[INSTANCE_NAME].sets[plate.field_output_face_set_name]
#     mdb.models[MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
#                                               createStepName=create_step_name, variables=('UT',),
#                                               timeInterval=time_interval, region=region, sectionPoints=DEFAULT)
#     # mdb.models[MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
#     #                                           createStepName=create_step_name, variables=('U',),
#     #                                           timeInterval=EVERY_TIME_INCREMENT, position=NODES)
#
#
# def add_full_field_output_request(plate, create_step_name, time_interval):
#     # todo remove
#     mdb.models[MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
#                                               createStepName=create_step_name, variables=('UT',),
#                                               timeInterval=time_interval)
#
#
# def add_2d_fft_field_output_request(create_step_name, time_interval, set_name):
#     region = mdb.models[MODEL_NAME].rootAssembly.allInstances[INSTANCE_NAME].sets[set_name]
#     mdb.models[MODEL_NAME].FieldOutputRequest(name=set_name,
#                                               createStepName=create_step_name, variables=('UT',),
#                                               timeInterval=time_interval, region=region, sectionPoints=DEFAULT)
#
#
# def add_amplitude(name, signal, max_time_increment):
#     # generate time data
#     if isinstance(signal, DiracImpulse):
#         # impulses are handled differently than other signals to ensure that the impulse is only
#         # nonzero for the very first Abaqus/Explicit increment
#         time_data_table = [(0, signal.magnitude), (max_time_increment * 1e-2, 0)]
#     else:
#         # all other signals besides impulses can be sampled from the signal definition in their method 'get_value_at'
#         time_data_table = []
#         for t in np.arange(start=signal.dt, stop=signal.dt + signal.get_duration() * 1.01, step=max_time_increment / 2):
#             time_data_table.append((t, signal.get_value_at(t=t)))
#
#     # create amplitude in Abaqus
#     mdb.models[MODEL_NAME].TabularAmplitude(name=name, timeSpan=STEP, smooth=SOLVER_DEFAULT,
#                                             data=tuple(time_data_table))
#
#
# def add_piezo_point_force(load_name, step_name, piezo, signal, max_time_increment):
#     add_amplitude(load_name, signal, max_time_increment)
#     a = mdb.models[MODEL_NAME].rootAssembly
#     region = a.instances[INSTANCE_NAME].sets[piezo.cell_set_name]
#     mdb.models[MODEL_NAME].ConcentratedForce(name=load_name, createStepName=step_name, region=region, cf3=1.0,
#                                              amplitude=load_name, distributionType=UNIFORM,
#                                              field='', localCsys=None)
#
#
# def write_input_file(job_name, num_cpus=1):
#     if num_cpus == 1:
#         pass
#         mdb.Job(name=job_name, model=MODEL_NAME, description='', type=ANALYSIS,
#                 atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
#                 memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
#                 nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
#                 contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
#                 resultsFormat=ODB)
#     else:
#         mdb.Job(name=job_name, model=MODEL_NAME, description='', type=ANALYSIS,
#                 atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
#                 memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
#                 nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
#                 contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
#                 resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=num_cpus,
#                 activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=num_cpus)
#     mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
#
#
