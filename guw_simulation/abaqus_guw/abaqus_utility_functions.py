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

PART_NAME = 'plate'
MODEL_NAME = 'Model-1'
INSTANCE_NAME = PART_NAME
STEP_NAME = 'lamb_excitation'


# DATUM_PLANE_NAME = 'plate-surface'
# DATUM_AXIS_NAME = 'plate-right-edge'


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
    plate.datum_axis_abaqus_id = p.DatumAxisByTwoPoint(point1=(1, 0, plate.thickness),
                                                       point2=(1, 1, plate.thickness)).id
    session.viewports['Viewport: 1'].setValues(displayedObject=p)


def add_circular_hole_to_plate(plate, circle_pos_x, circle_pos_y, circle_radius, guideline_option='none',
                               meshing_algorithm="medial_axis"):
    """
    function to add a circular hole to a plate object

    Args:
        plate (plate):              plate object to add the hole to
        circle_pos_x (float):       x-coordinate of the circular hole (center)
        circle_pos_y (float):       y-coordinate of the circular hole (center)
        circle_radius (float):      radius of the hole
        guideline_option (string):  option to add partitions for a cleaner mesh,
                                    available: 'none', 'plus', 'star', 'asterisk'
        meshing_algorithm (string): set Abaqus meshing algorithm for the hole region
                                    available: 'medial_axis' or 'advancing_front'

    """
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
    bounding_box_scale = 2.5
    x_left = circle_pos_x - bounding_box_scale * circle_radius
    x_right = circle_pos_x + bounding_box_scale * circle_radius
    y_lower = circle_pos_y - bounding_box_scale * circle_radius
    y_upper = circle_pos_y + bounding_box_scale * circle_radius
    x_click = circle_pos_x - 0.5 * bounding_box_scale * circle_radius
    y_click = circle_pos_y + 0.5 * bounding_box_scale * circle_radius

    # helper datum planes
    id_cut_plane = [float("nan")] * 4
    id_cut_plane[0] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_left).id
    id_cut_plane[1] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_right).id
    id_cut_plane[2] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=y_lower).id
    id_cut_plane[3] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=y_upper).id

    # partitioning
    cut_plane_positions = ['left vertical', 'right vertical', 'lower horizontal', 'upper horizontal']
    for i in range(4):
        try:
            p.PartitionCellByDatumPlane(datumPlane=p.datums[id_cut_plane[i]], cells=p.cells)
        except:
            print('No partition created for ' + cut_plane_positions[i] + ' datum plane (hole at (%f, %f)).' % (
                circle_pos_x, circle_pos_y))

    # add guidelines
    if guideline_option == 'none':
        pass
    else:
        t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
                                  sketchUpEdge=p.datums[sketch_up_edge_id],
                                  sketchPlaneSide=SIDE1,
                                  origin=(0.0, 0.0, plate.thickness))
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

    # set meshing algorithm for regions
    picked_cell = p.cells.findAt(((x_click, y_click, plate.thickness),))
    if meshing_algorithm == "medial_axis":
        p.setMeshControls(regions=picked_cell, algorithm=MEDIAL_AXIS)
    elif meshing_algorithm == "advancing_front":
        p.setMeshControls(regions=picked_cell, algorithm=ADVANCING_FRONT)


def add_vertex_to_plate(pos_x, pos_y):
    id_cut_plane = [float("nan")] * 2
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    id_cut_plane[0] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=pos_x).id
    id_cut_plane[1] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=pos_y).id
    for i in range(2):
        try:
            p.PartitionCellByDatumPlane(datumPlane=p.datums[id_cut_plane[i]], cells=p.cells)
        except:
            print('No partition created for excitation.')


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


def _create_material(material):
    mdb.models[MODEL_NAME].Material(name=material)
    if material == 'aluminum':
        mdb.models[MODEL_NAME].materials[material].Density(table=((2700.0,),))
        mdb.models[MODEL_NAME].materials[material].Elastic(table=((70000000000.0, 0.33),))
    else:
        raise ValueError('Unknown material {}.'.format(material))


def assign_material(material):
    # create the new material
    _create_material(material)

    # create new homogenous section
    section_name = PART_NAME + '_section_homogenous_' + material
    mdb.models[MODEL_NAME].HomogeneousSolidSection(
        name=section_name,
        material=material,
        thickness=None)

    # create new set containing all cells and assign section to set
    set_name = 'set-' + PART_NAME
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    region = p.Set(cells=p.cells, name=set_name)
    p.SectionAssignment(region=region,
                        sectionName=section_name,
                        offset=0.0,
                        offsetType=MIDDLE_SURFACE,
                        offsetField='',
                        thicknessAssignment=FROM_SECTION)


def mesh_part(element_size=0.01):
    # seed and mesh part with desired element size
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()


def create_assembly_instantiate_plate():
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


def create_step_dynamic_explicit(time_period, max_increment):
    mdb.models[MODEL_NAME].ExplicitDynamicsStep(name=STEP_NAME,
                                                previous='Initial',
                                                description='Generation and propagation of Lamb waves',
                                                timePeriod=time_period,
                                                maxIncrement=max_increment, improvedDtMethod=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step=STEP_NAME)
    mdb.models[MODEL_NAME].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A',
        'EVF'), timeInterval=EVERY_TIME_INCREMENT)


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
    print('Saved screenshot.')
