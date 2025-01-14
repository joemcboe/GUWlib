"""
Bottom-level helper-functions to automate specific modelling tasks in ABAQUS/CAE using ABAQUS scripting interface. Note
that these functions are only available from the ABAQUS python interpreter.
"""

import os
import math
import numpy as np

from guwlib import *
import guwlib.functions_utility.console_output

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
def create_isotropic_rectangular_plate_part(plate):
    """
    Creates the geometry of a rectangular isotropic plate as an ABAQUS part by solid extrusion.

    :param IsotropicRectangularPlate plate: Plate instance to be modelled in ABAQUS.
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


def create_reference_mesh_plate_part(plate, element_size):
    """
    Creates and meshes a temporary reference plate without any defects or transducers. The reference mesh
    is used to create suitable partitions on the actual plate part for a better mesh quality.

    :param IsotropicRectangular plate: Plate instance for which to create the reference part in ABAQUS.
    :param float element_size: Desired element size (in-plane) used for meshing.
    :return: None
    """
    # create an extrusion from two-dimensional shape
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    s.rectangle(point1=(0, 0), point2=(plate.width, plate.length))
    p = mdb.models[MODEL_NAME].Part(name=REFERENCE_PLATE_PART_NAME, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    p.BaseShell(sketch=s)
    del s

    # seed and mesh part with desired element size using structured meshing
    p.setMeshControls(regions=p.cells, technique=STRUCTURED)
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()


def remove_reference_mesh_plate_part():
    """
    Removes the temporary reference plate part.
    :return: None
    """
    del mdb.models[MODEL_NAME].parts[REFERENCE_PLATE_PART_NAME]


def create_circular_hole_in_plate(plate, hole, element_size):
    """
    Adds a cut extrude hole to an existing plate part in ABAQUS.

    Around the hole, a rectangular partition is created (bounding box). This is necessary to create structured meshes.
    The hole position must be on the plate and must not intersect other geometry features already added to the plate.

    :param IsotropicRectangularPlate plate: Plate to which the hole is added.
    :param Hole hole: Hole to add.
    :param float element_size: Desired element size (in-plane) of the mesh. Value is needed for partitioning.
    :return: Bounding box coordinates.
    :rtype: list[float, float, float, float]
    """
    # decompose hole attributes
    circle_pos_x = hole.position_x
    circle_pos_y = hole.position_y
    circle_radius = hole.radius

    # bounding box scaling TODO: make this an instance variable of Hole
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

    # the area around the circular hole needs to be a separate partition, otherwise ABAQUS cannot mesh the part
    # create a rectangular partition (bounding box) around the hole and adjust the corner coordinates so that they lie
    # on the nodes of a reference structured mesh
    boundbox_radius = boundbox_scale * circle_radius
    x_left, x_right, y_lower, y_upper, x_center, y_center = (
        __get_bounding_box_coordinates_from_reference_mesh(circle_pos_x, circle_pos_y, boundbox_radius,
                                                           element_size))
    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    __add_rectangular_cell_partition_to_plate(plate, lower_left_coord, upper_right_coord,
                                              hole.bounding_box_cell_set_name)

    # the geometry inside the bounding box needs further partitioning so ABAQUS can mesh the region w structured meshing
    # draw a sketch to add four face partitions to the bounding box top surface
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=1.84, gridSpacing=0.04, transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.Line(point1=(x_left, y_center), point2=(circle_pos_x - circle_radius, circle_pos_y))
    s.Line(point1=(circle_pos_x + circle_radius, circle_pos_y), point2=(x_right, y_center))
    s.Line(point1=(x_center, y_lower), point2=(circle_pos_x, circle_pos_y - circle_radius))
    s.Line(point1=(circle_pos_x, circle_pos_y + circle_radius), point2=(x_center, y_upper))

    # find the face of the bounding box with findAt() method and partition the face with the sketch
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


def create_crack_in_plate(plate, crack, element_size):
    """
    Adds a simple crack to an existing plate part in ABAQUS. A seam must be assigned to the crack edges afterward
    to separate the nodes.

    Around the crack, a rectangular partition is created (bounding box). This is necessary to create structured meshes.
    The cracks position must be on the plate and must not intersect other geometry features already added to the plate.

    :param IsotropicRectangularPlate plate: Plate to which the crack is added.
    :param Crack crack: Crack to add.
    :param float element_size: Desired element size (in-plane) of the mesh. Value is needed for partitioning.
    :return: Bounding box coordinates.
    :rtype: list[float, float, float, float]
    """
    # decompose crack attributes
    crack_pos_x = crack.position_x
    crack_pos_y = crack.position_y
    crack_length = crack.length
    crack_angle = crack.angle % math.pi

    # retrieve part
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]

    # bounding box scaling and name TODO
    boundbox_scale = 1.5

    # the area around the crack needs to be a separate partition, otherwise ABAQUS can't mesh the part
    # create a rectangular partition (bounding box) around the crack and adjust the corner coordinates so that they lie
    # on the nodes of a reference structured mesh
    boundbox_radius = boundbox_scale * crack_length * 0.5
    x_left, x_right, y_lower, y_upper, x_center, y_center = (
        __get_bounding_box_coordinates_from_reference_mesh(crack_pos_x, crack_pos_y, boundbox_radius, element_size))
    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    __add_rectangular_cell_partition_to_plate(plate, lower_left_coord, upper_right_coord,
                                              crack.bounding_box_cell_set_name)

    # calculate helper coordinates and add datum points
    c, s = (np.cos(crack_angle), np.sin(crack_angle))
    rotation_matrix = np.array([[c, -s], [s, c]])
    crack_center = np.array([crack_pos_x, crack_pos_y])
    crack_start = crack_center + np.dot(rotation_matrix, np.array([0, crack_length / 2]))
    crack_end = crack_center + np.dot(rotation_matrix, np.array([0, -crack_length / 2]))
    if (crack_angle > 45 * math.pi / 180) and (crack_angle < 135 * math.pi / 180):
        boundary_start = [x_left, crack_start[1]]
        boundary_end = [x_right, crack_end[1]]
    else:
        boundary_start = [crack_start[0], y_upper]
        boundary_end = [crack_end[0], y_lower]
    crack_top_start_datum_point = p.DatumPointByCoordinate(coords=(crack_start[0], crack_start[1], plate.thickness)).id
    crack_bot_start_datum_point = p.DatumPointByCoordinate(coords=(crack_start[0], crack_start[1], 0)).id
    crack_top_end_datum_point = p.DatumPointByCoordinate(coords=(crack_end[0], crack_end[1], plate.thickness)).id
    crack_bot_end_datum_point = p.DatumPointByCoordinate(coords=(crack_end[0], crack_end[1], 0)).id

    # partition cell to add crack surfaces
    f = p.faces.findAt(((crack_pos_x, crack_pos_y, plate.thickness),))
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, transform=t)

    s.Line(point1=(boundary_start[0], boundary_start[1]), point2=(crack_start[0], crack_start[1]))
    s.Line(point1=(crack_start[0], crack_start[1]), point2=(crack_end[0], crack_end[1]))
    s.Line(point1=(crack_end[0], crack_end[1]), point2=(boundary_end[0], boundary_end[1]))
    p.PartitionFaceBySketchThruAll(faces=f, sketch=s, sketchPlane=p.datums[sketch_plane_id],
                                   sketchUpEdge=p.datums[sketch_up_edge_id], sketchPlaneSide=SIDE1)

    f = p.faces.findAt(((crack_pos_x, crack_pos_y, plate.thickness),))
    e = f[0].getEdges()
    p.PartitionCellByExtrudeEdge(cells=p.sets[crack.bounding_box_cell_set_name].cells,
                                 line=p.datums[plate.datum_z_axis_id],
                                 edges=[p.edges[i] for i in e],
                                 sense=REVERSE)

    # partition the cutting plane face
    if crack_angle == 0 or crack_angle == math.pi:
        f = p.faces.findAt(((crack_pos_x, crack_pos_y, plate.thickness * 0.5),))
        p.PartitionFaceByShortestPath(faces=f,
                                      point1=p.datums[crack_bot_start_datum_point],
                                      point2=p.datums[crack_top_start_datum_point])
        f = p.faces.findAt(((crack_pos_x, crack_pos_y, plate.thickness * 0.5),))
        p.PartitionFaceByShortestPath(faces=f,
                                      point1=p.datums[crack_bot_end_datum_point],
                                      point2=p.datums[crack_top_end_datum_point])

    f = p.faces.findAt(((crack_pos_x, crack_pos_y, plate.thickness * 0.5),))
    p.Set(faces=f, name=crack.seam_face_set_name)

    # return the coordinates of the bounding box
    return [x_left, y_lower, x_right, y_upper]


def create_transducer_as_vertex_on_plate(plate, transducer, element_size):
    """
    Creates the geometry for a point-force representation of a (piezo-electric) transducer.

    The plate area around the transducer is partitioned so that a line-intersection at the transducers location is
    generated. This ensures that a node is placed at the exact position of the piezo element during meshing.

    :param IsotropicRectangularPlate plate: Plate to which to add the transducer.
    :param CircularTransducer transducer: Transducer to add to the plate.
    :param float element_size: Desired element size (in-plane) of the mesh. Value is needed for partitioning.
    :return: Bounding box coordinates.
    :rtype: list[float, float, float, float]
    """
    # decompose piezo attributes
    piezo_pos_x = transducer.position_x
    piezo_pos_y = transducer.position_y
    piezo_radius = transducer.radius

    # constants
    boundbox_scale = 1.0

    # retrieve ABAQUS part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # partition the plate to get a rectangular bounding box around the piezo element position
    boundbox_radius = piezo_radius * boundbox_scale
    x_left, x_right, y_lower, y_upper, x_center, y_center = \
        (__get_bounding_box_coordinates_from_reference_mesh(piezo_pos_x, piezo_pos_y, boundbox_radius, element_size))

    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    __add_rectangular_cell_partition_to_plate(plate, lower_left_coord, upper_right_coord,
                                              transducer.bounding_box_cell_set_name)

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
    sketch_face = p.faces.findAt(((piezo_pos_x, piezo_pos_y, 0),),
                                 ((piezo_pos_x, piezo_pos_y, plate.thickness),) )
    p.PartitionFaceBySketchThruAll(faces=sketch_face, sketchPlane=p.datums[sketch_plane_id],
                                   sketchUpEdge=p.datums[sketch_up_edge_id], sketchPlaneSide=SIDE1, sketch=s)

    # add line intersection point at plate top surface to piezo node set
    intersection_point = p.vertices.findAt(((piezo_pos_x, piezo_pos_y, plate.thickness),))
    p.Set(name=transducer.on_plate_top_set_name, vertices=intersection_point)

    # add line intersection point at plate bottom surface to piezo node set
    intersection_point = p.vertices.findAt(((piezo_pos_x, piezo_pos_y, 0),))
    p.Set(name=transducer.on_plate_bottom_set_name, vertices=intersection_point)

    return [x_left, y_lower, x_right, y_upper]


def add_rectangular_cell_partition_to_plate(plate, lower_left_coord, upper_right_coord):
    """
    Creates a rectangular cell partition in the plate with diagonal corners lower_left_coord and upper_right_coord.

    Note that this function is similar to the (internal) function __add_rectangular_cell_partition_to_plate, but is used
    in a different context and has

    :param IsotropicRectangularPlate plate: Plate to which to add the rectangular cell partition.
    :param tuple[float, float] lower_left_coord: Lower-left coordinate (x, y) of the rectangular cell partition.
    :param tuple[float, float] upper_right_coord: Upper-right coordinate (x, y) of the rectangular cell partition.
    :return: status-flag and exception message
    :rtype: tuple[int, str]
    """
    status = 0
    warning = ""

    # retrieve ABAQUS part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # decompose tuples
    left, lower = lower_left_coord
    right, upper = upper_right_coord

    # partition the plate to get a rectangular partition that cen be meshed using structured meshing
    # draw the rectangular region
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id], sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=3.25, gridSpacing=0.08, transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.rectangle(point1=lower_left_coord, point2=upper_right_coord)

    # create a face partition from the sketch on the plates top surface
    plate_faces = p.sets[plate.top_surf_face_set_name].faces.findAt(
        (((left + right) / 2, (lower + upper) / 2, plate.thickness),))
    try:
        p.PartitionFaceBySketch(faces=plate_faces[0], sketch=s)
        del mdb.models[MODEL_NAME].sketches['__profile__']
    except Exception as e:
        warning = ("Face partition could not be created: {}. "
                   "Probably the target region is already rectangular.".format(e))
        status = 1
        return status, warning

    # get the rectangular regions face and use its edges to create a cuboid cell partition
    rectangular_face = p.sets[plate.top_surf_face_set_name].faces.getByBoundingBox(zMin=plate.thickness,
                                                                                   zMax=plate.thickness,
                                                                                   xMin=left, yMin=lower, xMax=right,
                                                                                   yMax=upper)
    e = rectangular_face[0].getEdges()
    cell_to_partition = p.sets[plate.cell_set_name].cells.findAt(
        ((left + right) / 2, (lower + upper) / 2, plate.thickness / 2), )
    try:
        p.PartitionCellByExtrudeEdge(cells=cell_to_partition, line=p.datums[plate.datum_z_axis_id],
                                     edges=[p.edges[i] for i in e], sense=REVERSE)
    except Exception as e:
        warning = ("Cell partition could not be created: {}. "
                   "Probably the target region is already rectangular.".format(e))
        status = 1
        return status, warning

    return status, warning


def __add_rectangular_cell_partition_to_plate(plate, lower_left_coord, upper_right_coord, cell_set_name):
    """
    (Helper) Creates a rectangular cell partition around a defect or piezoelectric transducer and adds it to a set.

    :param IsotropicRectangularPlate plate: Plate to which to add the rectangular cell partition.
    :param tuple[float, float] lower_left_coord: Lower-left coordinate of the rectangular cell partition.
    :param tuple[float, float] upper_right_coord: Upper-right coordinate of the rectangular cell partition.
    :param str cell_set_name: Name of the set which is created for the rectangular cell.
    :return: None
    """
    # retrieve ABAQUS part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id

    # partition the plate to create a rectangular (cuboid) cell
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
    p.Set(cells=boundbox_cell, name=cell_set_name)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[plate.cell_set_name], p.sets[cell_set_name]],
                   name=plate.cell_set_name)


def __get_bounding_box_coordinates_from_reference_mesh(x, y, bounding_box_radius, element_size):
    """
    (Helper) Returns corner- and edge-center-coordinates that snap to the nearest node of a reference mesh. Comes down
    to a closest-match search of the desired bounding box coordinates on the reference mesh.

    :param float x: X-coordinate of the center of the bounding box.
    :param float y: X-coordinate of the center of the bounding box.
    :param float bounding_box_radius: Radius (length and width) of the bounding box.
    :param float element_size: Desired element size (in-plane) of the mesh. Needed to limit the search range.

    :return: Corner- and edge-center-coordinates that snap to the nearest nodes of the reference mesh.
    :rtype: tuple[float, float, float, float, float, float]
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


# MESH MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def mesh_part(element_size_in_plane, element_size_thickness, plate, transducers, defects):
    """
    Sets the meshing algorithm for different partitions of the plate. Seeds the plate with desired through-thickness
    and in-plane element size. Sets the element type to C3D8R for the whole model. Generates the mesh.

    :param float element_size_in_plane: Desired element size (in-plane).
    :param float element_size_thickness: Desired element size (through-thickness).
    :param IsotropicRectangular plate: Plate to be meshed.
    :param list[Transducer] transducers: List of applied transducers.
    :param list[Defect] defects: List of plate defects.
    :return: Number of nodes of the generated mesh.
    :rtype: int
    """
    # set meshing algorithm for plate
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    p.setMeshControls(regions=p.sets[plate.cell_set_name].cells, technique=STRUCTURED)

    # set meshing algorithm for transducer bounding boxes
    for transducer in transducers:
        p.setMeshControls(regions=p.sets[transducer.bounding_box_cell_set_name].cells, algorithm=MEDIAL_AXIS)

    for defect in defects:
        if isinstance(defect, Crack):
            p.setMeshControls(regions=p.sets[defect.bounding_box_cell_set_name].cells, technique=SWEEP,
                              algorithm=ADVANCING_FRONT)
        else:
            p.setMeshControls(regions=p.sets[defect.bounding_box_cell_set_name].cells, technique=SWEEP,
                              algorithm=MEDIAL_AXIS)

    # seed and mesh part with desired in-plane element size
    p.seedPart(size=element_size_in_plane, deviationFactor=0.1, minSizeFactor=0.1)

    # seed all vertical edges with through-thickness element size
    vertical_edge_indices = []
    for edge in p.edges:
        vertex_indices = edge.getVertices()
        if len(vertex_indices) == 2:
            x1, y1 = p.vertices[vertex_indices[0]].pointOn[0][0:2]
            x2, y2 = p.vertices[vertex_indices[1]].pointOn[0][0:2]
            if (x2 - x1) == 0 and (y2 - y1) == 0:
                vertical_edge_indices.append(edge.index)
    if len(vertical_edge_indices) > 0:
        p.seedEdgeBySize(edges=[p.edges[i] for i in vertical_edge_indices], size=element_size_thickness)

    # set the element type for the whole model
    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT,
                              secondOrderAccuracy=OFF, distortionControl=DEFAULT)
    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=EXPLICIT)
    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=EXPLICIT)
    p.setElementType(regions=(p.cells,), elemTypes=(elemType1, elemType2, elemType3))

    # generate the mesh
    p.generateMesh()
    mesh_stats = p.getMeshStats()
    return mesh_stats.numNodes


# PROPERTY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def create_isotropic_material(material):
    """
    Creates the material in ABAQUS.

    :param IsotropicMaterial material: Material.
    :return: None
    """
    if isinstance(material, IsotropicMaterial):
        mdb.models[MODEL_NAME].Material(name=material.name)
        mdb.models[MODEL_NAME].materials[material.name].Density(table=((material.properties["density"],),))
        mdb.models[MODEL_NAME].materials[material.name].Elastic(table=((material.properties["youngs_modulus"],
                                                                        material.properties["poissons_ratio"]),))
    else:
        raise ValueError('Material is not isotropic.')


def assign_material(set_name, material):
    """
    Assigns the material to the desired set. A new homogeneous solid section will be created.

    :param str set_name: Name of the ABAQUS set that the material is assigned to.
    :param Material material: Material that is assigned to the set.
    :return: None
    """
    # create new homogenous continuum section
    section_name = set_name + '_section_homogenous_' + material.name
    mdb.models[MODEL_NAME].HomogeneousSolidSection(name=section_name, material=material.name, thickness=None)

    # create new set containing all cells and assign section to set
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    p.SectionAssignment(region=p.sets[set_name], sectionName=section_name, offset=0.0, offsetType=MIDDLE_SURFACE,
                        offsetField='', thicknessAssignment=FROM_SECTION)


# ASSEMBLY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def assemble():
    """
    Instantiates the (only) plate part in a new assembly.
    :return: None
    """
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    a = mdb.models[MODEL_NAME].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name=PLATE_PART_NAME, part=p, dependent=ON)


# STEP / LOAD MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------
def remove_all_steps():
    """
    Removes all step definitions from the model tree.
    :return: None
    """
    model = mdb.models[MODEL_NAME]
    for step_name in reversed(model.steps.keys()):
        if step_name != 'Initial':
            del model.steps[step_name]


def create_step_dynamic_explicit(step_name, previous_step_name, time_period, max_increment):
    """
    Creates a new dynamic/explicit step with desired duration and desired maximum time increment.

    :param str step_name: Name of the step to be created.
    :param str previous_step_name: Name of the step after which the current step should be created. If None, the current
    step is created after the 'Initial' step.
    :param float time_period: Step duration.
    :param float max_increment: Maximum time increment for numerical time integration scheme (central difference method)
    :return: None
    """
    # create dynamic, explicit step
    m = mdb.models[MODEL_NAME]
    m.ExplicitDynamicsStep(name=step_name,
                           previous=previous_step_name if previous_step_name is not None else 'Initial',
                           description='',
                           timePeriod=time_period,
                           maxIncrement=max_increment,
                           nlgeom=OFF)


def remove_standard_field_output_request():
    """
    Removes the standard field output request from the model tree.
    """
    # delete standard field output request
    if hasattr(mdb.models[MODEL_NAME], 'fieldOutputRequests'):
        if 'F-Output-1' in mdb.models[MODEL_NAME].fieldOutputRequests:
            del mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1']


def add_history_output_request_transducer_signals(transducers, create_step_name):
    """
    Adds history output requests for the translational DOFs of the provided list of transducers for the desired step.

    This output request causes ABAQUS to write translational nodal displacements of all transducers to the .ODB file
    for every EXPLICIT increment.

    :param list[Transducer] transducers: List of transducers for which to request history output.
    :param str create_step_name: Name of the step in which to create the history output request.
    :return: None
    """
    for i, transducer in enumerate(transducers):
        a = mdb.models[MODEL_NAME].rootAssembly
        for set_name, description in zip([transducer.on_plate_top_set_name, transducer.on_plate_bottom_set_name],
                                         ['top', 'bottom']):
            region_def = a.instances[PLATE_PART_NAME].sets[set_name]
            mdb.models[MODEL_NAME].HistoryOutputRequest(name='history_transducer_{}_{}'.format(i+1, description),
                                                        createStepName=create_step_name,
                                                        variables=('U1', 'U2', 'U3'),
                                                        frequency=1,
                                                        region=region_def,
                                                        sectionPoints=DEFAULT,
                                                        rebar=EXCLUDE)


def add_field_output_request_plate_surface(plate, create_step_name, time_interval):
    """
    Adds a field output request for the translational DOFs of all nodes on the plates' surface for the desired step.

    This output request causes ABAQUS to write translational nodal displacements of all nodes on the plate surface
    to the .ODB file in fixed time intervals.

    :param IsotropicRectangular plate: Plate instance.
    :param str create_step_name: Name of the step in which to create the history output request.
    :param float time_interval: Time interval in which output should be written.
    :return: None
    """
    region = mdb.models[MODEL_NAME].rootAssembly.allInstances[PLATE_PART_NAME].sets[plate.field_output_face_set_name]
    mdb.models[MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
                                              createStepName=create_step_name, variables=('UT',),
                                              timeInterval=time_interval, region=region, sectionPoints=DEFAULT)


def __add_amplitude(name, signal, max_time_increment):
    """
    (Helper) Adds an amplitude to the model tree as tabular data, sampled from the provided signal definition.

    :param str name: Name of the amplitude.
    :param Signal signal: Signal to be added as an amplitude.
    :param float max_time_increment: Maximum time increment of the time integration scheme. Needed to ensure that the
    amplitude data is written with sufficient sampling frequency.
    :return: None
    """
    # generate time data
    if isinstance(signal, DiracImpulse):
        # impulses are handled differently than other signals to ensure that the impulse is only
        # nonzero for the very first ABAQUS/Explicit increment
        time_data_table = [(0, signal.magnitude), (max_time_increment * 1e-2, 0)]
    else:
        # all other signals besides impulses can be sampled from the signal definition in their method 'get_value_at'
        time_data_table = []
        for t in np.arange(start=signal.delta_t, stop=signal.delta_t + signal.get_duration() * 1.01,
                           step=max_time_increment / 2):
            time_data_table.append((t, signal.get_value_at(t=t)))

    # create amplitude in ABAQUS
    mdb.models[MODEL_NAME].TabularAmplitude(name=name, timeSpan=STEP, smooth=SOLVER_DEFAULT,
                                            data=tuple(time_data_table))


def add_transducer_concentrated_force(step_name, transducer, signal, max_time_increment):
    """
    Creates loads (concentrated forces) at the transducers' location, depending on whether the transducer is in top,
    bottom, symmetric or asymmetric excitation mode. The magnitude of the load is linked to the supplied signal
    definition.

    :param str step_name: Name of the step in which to create the load.
    :param CircularTransducer transducer: Transducer for which to add the load.
    :param Signal signal: Signal that drives the load amplitude.
    :param float max_time_increment: Maximum time increment of the time integration scheme. Needed to ensure that the
    amplitude data is written with sufficient sampling frequency.
    :return: None
    """

    amplitude_name = 'transducer_{}_{}'.format(transducer.name, signal.__class__.__name__)
    __add_amplitude(amplitude_name, signal, max_time_increment)

    set_names, concentrated_force_z_amplitudes = (None, None)
    if transducer.position_z == 'top':
        set_names = [transducer.on_plate_top_set_name]
        concentrated_force_z_amplitudes = [1.0]
    if transducer.position_z == 'bottom':
        set_names = [transducer.on_plate_bottom_set_name]
        concentrated_force_z_amplitudes = [-1.0]
    if transducer.position_z == 'symmetric':
        set_names = [transducer.on_plate_top_set_name, transducer.on_plate_bottom_set_name]
        concentrated_force_z_amplitudes = [1.0, -1.0]
    if transducer.position_z == 'asymmetric':
        set_names = [transducer.on_plate_top_set_name, transducer.on_plate_bottom_set_name]
        concentrated_force_z_amplitudes = [1.0, 1.0]

    for set_name, concentrated_force_z_amplitude in zip(set_names, concentrated_force_z_amplitudes):
        region = mdb.models[MODEL_NAME].rootAssembly.instances[PLATE_PART_NAME].sets[set_name]
        load_name = '{}_{}'.format(set_name, signal.__class__.__name__)
        mdb.models[MODEL_NAME].ConcentratedForce(name=load_name, createStepName=step_name, region=region,
                                                 cf3=concentrated_force_z_amplitude,
                                                 amplitude=amplitude_name, distributionType=UNIFORM,
                                                 field='', localCsys=None)


def write_input_file(job_name, output_directory):
    """
    Writes an input (.INP) file for the current model tree. The .INP file is written to the specified output directory.

    :param str job_name: Name of the ABAQUS job and .INP file.
    :param str output_directory: Name of the directory to which to write the output to (is created if it doesn't exist).
    :return: None
    """
    original_directory = os.getcwd()
    os.mkdir(output_directory)
    os.chdir(output_directory)
    mdb.Job(name=job_name, model=MODEL_NAME, description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB)
    mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
    os.chdir(original_directory)


# INTERACTION MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------
def assign_seam(crack):
    """
    Assigns a seam to the crack to achieve node separation between the opposing crack edges.
    :param Crack crack: Crack for which to assign the seam.
    :return: None
    """
    a = mdb.models[MODEL_NAME].rootAssembly
    i = a.instances[PLATE_PART_NAME]
    a.makeIndependent(instances=(i,))
    picked_region = i.sets[crack.seam_face_set_name]        #.faces[:]
    mdb.models[MODEL_NAME].rootAssembly.engineeringFeatures.assignSeam(regions=picked_region)

