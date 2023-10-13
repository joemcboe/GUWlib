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
PLATE_CELL_NAME = 'plate'
PLATE_TOP_FACE_NAME = 'plate-top-surface'


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
    plate.datum_axis_abaqus_id = p.DatumAxisByTwoPoint(point1=(0, 0, plate.thickness),
                                                       point2=(0, 1, plate.thickness)).id
    session.viewports['Viewport: 1'].setValues(displayedObject=p)

    # store plate cell in set
    p.Set(cells=p.cells[0:1], name=PLATE_CELL_NAME)
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
    boundbox_cell_name = 'bounding_box_piezo_{}'.format(piezo_id)
    piezo_cell_name = 'piezo_{}'.format(piezo_id)

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

    # apply meshing algorithm
    p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=MEDIAL_AXIS)
    p.setMeshControls(regions=p.sets[piezo_cell_name].cells, algorithm=ADVANCING_FRONT)


# def add_circular_hole_to_plate(plate, circle_pos_x, circle_pos_y, circle_radius, guideline_option='none',
#                                meshing_algorithm="medial_axis"):
#     """
#     function to add a circular hole to a plate object
#
#     Args:
#         plate (plate):              plate object to add the hole to
#         circle_pos_x (float):       x-coordinate of the circular hole (center)
#         circle_pos_y (float):       y-coordinate of the circular hole (center)
#         circle_radius (float):      radius of the hole
#         guideline_option (string):  option to add partitions for a cleaner mesh,
#                                     available: 'none', 'plus', 'star', 'asterisk'
#         meshing_algorithm (string): set Abaqus meshing algorithm for the hole region
#                                     available: 'medial_axis' or 'advancing_front'
#
#     """
#     # add sketch of circle and cut through all
#     p = mdb.models[MODEL_NAME].parts[PART_NAME]
#     sketch_plane_id = plate.datum_plane_abaqus_id
#     sketch_up_edge_id = plate.datum_axis_abaqus_id
#     t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
#                               sketchUpEdge=p.datums[sketch_up_edge_id],
#                               sketchPlaneSide=SIDE1,
#                               sketchOrientation=RIGHT,
#                               origin=(0.0, 0.0, 0.0))
#     s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
#                                                  sheetSize=3.25,
#                                                  gridSpacing=0.08,
#                                                  transform=t)
#     p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
#     s.CircleByCenterPerimeter(center=(circle_pos_x, circle_pos_y),
#                               point1=(circle_pos_x + circle_radius, circle_pos_y))
#     p.CutExtrude(sketchPlane=p.datums[sketch_plane_id],
#                  sketchUpEdge=p.datums[sketch_up_edge_id],
#                  sketchPlaneSide=SIDE1,
#                  sketchOrientation=RIGHT,
#                  sketch=s,
#                  flipExtrudeDirection=OFF)
#     del mdb.models[MODEL_NAME].sketches['__profile__']
#     partition_circular_plate_region(plate, circle_pos_x, circle_pos_y, circle_radius, guideline_option,
#                                     meshing_algorithm)
#
#
# def add_circular_piezo_to_plate(plate, piezo_pos_x, piezo_pos_y, piezo_radius, piezo_thickness, guideline_option='plus',
#                                 meshing_algorithm="medial_axis"):
#     # add sketch of circle and extrude
#     p = mdb.models[MODEL_NAME].parts[PART_NAME]
#     sketch_plane_id = plate.datum_plane_abaqus_id
#     sketch_up_edge_id = plate.datum_axis_abaqus_id
#     t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
#                               sketchUpEdge=p.datums[sketch_up_edge_id],
#                               sketchPlaneSide=SIDE1,
#                               sketchOrientation=RIGHT,
#                               origin=(0.0, 0.0, 0.0))
#     s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
#                                                  sheetSize=3.25,
#                                                  gridSpacing=0.08,
#                                                  transform=t)
#     p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
#     s.CircleByCenterPerimeter(center=(piezo_pos_x, piezo_pos_y),
#                               point1=(piezo_pos_x + piezo_radius, piezo_pos_y))
#     p.SolidExtrude(sketchPlane=p.datums[sketch_plane_id],
#                    sketchUpEdge=p.datums[sketch_up_edge_id],
#                    sketchPlaneSide=SIDE1,
#                    sketchOrientation=RIGHT,
#                    sketch=s,
#                    depth=piezo_thickness,
#                    flipExtrudeDirection=OFF)
#     del mdb.models[MODEL_NAME].sketches['__profile__']
#     partition_circular_plate_region(plate, piezo_pos_x, piezo_pos_y, piezo_radius, guideline_option,
#                                     meshing_algorithm)
#
#
# def partition_circular_plate_region(plate, circle_pos_x, circle_pos_y, circle_radius, guideline_option='none',
#                                     meshing_algorithm="medial_axis"):
#
#     # get part and datum objects
#     p = mdb.models[MODEL_NAME].parts[PART_NAME]
#     sketch_plane_id = plate.datum_plane_abaqus_id
#     sketch_up_edge_id = plate.datum_axis_abaqus_id
#
#     # helper coordinates
#     bounding_box_scale = 2.5
#     x_left = circle_pos_x - bounding_box_scale * circle_radius
#     x_right = circle_pos_x + bounding_box_scale * circle_radius
#     y_lower = circle_pos_y - bounding_box_scale * circle_radius
#     y_upper = circle_pos_y + bounding_box_scale * circle_radius
#     x_click = circle_pos_x - 0.5 * bounding_box_scale * circle_radius
#     y_click = circle_pos_y + 0.5 * bounding_box_scale * circle_radius
#
#     # helper datum planes
#     id_cut_plane = [float("nan")] * 4
#     id_cut_plane[0] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_left).id
#     id_cut_plane[1] = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_right).id
#     id_cut_plane[2] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=y_lower).id
#     id_cut_plane[3] = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=y_upper).id
#
#     # partitioning
#     cut_plane_positions = ['left vertical', 'right vertical', 'lower horizontal', 'upper horizontal']
#     for i in range(4):
#         try:
#             p.PartitionCellByDatumPlane(datumPlane=p.datums[id_cut_plane[i]], cells=p.cells)
#         except:
#             log_warning('No partition created for ' + cut_plane_positions[i] + 'datum plane (circular region at (%f, '
#                                                                                '%f)).' % (circle_pos_x, circle_pos_y))
#
#     # add guidelines
#     if guideline_option == 'none':
#         pass
#     else:
#         t = p.MakeSketchTransform(sketchPlane=p.datums[sketch_plane_id],
#                                   sketchUpEdge=p.datums[sketch_up_edge_id],
#                                   sketchPlaneSide=SIDE1,
#                                   origin=(0.0, 0.0, 0))
#         s1 = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
#                                                       sheetSize=1.84,
#                                                       gridSpacing=0.04,
#                                                       transform=t)
#         p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
#
#         if guideline_option == 'plus' or guideline_option == 'asterisk':
#             s1.Line(point1=(x_left, circle_pos_y), point2=(x_right, circle_pos_y))
#             s1.Line(point1=(circle_pos_x, y_lower), point2=(circle_pos_x, y_upper))
#         if guideline_option == 'star' or guideline_option == 'asterisk':
#             s1.Line(point1=(x_left, y_upper), point2=(x_right, y_lower))
#             s1.Line(point1=(x_left, y_lower), point2=(x_right, y_upper))
#
#         picked_faces = p.faces.findAt(((x_click, y_click, plate.thickness),))
#         p.PartitionFaceBySketch(sketchUpEdge=p.datums[sketch_up_edge_id],
#                                 faces=picked_faces,
#                                 sketch=s1)
#         del mdb.models[MODEL_NAME].sketches['__profile__']
#
#     # set meshing algorithm for regions
#     picked_cell = p.cells.findAt(((x_click, y_click, plate.thickness),))
#     if meshing_algorithm == "medial_axis":
#         p.setMeshControls(regions=picked_cell, algorithm=MEDIAL_AXIS)
#     elif meshing_algorithm == "advancing_front":
#         p.setMeshControls(regions=picked_cell, algorithm=ADVANCING_FRONT)


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


def assign_material(material, set_name):
    # create new homogenous section
    section_name = set_name + '_section_homogenous_' + material
    mdb.models[MODEL_NAME].HomogeneousSolidSection(
        name=section_name,
        material=material,
        thickness=None)

    # create new set containing all cells and assign section to set
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    region = p.Set(cells=p.cells, name=set_name)
    p.SectionAssignment(region=region,
                        sectionName=section_name,
                        offset=0.0,
                        offsetType=MIDDLE_SURFACE,
                        offsetField='',
                        thicknessAssignment=FROM_SECTION)


def mesh_part(element_size=0.01):

    # set meshing algorithm for plate cell
    p = mdb.models[MODEL_NAME].parts[PART_NAME]
    p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)

    # seed and mesh part with desired element size
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
                                                maxIncrement=max_increment)
    # improvedDtMethod=ON)
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
    log_info('Saved screenshot.')
