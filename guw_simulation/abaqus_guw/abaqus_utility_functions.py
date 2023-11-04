# -*- coding: mbcs -*-
"""
This module provides utility functions for the classes fe_model, phased_array and plate to create and modify geometry
and to perform meshing in Abaqus/CAE using its python interpreter (Abaqus Scripting Interface).

Author: j.froboese(at)tu-braunschweig.de
Created on: September 20, 2023
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
import step
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

import numpy as np
import datetime

from .materials import get_material_properties
from .output import *
import time

PART_NAME = 'plate'
MODEL_NAME = 'Model-1'
INSTANCE_NAME = PART_NAME
STEP_NAME = 'lamb_excitation'

# these are all sets and should maybe be named as such ...
PLATE_CELL_NAME = 'plate'
PLATE_TOP_FACE_NAME = 'plate-top-surface'
PLATE_SET_NAME = 'plate-material'

PIEZO_CELL_NAME = 'piezo'
HOLE_CELL_NAME = 'hole'
BOUNDBOX_CELL_NAME = 'bounding_box'


# PART MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def create_plate(plate):
    # create an extrusion from two-dimensional shape
    s1 = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    for i in range(len(plate.shape) - 1):
        s1.Line(point1=plate.shape[i], point2=plate.shape[i + 1])

    # s1.rectangle(point1=(0.0, 0.0), point2=(plate.width, plate.length))
    p = mdb.models[MODEL_NAME].Part(name=PART_NAME, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s1, depth=plate.thickness)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # define datum plane and store abaqus id
    plate.datum_plane_abaqus_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                               offset=plate.thickness).id

    # define datum axis and store abaqus id
    plate.datum_axis_abaqus_id = p.DatumAxisByTwoPoint(point1=(0, 0, plate.thickness),
                                                       point2=(0, 1, plate.thickness)).id
    session.viewports['Viewport: 1'].setValues(displayedObject=p)

    # store plate cell in set
    plate.set_name = PLATE_SET_NAME
    p.Set(cells=p.cells, name=PLATE_CELL_NAME)  # contains the plate without the bounding boxes
    p.Set(cells=p.cells, faces=p.faces, name=PLATE_SET_NAME)  # contains the whole plate (for material assignment)
    p.Set(faces=p.faces.getByBoundingBox(zMin=plate.thickness / 2), name=PLATE_TOP_FACE_NAME)


def create_circular_hole_in_plate(plate, hole):
    # decompose hole attributes
    circle_pos_x = hole.position_x
    circle_pos_y = hole.position_y
    circle_radius = hole.radius
    circle_id = hole.id
    guideline_option = hole.guideline_option

    # constants
    boundbox_scale = 2.5
    boundbox_cell_name = '{}_{}_{}'.format(HOLE_CELL_NAME, circle_id, BOUNDBOX_CELL_NAME)

    # add sketch of circle and cut through all
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    sketch_plane_id = plate.datum_plane_abaqus_id
    sketch_up_edge_id = plate.datum_axis_abaqus_id
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
    s.CircleByCenterPerimeter(center=(circle_pos_x, circle_pos_y),
                              point1=(circle_pos_x + circle_radius, circle_pos_y))
    p.CutExtrude(sketchPlane=p.datums[sketch_plane_id],
                 sketchUpEdge=p.datums[sketch_up_edge_id],
                 sketchPlaneSide=SIDE1,
                 sketchOrientation=RIGHT,
                 sketch=s,
                 flipExtrudeDirection=OFF)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # helper coordinates
    x_left = circle_pos_x - boundbox_scale * circle_radius
    x_right = circle_pos_x + boundbox_scale * circle_radius
    y_lower = circle_pos_y - boundbox_scale * circle_radius
    y_upper = circle_pos_y + boundbox_scale * circle_radius
    x_click = circle_pos_x - 0.5 * boundbox_scale * circle_radius
    y_click = circle_pos_y + 0.5 * boundbox_scale * circle_radius

    # partition the plate to get a rectangular bounding box around the hole
    lower_left_coord = (x_left, y_lower)
    upper_right_coord = (x_right, y_upper)
    _add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, boundbox_cell_name)

    # partition face inside bounding box to achieve better mesh quality
    if guideline_option == 'none':
        pass
    else:
        t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
                                  sketchUpEdge=p.datums[sketch_up_edge_id],
                                  sketchPlaneSide=SIDE1,
                                  origin=(0.0, 0.0, 0))
        s1 = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                      sheetSize=1.84,
                                                      gridSpacing=0.04,
                                                      transform=t)
        p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)

        if guideline_option == 'plus' or guideline_option == 'asterisk':
            s1.Line(point1=(x_left, circle_pos_y), point2=(x_right, circle_pos_y))
            s1.Line(point1=(circle_pos_x, y_lower), point2=(circle_pos_x, y_upper))
        if guideline_option == 'star' or guideline_option == 'asterisk':
            s1.Line(point1=(x_left, y_upper), point2=(x_right, y_lower))
            s1.Line(point1=(x_left, y_lower), point2=(x_right, y_upper))

        picked_faces = p.faces.findAt(((x_click, y_click, plate.thickness),))
        p.PartitionFaceBySketch(sketchUpEdge=p.datums[sketch_up_edge_id],
                                faces=picked_faces,
                                sketch=s1)
        del mdb.models[MODEL_NAME].sketches['__profile__']


def create_piezo_as_point_load(plate, piezo_element):
    # decompose piezo attributes
    piezo_pos_x = piezo_element.position_x
    piezo_pos_y = piezo_element.position_y
    piezo_radius = piezo_element.radius
    piezo_id = piezo_element.id

    # constants
    boundbox_scale = 1.0
    boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, piezo_id, BOUNDBOX_CELL_NAME)
    piezo_node_set_name = '{}_{}_node'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_element.set_name = piezo_node_set_name

    # retrieve Abaqus part and datums
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    sketch_plane_id = plate.datum_plane_abaqus_id
    sketch_up_edge_id = plate.datum_axis_abaqus_id

    # partition the plate to get a rectangular bounding box around the piezo element position
    lower_left_coord = (piezo_pos_x - boundbox_scale * piezo_radius, piezo_pos_y - boundbox_scale * piezo_radius)
    upper_right_coord = (piezo_pos_x + boundbox_scale * piezo_radius, piezo_pos_y + boundbox_scale * piezo_radius)
    _add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, boundbox_cell_name)

    # add line intersection at piezo center location by face partitioning (inside bounding box)
    t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)
    s.Line(point1=(piezo_pos_x - boundbox_scale * piezo_radius, piezo_pos_y),
           point2=(piezo_pos_x + boundbox_scale * piezo_radius, piezo_pos_y))
    s.Line(point1=(piezo_pos_x, piezo_pos_y - boundbox_scale * piezo_radius),
           point2=(piezo_pos_x, piezo_pos_y + boundbox_scale * piezo_radius))

    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    sketch_face = p.faces.findAt(
        ((piezo_pos_x, piezo_pos_y, plate.thickness),),
    )
    p.PartitionFaceBySketchThruAll(
        faces=sketch_face,
        sketchPlane=p.datums[sketch_plane_id],
        sketchUpEdge=p.datums[sketch_up_edge_id],
        sketchPlaneSide=SIDE1,
        sketch=s)

    # add line intersection point to piezo node set
    intersection_point = p.vertices.findAt(((piezo_pos_x, piezo_pos_y, plate.thickness),))
    p.Set(name=piezo_node_set_name, vertices=intersection_point)


def _add_bounding_box_to_plate(plate, lower_left_coord, upper_right_coord, boundbox_cell_name):
    # retrieve Abaqus part and datums
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    sketch_plane_id = plate.datum_plane_abaqus_id
    sketch_up_edge_id = plate.datum_axis_abaqus_id

    # partition the plate to get a rectangular bounding box around the piezo element position
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

    # update sets for plate top surface, bounding box, plate, and plate cell
    p.Set(faces=p.sets[PLATE_TOP_FACE_NAME].faces[0:1], name=PLATE_TOP_FACE_NAME)
    boundbox_cell = p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=0,
                                                                   zMax=plate.thickness,
                                                                   xMin=lower_left_coord[0],
                                                                   yMin=lower_left_coord[1],
                                                                   xMax=upper_right_coord[0],
                                                                   yMax=upper_right_coord[1])
    p.Set(cells=boundbox_cell, name=boundbox_cell_name)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[PLATE_CELL_NAME], p.sets[boundbox_cell_name]],
                   name=PLATE_CELL_NAME)


# STEP MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def create_step_dynamic_explicit(time_period, max_increment):
    mdb.models[MODEL_NAME].ExplicitDynamicsStep(name=STEP_NAME,
                                                previous='Initial',
                                                description='Lamb wave propagation (time domain)',
                                                timePeriod=time_period,
                                                maxIncrement=max_increment,
                                                nlgeom=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step=STEP_NAME)
    # mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1'].setValues(variables=(
    #     'S', 'E', 'U'), timeInterval=max_increment)
    mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'E', 'U'), numIntervals=10)


def add_amplitude(signal, excitation_id, max_time_increment):
    # generate time data
    time_data_table = []
    for t in np.arange(start=signal.dt, stop=signal.dt + signal.get_duration() * 1.01, step=max_time_increment / 2):
        time_data_table.append((t, signal.get_value_at(t=t)))

    # create in Abaqus
    mdb.models[MODEL_NAME].TabularAmplitude(name='amp-piezo-{}'.format(excitation_id),
                                            timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT,
                                            data=tuple(time_data_table))


# PROPERTY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def create_material(material_name):
    try:
        material_properties = get_material_properties(material_name)
        mdb.models[MODEL_NAME].Material(name=material_name)
        mdb.models[MODEL_NAME].materials[material_name].Density(table=((material_properties["density"],),))
        mdb.models[MODEL_NAME].materials[material_name].Elastic(table=((material_properties["youngs_modulus"],
                                                                        material_properties["poissons_ratio"]),))
    except ValueError as e:
        log_error(e)


def assign_material(set_name, material):
    # create new homogenous section
    section_name = set_name + '_section_homogenous_' + material
    mdb.models[MODEL_NAME].HomogeneousSolidSection(
        name=section_name,
        material=material,
        thickness=None)

    # create new set containing all cells and assign section to set
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    p.SectionAssignment(region=p.sets[set_name],
                        sectionName=section_name,
                        offset=0.0,
                        offsetType=MIDDLE_SURFACE,
                        offsetField='',
                        thicknessAssignment=FROM_SECTION)


# MESH MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def mesh_part(element_size, phased_array):
    # set meshing algorithm for plate
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)

    # set meshing algorithm for piezo elements
    for i in range(len(phased_array)):
        boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, i, BOUNDBOX_CELL_NAME)
        piezo_cell_name = '{}_{}'.format(PIEZO_CELL_NAME, i)
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=MEDIAL_AXIS)
        p.setMeshControls(regions=p.sets[piezo_cell_name].cells, algorithm=ADVANCING_FRONT)

    # seed and mesh part with desired element size
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

    meshStats = p.getMeshStats()
    log_info("The FE model has {} nodes.".format(meshStats.numNodes))
    return meshStats.numNodes


# ASSEMBLY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def create_assembly_instantiate_part():
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    a = mdb.models[MODEL_NAME].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name=INSTANCE_NAME,
               part=p,
               dependent=ON)
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=OFF,
        geometricRestrictions=OFF,
        stopConditions=OFF)


def make_datums_invisible():
    # function to hide all datum objects and set the projection to PARALLEL
    session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        datumPoints=OFF,
        datumAxes=OFF,
        datumPlanes=OFF,
        datumCoordSystems=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.geometryOptions.setValues(
        datumPoints=OFF,
        datumAxes=OFF,
        datumPlanes=OFF,
        datumCoordSystems=OFF)


# deprecated functions -------------------------------------------------------------------------------------------------
def save_viewport_to_png(center_x, center_y):
    # function to save a screenshot of the Abaqus viewport to a png file
    # center_x: x-coordinate of the center of the viewport
    # center_y: y-coordinate of the center of the viewport
    #
    # example:
    # save_viewport_to_png(0.5, 0.5, 1)
    # saves a screenshot of the viewport with the center at (0.5, 0.5) to the file '1.png'
    session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
    session.viewports['Viewport: 1'].view.setValues(cameraPosition=(center_x, center_y, 2.83871),
                                                    cameraTarget=(center_x, center_y, 0.01),
                                                    width=0.15)
    session.printToFile(
        filename='abaqus_screenshot_' + str(datetime.datetime.now()),
        format=PNG,
        canvasObjects=(session.viewports['Viewport: 1'],))
    log_info('Saved screenshot.')


# def add_vertex_to_plate(pos_x, pos_y):
#     id_cut_plane = [float("nan")] * 2
#     p = mdb.models[MODEL_NAME].parts[PART_NAME]
#     id_cut_plane[0] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=pos_x).id
#     id_cut_plane[1] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=pos_y).id
#     for i in range(2):
#         try:
#             p.PartitionCellByDatumPlane(datumPlane=p.datums[id_cut_plane[i]], cells=p.cells)
#         except:
#             log_warning('No partition created for excitation.')


# def add_concentrated_force(pos_x, pos_y, pos_z, amplitude, excitation_id):
#     set_name = "set-concentrated-force-{}".format(excitation_id)
#     a = mdb.models[MODEL_NAME].rootAssembly
#     v1 = a.instances[INSTANCE_NAME].vertices
#     verts1 = v1.findAt(coordinates=((pos_x, pos_y, pos_z),))
#     region = a.Set(vertices=verts1, name=set_name)
#     mdb.models[MODEL_NAME].ConcentratedForce(name='point-load-{}'.format(excitation_id),
#                                              createStepName=STEP_NAME,
#                                              region=region,
#                                              cf3=amplitude,
#                                              amplitude='amp-{}'.format(excitation_id),
#                                              distributionType=UNIFORM,
#                                              field='',
#                                              localCsys=None)


def write_input_file(job_name):
    mdb.Job(name=job_name, model=MODEL_NAME, description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=4,
            activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=4)
    mdb.jobs[job_name].writeInput(consistencyChecking=OFF)


def print_generate_area_vector(set_name):
    print(set_name)
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    for element in p.sets[set_name].cells[0].getElements():
        for face in element.getElemFaces():
            pass


def beautify_set_colors(phased_array):
    color_data = {}
    for i in range(len(phased_array)):
        key_1 = '{}_{}'.format(BOUNDBOX_CELL_NAME, i)
        key_2 = '{}_{}'.format(PIEZO_CELL_NAME, i)
        value_1 = (True, '#CCCCCC', 'Default', '#CCCCCC')
        value_2 = (True, '#FFDE7F', 'Default', '#FFDE7F')
        color_data[key_1] = value_1
        color_data[key_2] = value_2

    color_data[PLATE_CELL_NAME] = (True, '#CCCCCC', 'Default', '#CCCCCC')
    color_data[PLATE_TOP_FACE_NAME] = (True, '#CCCCCC', 'Default', '#CCCCCC')

    cmap = session.viewports['Viewport: 1'].colorMappings['Set']
    cmap.updateOverrides(overrides=color_data)
    session.viewports['Viewport: 1'].enableMultipleColors()  #
    session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')  #
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()  #


def add_piezo_load(piezo, max_time_increment):
    # generate time data
    time_data_table = []
    for t in np.arange(start=piezo.signal.dt, stop=piezo.signal.dt + piezo.signal.get_duration() * 1.01,
                       step=max_time_increment / 2):
        time_data_table.append((t, piezo.signal.get_value_at(t=t)))

    # create amplitude in Abaqus
    amplitude_name = 'amp-piezo-{}'.format(piezo.id)
    mdb.models[MODEL_NAME].TabularAmplitude(name=amplitude_name,
                                            timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT,
                                            data=tuple(time_data_table))

    # create the load
    load_name = 'load-piezo-{}'.format(piezo.id)
    surface_name = 'surface-piezo-{}'.format(piezo.id)

    assembly = mdb.models[MODEL_NAME].rootAssembly
    instance = assembly.instances[PART_NAME]
    region = assembly.Surface(side1Faces=instance.sets[piezo.wall_face_set_name].faces, name=surface_name)
    mdb.models[MODEL_NAME].Pressure(name=load_name,
                                    createStepName=STEP_NAME,
                                    region=region,
                                    distributionType=UNIFORM,
                                    field='', magnitude=1.0,
                                    amplitude=amplitude_name)


def create_piezo_element(plate, piezo_element):
    # decompose piezo attributes
    piezo_pos_x = piezo_element.position_x
    piezo_pos_y = piezo_element.position_y
    piezo_radius = piezo_element.radius
    piezo_thickness = piezo_element.thickness
    piezo_id = piezo_element.id

    # constants
    boundbox_scale = 1.5
    boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, piezo_id, BOUNDBOX_CELL_NAME)
    piezo_cell_name = '{}_{}'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_wall_face_set_name = '{}_{}_wall'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_element.wall_face_set_name = piezo_wall_face_set_name
    piezo_element.set_name = piezo_cell_name

    # create solid extrusion
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    sketch_plane_id = plate.datum_plane_abaqus_id
    sketch_up_edge_id = plate.datum_axis_abaqus_id
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
                   depth=piezo_thickness,
                   flipExtrudeDirection=OFF)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # partition the part into two cells (piezo-element and plate)
    plate_cell = p.sets[PLATE_CELL_NAME].cells[0:1]
    p.PartitionCellByDatumPlane(cells=plate_cell, datumPlane=p.datums[sketch_plane_id])
    p.Set(cells=p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=plate.thickness),
          faces=p.sets[PLATE_CELL_NAME].faces.getByBoundingBox(zMin=plate.thickness), name=piezo_cell_name)
    p.Set(cells=p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMax=plate.thickness), name=PLATE_CELL_NAME)

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

    # update sets for plate top surface, bounding box, plate, and plate cell
    p.Set(faces=p.sets[PLATE_TOP_FACE_NAME].faces[0:1], name=PLATE_TOP_FACE_NAME)
    boundbox_cell = p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=0,
                                                                   zMax=plate.thickness,
                                                                   xMin=lower_left_coord[0],
                                                                   yMin=lower_left_coord[1],
                                                                   xMax=upper_right_coord[0],
                                                                   yMax=upper_right_coord[1])
    p.Set(cells=boundbox_cell, name=boundbox_cell_name)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[PLATE_CELL_NAME], p.sets[boundbox_cell_name]],
                   name=PLATE_CELL_NAME)
    p.SetByBoolean(operation=DIFFERENCE,
                   sets=[p.sets[PLATE_SET_NAME], p.sets[piezo_cell_name]],
                   name=PLATE_SET_NAME)

    # generate guidelines for better mesh quality
    a = 1.3
    b = 0.7
    x_seq = np.array([-1, -1, -1, 0, 1, 1, 1, 0])
    y_seq = np.array([-1, 0, 1, 1, 1, 0, -1, -1])
    mask_x = np.array([1, a, 1, 1, 1, a, 1, 1])
    mask_y = np.array([1, 1, 1, a, 1, 1, 1, a])

    c = 1 / (sqrt(2) * boundbox_scale)
    temp = np.array([c, 1, c, 1, c, 1, c, 1])

    x_outer = x_seq * piezo_radius * boundbox_scale * temp + piezo_pos_x
    y_outer = y_seq * piezo_radius * boundbox_scale * temp + piezo_pos_y
    x_inner = x_seq * b * (1 / np.sqrt(2)) * piezo_radius * mask_x + piezo_pos_x
    y_inner = y_seq * b * (1 / np.sqrt(2)) * piezo_radius * mask_y + piezo_pos_y

    # draw guidelines
    temp_sketch_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                        offset=plate.thickness + piezo_thickness).id
    t = p.MakeSketchTransform(sketchPlane=p.datums[temp_sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)
    for i in range(len(x_seq)):
        s.Line(point1=(x_outer[i], y_outer[i]), point2=(x_inner[i], y_inner[i]))
        s.Line(point1=(x_inner[i - 1], y_inner[i - 1]), point2=(x_inner[i], y_inner[i]))

    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)

    # notiz an mich selbst: warum nicht cell -> faces -> getbyboundingbox? weil cell - faces leer ist
    face_array = p.faces.findAt(
        ((piezo_pos_x + piezo_radius * (1 + boundbox_scale) / 2, piezo_pos_y, plate.thickness),),
        ((piezo_pos_x + piezo_radius, piezo_pos_y, plate.thickness + 0.5 * piezo_thickness),),
        ((piezo_pos_x, piezo_pos_y, plate.thickness + piezo_thickness),)
    )

    p.PartitionFaceBySketchThruAll(
        faces=face_array,
        sketchPlane=p.datums[temp_sketch_plane_id],
        sketchUpEdge=p.datums[sketch_up_edge_id],
        sketchPlaneSide=SIDE1,
        sketch=s)

    # save the wall faces of the piezo element to a set named
    face_ids = p.sets[piezo_cell_name].cells[0].getFaces()
    vertical_face_ids = [face_id for face_id in face_ids if p.faces[face_id].getNormal()[2] == 0]
    vertical_faces = [p.faces[i:i + 1] for i in vertical_face_ids]
    p.Set(faces=vertical_faces, name=piezo_wall_face_set_name)
    # face_array = p.faces.getByBoundingCylinder(center1=(piezo_pos_x, piezo_pos_y, plate.thickness),
    #                                            center2=(piezo_pos_x, piezo_pos_y, plate.thickness + piezo_thickness),
    #                                            radius=piezo_radius)
    # p.Set(faces=face_array, name=piezo_wall_face_set_name)
