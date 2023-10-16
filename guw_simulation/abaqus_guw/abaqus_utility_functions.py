# -*- coding: mbcs -*-
"""
This module provides utility functions for the classes fe_model, phased_array and plate to create and modify geometry
and to perform meshing in Abaqus/CAE using its python interpreter (Abaqus Scripting Interface).

Author: j.froboese(at)tu-braunschweig.de
Created on: September 20, 2023
"""

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
PIEZO_BOUNDBOX_CELL_NAME = 'piezo_bounding_box'


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
    p.Set(cells=p.cells[0:1], name=PLATE_CELL_NAME)     # contains the plate without the bounding boxes
    p.Set(cells=p.cells[0:1], name=PLATE_SET_NAME)      # contains the whole plate (for material assignment)
    p.Set(faces=p.faces.getByBoundingBox(zMin=plate.thickness / 2), name=PLATE_TOP_FACE_NAME)


def create_piezo_element(plate, piezo_element):
    # decompose piezo attributes
    piezo_pos_x = piezo_element.position_x
    piezo_pos_y = piezo_element.position_y
    piezo_radius = piezo_element.radius
    piezo_thickness = piezo_element.thickness
    piezo_id = piezo_element.id

    # constants
    boundbox_scale = 1.5
    boundbox_cell_name = '{}_{}'.format(PIEZO_BOUNDBOX_CELL_NAME, piezo_id)
    piezo_cell_name = '{}_{}'.format(PIEZO_CELL_NAME, piezo_id)
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
    p.Set(cells=p.sets[PLATE_CELL_NAME].cells.getByBoundingBox(zMin=plate.thickness), name=piezo_cell_name)
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
    p.SetByBoolean(operation=UNION,
                   sets=[p.sets[PLATE_SET_NAME]]

 #       cells=p.sets[PLATE_CELL_NAME].cells, name=PLATE_CELL_NAME)

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


def add_amplitude(signal, excitation_id, max_time_increment):
    # generate time data
    time_data_table = []
    for t in np.arange(start=signal.dt, stop=signal.dt + signal.get_duration(), step=max_time_increment / 2):
        time_data_table.append((t, signal.get_value_at(t=t)))

    # create in Abaqus
    mdb.models[MODEL_NAME].TabularAmplitude(name='amp-{}'.format(excitation_id),
                                            timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT,
                                            data=tuple(time_data_table))


def create_material(material):
    mdb.models[MODEL_NAME].Material(name=material)
    if material == 'aluminum':
        mdb.models[MODEL_NAME].materials[material].Density(table=((2700.0,),))
        mdb.models[MODEL_NAME].materials[material].Elastic(table=((70000000000.0, 0.33),))
    else:
        raise ValueError('Unknown material {}.'.format(material))


def assign_material(set_name, material):
    # create new homogenous section
    section_name = set_name + '_section_homogenous_' + material
    mdb.models[MODEL_NAME].HomogeneousSolidSection(
        name=section_name,
        material=material,
        thickness=None)

    # create new set containing all cells and assign section to set
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    # region = p.Set(cells=p.cells, name=set_name)
    p.SectionAssignment(region=p.sets[set_name],
                        sectionName=section_name,
                        offset=0.0,
                        offsetType=MIDDLE_SURFACE,
                        offsetField='',
                        thicknessAssignment=FROM_SECTION)


def mesh_part(element_size, phased_array):
    # set meshing algorithm for plate
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)

    # set meshing algorithm for piezo elements
    for i in range(len(phased_array)):
        boundbox_cell_name = '{}_{}'.format(PIEZO_BOUNDBOX_CELL_NAME, i)
        piezo_cell_name = '{}_{}'.format(PIEZO_CELL_NAME, i)
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=MEDIAL_AXIS)
        p.setMeshControls(regions=p.sets[piezo_cell_name].cells, algorithm=ADVANCING_FRONT)

    # seed and mesh part with desired element size
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()


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


def beautify_set_colors(phased_array):
    color_data = {}
    for i in range(len(phased_array)):
        key_1 = '{}_{}'.format(PIEZO_BOUNDBOX_CELL_NAME, i)
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


def create_step_dynamic_explicit(time_period, max_increment):
    mdb.models[MODEL_NAME].ExplicitDynamicsStep(name=STEP_NAME,
                                                previous='Initial',
                                                description='Lamb wave propagation (time domain)',
                                                timePeriod=time_period,
                                                maxIncrement=max_increment)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step=STEP_NAME)
    mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A',
        'EVF'), timeInterval=EVERY_TIME_INCREMENT)


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


def add_vertex_to_plate(pos_x, pos_y):
    id_cut_plane = [float("nan")] * 2
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    id_cut_plane[0] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=pos_x).id
    id_cut_plane[1] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=pos_y).id
    for i in range(2):
        try:
            p.PartitionCellByDatumPlane(datumPlane=p.datums[id_cut_plane[i]], cells=p.cells)
        except:
            log_warning('No partition created for excitation.')


def add_concentrated_force(pos_x, pos_y, pos_z, amplitude, excitation_id):
    set_name = "set-concentrated-force-{}".format(excitation_id)
    a = mdb.models[MODEL_NAME].rootAssembly
    v1 = a.instances[INSTANCE_NAME].vertices
    verts1 = v1.findAt(coordinates=((pos_x, pos_y, pos_z),))
    region = a.Set(vertices=verts1, name=set_name)
    mdb.models[MODEL_NAME].ConcentratedForce(name='point-load-{}'.format(excitation_id),
                                             createStepName=STEP_NAME,
                                             region=region,
                                             cf3=amplitude,
                                             amplitude='amp-{}'.format(excitation_id),
                                             distributionType=UNIFORM,
                                             field='',
                                             localCsys=None)
