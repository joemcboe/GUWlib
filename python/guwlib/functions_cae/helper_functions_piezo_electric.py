# -*- coding: mbcs -*-
"""
Bottom-level helper-functions to automate specific modelling tasks in ABAQUS/CAE using ABAQUS scripting interface. Note
that these functions are only available from the ABAQUS python interpreter. These helper functions are made for the
``'piezo_electric'`` model approach.

THESE FUNCTIONS ARE UNDOCUMENTED AND NOT PROPERLY INTEGRATED. LAST COMMIT WHERE THESE FUNCTIONS WERE TESTED WAS NOV 15
2023. DO NOT IMPORT THIS MODULE!
"""
from math import sqrt

# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import load_case
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

import numpy as np
import datetime

from .materials import *
from .output import *
from .signals import *

PLATE_PART_NAME = 'plate'
MODEL_NAME = 'Model-1'
STD_MODEL_NAME = 'Model-1-STD'  # the model for Abaqus Standard simulation
XPL_MODEL_NAME = 'Model-1-XPL'  # the model for Abaqus Explicit simulation
INSTANCE_NAME = PLATE_PART_NAME
STEP_NAME = 'lamb_excitation'

PLATE_MESH_PART_NAME = 'XPL_mesh'
PIEZO_MESH_PART_NAME = 'STD_mesh'

# bounding box scale
BOUNDBOX_SCALE = 1.5

# todo: better names
PLATE_CELL_NAME = 'plate'
PLATE_TOP_FACE_NAME = 'plate-top-surface'
PLATE_SET_NAME = 'plate-material'

PIEZO_CELL_NAME = 'transducer'
DEFECT_CELL_NAME = 'defect'
BOUNDBOX_CELL_NAME = 'bounding_box'


# PART MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def create_piezo_element(plate, piezo_element):
    # decompose piezo attributes
    piezo_pos_x = piezo_element.position_x
    piezo_pos_y = piezo_element.position_y
    piezo_radius = piezo_element.radius
    piezo_thickness = piezo_element.thickness
    piezo_id = piezo_element.id
    electrode_thickness = piezo_element.electrode_thickness

    # constants and set names
    boundbox_scale = 1.5
    boundbox_cell_set_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, piezo_id, BOUNDBOX_CELL_NAME)
    piezo_cell_set_name = '{}_{}'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_material_cell_set_name = '{}_piezo_material'.format(piezo_cell_set_name)
    electrode_material_cell_set_name = '{}_electrode_material'.format(piezo_cell_set_name)
    piezo_top_surf_set_name = "{}_top_surf".format(piezo_cell_set_name)
    piezo_bot_surf_set_name = "{}_bot_surf".format(piezo_cell_set_name)
    piezo_interface_surf_set_name = "{}_int_surf".format(piezo_cell_set_name)

    # create solid extrusion
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_xy_plane_id
    sketch_up_edge_id = plate.datum_y_axis_id
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.CircleByCenterPerimeter(center=(piezo_pos_x, piezo_pos_y),
                              point1=(piezo_pos_x + piezo_radius, piezo_pos_y))
    p.SolidExtrude(sketchPlane=p.datums[sketch_plane_id],
                   sketchUpEdge=p.datums[sketch_up_edge_id],
                   sketchPlaneSide=SIDE1,
                   sketchOrientation=RIGHT,
                   sketch=s,
                   depth=piezo_thickness + electrode_thickness,
                   flipExtrudeDirection=OFF)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # partition the part into two cells (transducer and plate)
    p.PartitionCellByDatumPlane(cells=p.sets[PLATE_CELL_NAME].cells[0:1], datumPlane=p.datums[sketch_plane_id])
    p.Set(cells=p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=plate.thickness),
          faces=p.sets[PLATE_CELL_NAME].faces.getByBoundingBox(zMin=plate.thickness), name=piezo_cell_set_name)
    p.Set(cells=p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMax=plate.thickness), name=PLATE_CELL_NAME)

    # partition the transducer into two cells (piezoelectric and electrode)
    offset = plate.thickness + electrode_thickness
    partition_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=offset).id
    p.PartitionCellByDatumPlane(cells=p.sets[piezo_cell_set_name].cells[0:1], datumPlane=p.datums[partition_plane_id])
    p.Set(cells=p.sets[piezo_cell_set_name].cells.getByBoundingBox(zMin=offset), name=piezo_material_cell_set_name)
    p.Set(cells=p.sets[piezo_cell_set_name].cells.getByBoundingBox(zMax=offset), name=electrode_material_cell_set_name)

    # partition the plate to get a rectangular bounding box around the piezo element
    lower_left_coord = (piezo_pos_x - boundbox_scale * piezo_radius, piezo_pos_y - boundbox_scale * piezo_radius)
    upper_right_coord = (piezo_pos_x + boundbox_scale * piezo_radius, piezo_pos_y + boundbox_scale * piezo_radius)
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.rectangle(point1=lower_left_coord, point2=upper_right_coord)
    plate_faces = p.sets[PLATE_TOP_FACE_NAME].faces[0]
    f = p.PartitionFaceBySketch(faces=plate_faces,
                                sketch=s)
    e = p.sets[PLATE_TOP_FACE_NAME].faces[1].getEdges()
    line_id = p.DatumAxisByTwoPoint(point1=(0, 0, 0), point2=(0, 0, plate.thickness)).id
    p.PartitionCellByExtrudeEdge(cells=p.sets[PLATE_CELL_NAME].cells[0:1],
                                 line=p.datums[line_id],
                                 edges=[p.edges[i] for i in e[0:4]],
                                 sense=REVERSE)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # update sets for plate top surface, bounding box, plate, and plate cell
    p.Set(faces=p.sets[PLATE_TOP_FACE_NAME].faces[0:1], name=PLATE_TOP_FACE_NAME)
    boundbox_cell = p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=0,
                                                                   zMax=plate.thickness,
                                                                   xMin=lower_left_coord[0],
                                                                   yMin=lower_left_coord[1],
                                                                   xMax=upper_right_coord[0],
                                                                   yMax=upper_right_coord[1])
    p.Set(cells=boundbox_cell, name=boundbox_cell_set_name)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[PLATE_CELL_NAME], p.sets[boundbox_cell_set_name]],
                   name=PLATE_CELL_NAME)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[PLATE_SET_NAME], p.sets[piezo_cell_set_name]],
                   name=PLATE_SET_NAME)

    # generate guidelines for better mesh quality
    temp_sketch_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                        offset=plate.thickness + piezo_thickness + electrode_thickness).id
    t = p.MakeSketchTransform(sketchPlane=p.datums[temp_sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)

    guideline_coordinates = get_guidelines(piezo_pos_x, piezo_pos_y, piezo_radius)
    for coordinates in guideline_coordinates:
        s.Line(point1=coordinates[0], point2=coordinates[1])

    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)

    face_array = p.faces.findAt(
        ((piezo_pos_x + piezo_radius * (1 + boundbox_scale) / 2, piezo_pos_y, plate.thickness),),  # plate bbox
        ((piezo_pos_x + piezo_radius, piezo_pos_y, plate.thickness + 0.5 * electrode_thickness),),
        ((piezo_pos_x + piezo_radius, piezo_pos_y, plate.thickness + electrode_thickness + 0.5 * piezo_thickness),),
        ((piezo_pos_x, piezo_pos_y, plate.thickness + piezo_thickness + electrode_thickness),)
    )

    p.PartitionFaceBySketchThruAll(
        faces=face_array,
        sketchPlane=p.datums[temp_sketch_plane_id],
        sketchUpEdge=p.datums[sketch_up_edge_id],
        sketchPlaneSide=SIDE1,
        sketch=s)

    # define piezo top and bottom surfaces and interface surface - assumes plate is not subdivided in height direction
    help_points_z = [plate.thickness - 0.5 * plate.thickness,
                     plate.thickness + 0.5 * electrode_thickness,
                     plate.thickness + electrode_thickness + 0.5 * piezo_thickness,
                     plate.thickness + electrode_thickness + 1.5 * piezo_thickness]
    help_radius = 0.5 * (1 + boundbox_scale) * piezo_radius
    points = [(piezo_pos_x, piezo_pos_y, help_points_z[0]),
              (piezo_pos_x, piezo_pos_y, help_points_z[1]),
              (piezo_pos_x, piezo_pos_y, help_points_z[2]),
              (piezo_pos_x, piezo_pos_y, help_points_z[3])]
    int_faces = p.faces.getByBoundingCylinder(center1=points[0], center2=points[1], radius=help_radius)
    bot_faces = p.faces.getByBoundingCylinder(center1=points[1], center2=points[2], radius=help_radius)
    top_faces = p.faces.getByBoundingCylinder(center1=points[2], center2=points[3], radius=help_radius)

    # create sets from face arrays
    p.Set(name=piezo_top_surf_set_name, faces=top_faces)
    p.Set(name=piezo_bot_surf_set_name, faces=bot_faces)
    p.Set(name=piezo_interface_surf_set_name, faces=int_faces)

    # link set names to piezo element
    piezo_element.cell_set_name = piezo_cell_set_name
    piezo_element.bounding_box_set_name = boundbox_cell_set_name
    piezo_element.piezo_material_cell_set_name = piezo_material_cell_set_name
    piezo_element.electrode_material_cell_set_name = electrode_material_cell_set_name
    piezo_element.piezo_top_surf_set_name = piezo_top_surf_set_name
    piezo_element.piezo_bot_surf_set_name = piezo_bot_surf_set_name
    piezo_element.interface_surf_set_name = piezo_interface_surf_set_name


def get_guidelines(x, y, radius):
    a = 1.3
    b = 0.7
    x_seq = np.array([-1, -1, -1, 0, 1, 1, 1, 0])
    y_seq = np.array([-1, 0, 1, 1, 1, 0, -1, -1])
    mask_x = np.array([1, a, 1, 1, 1, a, 1, 1])
    mask_y = np.array([1, 1, 1, a, 1, 1, 1, a])

    c = 1 / (sqrt(2) * BOUNDBOX_SCALE)
    temp = np.array([c, 1, c, 1, c, 1, c, 1])

    x_outer = x_seq * radius * BOUNDBOX_SCALE * temp + x
    y_outer = y_seq * radius * BOUNDBOX_SCALE * temp + y
    x_inner = x_seq * b * (1 / np.sqrt(2)) * radius * mask_x + x
    y_inner = y_seq * b * (1 / np.sqrt(2)) * radius * mask_y + y

    point_sequence = []
    for i in range(len(x_seq)):
        point_sequence.append([(x_outer[i], y_outer[i]), (x_inner[i], y_inner[i])])
        point_sequence.append([(x_inner[i - 1], y_inner[i - 1]), (x_inner[i], y_inner[i])])

    return point_sequence


# PROPERTY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def create_materials_co_sim(plate, phased_array):
    # create material for plate
    create_material_co_sim(plate.material, XPL_MODEL_NAME)
    log_info("Material ({}) created.".format(plate.material))

    # create all materials needed for piezo
    piezo_materials = set()
    for piezo in phased_array:
        piezo_materials.add(piezo.material)
        piezo_materials.add(piezo.electrode_material)
    for material in piezo_materials:
        create_material_co_sim(material, STD_MODEL_NAME)
        log_info("Material ({}) created.".format(material))


def create_material_co_sim(material_name, model_name):
    # todo: potential duplicate
    try:
        material_properties = get_material_properties(material_name)

        type_of_material = material_properties["type"]
        if type_of_material == "isotropic":
            mdb.models[model_name].Material(name=material_name)
            m = mdb.models[model_name].materials[material_name]
            m.Density(table=((material_properties["density"],),))
            m.Elastic(table=((material_properties["youngs_modulus"], material_properties["poissons_ratio"]),))

        if type_of_material == "piezo_electric":
            mdb.models[model_name].Material(name=material_name)
            m = mdb.models[model_name].materials[material_name]
            m.Density(table=((material_properties["density"],),))
            m.Elastic(type=ENGINEERING_CONSTANTS, table=material_properties["elastic_engineering_constants_table"])
            m.Dielectric(type=ORTHOTROPIC, table=material_properties["dielectric_orthotropic_table"])
            m.Piezoelectric(type=STRAIN, table=material_properties["piezo_electric_strain_table"])
    except ValueError as e:
        log_error(e)


def assign_material_co_sim(plate, phased_array):
    # assign plate material
    _assign_material(XPL_MODEL_NAME, PLATE_MESH_PART_NAME, plate.material_cell_set_name, plate.material)

    # assign piezo materials
    for piezo in phased_array:
        _assign_material(STD_MODEL_NAME, PIEZO_MESH_PART_NAME,
                         piezo.piezo_material_cell_set_name, piezo.material)
        _assign_material(STD_MODEL_NAME, PIEZO_MESH_PART_NAME,
                         piezo.electrode_material_cell_set_name, piezo.electrode_material)
        _add_orientation(STD_MODEL_NAME, PIEZO_MESH_PART_NAME, piezo.piezo_material_cell_set_name)


def _add_orientation(model_name, part_name, set_name):
    p = mdb.models[model_name].parts[part_name]
    region = p.sets[set_name]
    p.MaterialOrientation(region=region, orientationType=GLOBAL, axis=AXIS_1, additionalRotationType=ROTATION_NONE,
                          localCsys=None, fieldName='', stackDirection=STACK_3)


def _assign_material(model_name, part_name, set_name, material):
    # todo: potential duplicate
    # create new homogenous section
    section_name = set_name + '_section_homogenous_' + material
    mdb.models[model_name].HomogeneousSolidSection(
        name=section_name,
        material=material,
        thickness=None)

    # create new set containing all cells and assign section to set
    p = mdb.models[model_name].parts[part_name]
    p.SectionAssignment(region=p.sets[set_name],
                        sectionName=section_name,
                        offset=0.0,
                        offsetType=MIDDLE_SURFACE,
                        offsetField='',
                        thicknessAssignment=FROM_SECTION)


# MESH MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def mesh_part_piezo_electric_approach(element_size, phased_array, defects):
    # helper variables
    element_type_1 = mesh.ElemType(elemCode=C3D8E, elemLibrary=STANDARD)
    element_type_2 = mesh.ElemType(elemCode=C3D6E, elemLibrary=STANDARD)
    element_type_3 = mesh.ElemType(elemCode=C3D4E, elemLibrary=STANDARD)
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]

    # set meshing algorithm for plate cell
    p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)

    # piezo elements
    for i, piezo in enumerate(phased_array):
        boundbox_cell_name = piezo.bounding_box_set_name
        piezo_cell_name = piezo.cell_set_name
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=ADVANCING_FRONT)
        p.setMeshControls(regions=p.sets[piezo_cell_name].cells, algorithm=ADVANCING_FRONT)

        # set element type of piezoelectric material
        piezo_material_cell_set = phased_array[i].piezo_material_cell_set_name
        p.setElementType(regions=(p.sets[piezo_material_cell_set].cells,),
                         elemTypes=(element_type_1, element_type_2, element_type_3))

    for i in range(len(defects)):
        boundbox_cell_name = '{}_{}_{}'.format(DEFECT_CELL_NAME, i, BOUNDBOX_CELL_NAME)
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=ADVANCING_FRONT)

    # seed and mesh part with desired element size
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

    mesh_stats = p.getMeshStats()
    num_nodes = mesh_stats.numNodes

    log_info("The FE model has {} nodes.".format(num_nodes))
    return num_nodes


def create_mesh_parts():
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]

    # create orphan mesh part (serves as basis for the plate mesh)
    p.PartFromMesh(name=PLATE_MESH_PART_NAME, copySets=True)

    # copy the orphan mesh part (serves as basis for the piezo transducers mesh)
    mdb.models[MODEL_NAME].Part(name=PIEZO_MESH_PART_NAME,
                                objectToCopy=mdb.models[MODEL_NAME].parts[PLATE_MESH_PART_NAME])

    # remove the original part
    del mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]


def split_mesh_parts(plate, phased_array):
    # part handles
    p_plate = mdb.models[MODEL_NAME].parts[PLATE_MESH_PART_NAME]
    p_piezo = mdb.models[MODEL_NAME].parts[PIEZO_MESH_PART_NAME]

    # clean up the plate mesh (delete all elements associated with the transducers, delete invalidated sets)
    for piezo in phased_array:
        del_set_name = piezo.cell_set_name
        p_plate.deleteElement(elements=p_plate.sets[del_set_name], deleteUnreferencedNodes=ON)
        for set_name in [piezo.bounding_box_set_name, piezo.piezo_material_cell_set_name,
                         piezo.electrode_material_cell_set_name, piezo.piezo_top_surf_set_name,
                         piezo.piezo_bot_surf_set_name, piezo.interface_surf_set_name]:
            del p_plate.sets[set_name]

    # clean up the piezo mesh (delete all elements associated with the plate, delete invalidated sets)
    del_set_name = plate.material_cell_set_name
    p_piezo.deleteElement(elements=p_piezo.sets[del_set_name], deleteUnreferencedNodes=ON)
    del p_piezo.sets[plate.cell_set_name]
    del p_piezo.sets[plate.material_cell_set_name]
    del p_piezo.sets[plate.top_surf_face_set_name]
    for piezo in phased_array:
        del p_piezo.sets[piezo.bounding_box_set_name]

    # create additional node sets for interface definition
    plate.std_interface_node_set_name = 'STD_interface_nodes'
    plate.xpl_interface_node_set_name = 'XPL_interface_nodes'
    p_piezo.SetByBoolean(operation=UNION,
                         sets=[p_piezo.sets[piezo.interface_surf_set_name] for piezo in phased_array],
                         name=plate.std_interface_node_set_name)
    p_piezo.Set(name=plate.std_interface_node_set_name, nodes=p_piezo.sets[plate.std_interface_node_set_name].nodes)
    p_plate.SetByBoolean(operation=UNION,
                         sets=[p_plate.sets[piezo.cell_set_name] for piezo in phased_array],
                         name=plate.xpl_interface_node_set_name)


def create_electric_interface(phased_array):
    p_piezo = mdb.models[MODEL_NAME].parts[PIEZO_MESH_PART_NAME]
    # create main nodes and slave nodes
    for i, piezo in enumerate(phased_array):
        piezo.signal_main_node_set_name = "{}_{}_SIGNAL".format(PIEZO_CELL_NAME, i)
        piezo.signal_slave_node_set_name = "{}_{}_SIGNAL_slave".format(PIEZO_CELL_NAME, i)
        piezo.gnd_main_node_set_name = "{}_{}_GND".format(PIEZO_CELL_NAME, i)
        piezo.gnd_slave_node_set_name = "{}_{}_GND_slave".format(PIEZO_CELL_NAME, i)

        p_piezo.Set(name=piezo.signal_main_node_set_name, nodes=p_piezo.sets[piezo.piezo_top_surf_set_name].nodes[0:1])
        p_piezo.Set(name=piezo.signal_slave_node_set_name, nodes=p_piezo.sets[piezo.piezo_top_surf_set_name].nodes[1:])
        p_piezo.Set(name=piezo.gnd_main_node_set_name, nodes=p_piezo.sets[piezo.piezo_bot_surf_set_name].nodes[0:1])
        p_piezo.Set(name=piezo.gnd_slave_node_set_name, nodes=p_piezo.sets[piezo.piezo_bot_surf_set_name].nodes[1:])

    # equality constraint


# ASSEMBLY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def assemble_co_sim():
    a = mdb.models[MODEL_NAME].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)

    # instantiate plate (Abaqus/Explicit part of the model)
    p = mdb.models[MODEL_NAME].parts[PLATE_MESH_PART_NAME]
    a.Instance(name=PLATE_MESH_PART_NAME,
               part=p,
               dependent=ON)

    # instantiate piezoelectric transducers (Abaqus/Standard part of the model)
    p = mdb.models[MODEL_NAME].parts[PIEZO_MESH_PART_NAME]
    a.Instance(name=PIEZO_MESH_PART_NAME,
               part=p,
               dependent=ON)


def setup_electric_interface(phased_array):
    for i, piezo in enumerate(phased_array):
        mdb.models[STD_MODEL_NAME].Equation(name='eqn-piezo-{}-top'.format(i),
                                            terms=((1.0, '{}.{}'.format(PIEZO_MESH_PART_NAME,
                                                                        piezo.signal_slave_node_set_name), 9),
                                                   (-1.0, '{}.{}'.format(PIEZO_MESH_PART_NAME,
                                                                         piezo.signal_main_node_set_name), 9)))
        mdb.models[STD_MODEL_NAME].Equation(name='eqn-piezo-{}-bot'.format(i),
                                            terms=((1.0, '{}.{}'.format(PIEZO_MESH_PART_NAME,
                                                                        piezo.gnd_slave_node_set_name), 9),
                                                   (-1.0, '{}.{}'.format(PIEZO_MESH_PART_NAME,
                                                                         piezo.gnd_main_node_set_name), 9)))


def split_model_for_co_sim():
    mdb.Model(name=STD_MODEL_NAME, objectToCopy=mdb.models[MODEL_NAME])
    mdb.models.changeKey(fromName=MODEL_NAME, toName=XPL_MODEL_NAME)

    # link the plate mesh in std model to plate mesh in xpl model
    mdb.models[STD_MODEL_NAME].linkInstances(instancesMap=((PLATE_MESH_PART_NAME,
                                                            mdb.models[XPL_MODEL_NAME].rootAssembly.instances[
                                                                PLATE_MESH_PART_NAME]),))

    # exclude the plate mesh from the std model
    a = mdb.models[STD_MODEL_NAME].rootAssembly
    a.excludeFromSimulation(instances=(a.instances[PLATE_MESH_PART_NAME],), exclude=True)

    # link the piezo mesh in xpl model to piezo mesh in std model
    mdb.models[XPL_MODEL_NAME].linkInstances(instancesMap=((PIEZO_MESH_PART_NAME,
                                                            mdb.models[STD_MODEL_NAME].rootAssembly.instances[
                                                                PIEZO_MESH_PART_NAME]),))

    # exclude the piezo mesh from the xpl model
    a = mdb.models[XPL_MODEL_NAME].rootAssembly
    a.excludeFromSimulation(instances=(a.instances[PIEZO_MESH_PART_NAME],), exclude=True)


# STEP / LOAD MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------

def remove_all_steps_co_sim():
    for model_name in [STD_MODEL_NAME, XPL_MODEL_NAME]:
        model = mdb.models[model_name]
        for step_name in reversed(model.steps.keys()):
            if step_name != 'Initial':
                del model.steps[step_name]


def create_steps_co_sim(step_name, time_period, max_increment, previous_step_name):
    m = mdb.models[XPL_MODEL_NAME]
    m.ExplicitDynamicsStep(name=step_name,
                           previous=previous_step_name if previous_step_name is not None else 'Initial',
                           description='',
                           timePeriod=time_period,
                           maxIncrement=max_increment,
                           nlgeom=OFF)

    m = mdb.models[STD_MODEL_NAME]
    m.ImplicitDynamicsStep(name=step_name,
                           previous=previous_step_name if previous_step_name is not None else 'Initial',
                           timePeriod=time_period,
                           maxNumInc=int(1e6),
                           initialInc=max_increment,
                           minInc=max_increment * 1e-2)  # minInc > dirac step time


def remove_standard_field_output_request_co_sim():
    # delete standard field output request
    for model_name in [STD_MODEL_NAME, XPL_MODEL_NAME]:
        if hasattr(mdb.models[model_name], 'fieldOutputRequests'):
            if 'F-Output-1' in mdb.models[model_name].fieldOutputRequests:
                del mdb.models[model_name].fieldOutputRequests['F-Output-1']


def add_amplitude(name, signal, max_time_increment):
    # this is a copy of add_amplitude, only model name is changed to STD_MODEL_NAME
    # generate time data
    if isinstance(signal, DiracImpulse):
        # impulses are handled differently than other signals to ensure that the impulse is only
        # nonzero for the very first Abaqus/Explicit increment
        time_data_table = [(0, signal.magnitude), (max_time_increment * 1e-2, 0)]
    else:
        # all other signals besides impulses can be sampled from the signal definition in their method 'get_value_at'
        time_data_table = []
        for t in np.arange(start=signal.dt, stop=signal.dt + signal.get_duration() * 1.01, step=max_time_increment / 2):
            time_data_table.append((t, signal.get_value_at(t=t)))

    # create amplitude in Abaqus
    mdb.models[STD_MODEL_NAME].TabularAmplitude(name=name,
                                                timeSpan=STEP,
                                                smooth=SOLVER_DEFAULT,
                                                data=tuple(time_data_table))


def add_piezo_boundary_conditions_co_sim(step_name, phased_array):
    a = mdb.models[STD_MODEL_NAME].rootAssembly
    for piezo in phased_array:
        region = a.instances[PIEZO_MESH_PART_NAME].sets[piezo.gnd_main_node_set_name]
        mdb.models[STD_MODEL_NAME].ElectricPotentialBC(name='gnd_{}'.format(piezo.cell_set_name),
                                                       createStepName=step_name, region=region,
                                                       fixed=OFF,
                                                       distributionType=UNIFORM, fieldName='', magnitude=0.0,
                                                       amplitude=UNSET)


def add_piezo_potential_co_sim(load_name, step_name, piezo, signal, max_time_increment):
    add_amplitude(load_name, signal, max_time_increment)
    a = mdb.models[STD_MODEL_NAME].rootAssembly
    region = a.instances[PIEZO_MESH_PART_NAME].sets[piezo.signal_main_node_set_name]
    mdb.models[STD_MODEL_NAME].ElectricPotentialBC(name=load_name,
                                                   createStepName=step_name, region=region, fixed=OFF,
                                                   distributionType=UNIFORM, fieldName='', magnitude=1.0,
                                                   amplitude=load_name)


def add_piezo_signal_history_output_request_co_sim(phased_array, create_step_name):
    for i, piezo in enumerate(phased_array):
        a = mdb.models[STD_MODEL_NAME].rootAssembly
        region_def = a.allInstances[PIEZO_MESH_PART_NAME].sets[piezo.signal_main_node_set_name]
        mdb.models[STD_MODEL_NAME].HistoryOutputRequest(name='piezo_{}_out'.format(i),
                                                        createStepName=create_step_name,
                                                        variables=('EPOT',),
                                                        frequency=1,
                                                        region=region_def,
                                                        sectionPoints=DEFAULT,
                                                        rebar=EXCLUDE)


def add_field_output_request_co_sim(create_step_name):
    mdb.models[XPL_MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
                                                  createStepName=create_step_name, variables=('U',),
                                                  timeInterval=EVERY_TIME_INCREMENT, position=NODES)
    mdb.models[STD_MODEL_NAME].FieldOutputRequest(name='full_field_{}'.format(create_step_name),
                                                  createStepName=create_step_name, variables=('U',),
                                                  frequency=1)


# INTERACTION MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------
def create_interaction_std_xpl_co_sim(plate, step_name):
    # setup co-sim interaction for xpl model
    a = mdb.models[XPL_MODEL_NAME].rootAssembly
    region = a.instances[PLATE_MESH_PART_NAME].sets[plate.xpl_interface_node_set_name]
    mdb.models[XPL_MODEL_NAME].StdXplCosimulation(name='Co-Sim-Int-1',
                                                  createStepName=step_name, region=region, incrementation=LOCKSTEP,
                                                  stepSizeDefinition=DEFAULT, stepSize=0.0)

    # setup co-sim interaction for std model
    a = mdb.models[STD_MODEL_NAME].rootAssembly
    region = a.instances[PIEZO_MESH_PART_NAME].sets[plate.std_interface_node_set_name]
    mdb.models[STD_MODEL_NAME].StdXplCosimulation(name='Co-Sim-Int-1',
                                                  createStepName=step_name, region=region, incrementation=LOCKSTEP,
                                                  stepSizeDefinition=DEFAULT, stepSize=0.0)