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
INSTANCE_NAME = PLATE_PART_NAME
STEP_NAME = 'lamb_excitation'

# bounding box scale
BOUNDBOX_SCALE = 1.5

# these are all sets and should maybe be named as such ...
PLATE_CELL_NAME = 'plate'
PLATE_TOP_FACE_NAME = 'plate-top-surface'
PLATE_SET_NAME = 'plate-material'

PIEZO_CELL_NAME = 'piezo'
DEFECT_CELL_NAME = 'defect'
BOUNDBOX_CELL_NAME = 'bounding_box'


# PART MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def create_piezo_socket_on_plate(plate, piezo_element):
    # decompose piezo attributes
    piezo_pos_x = piezo_element.position_x
    piezo_pos_y = piezo_element.position_y
    piezo_radius = piezo_element.radius
    piezo_thickness = piezo_element.thickness
    piezo_id = piezo_element.id

    # constants
    boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, piezo_id, BOUNDBOX_CELL_NAME)
    piezo_cell_name = '{}_{}'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_wall_face_set_name = '{}_{}_wall'.format(PIEZO_CELL_NAME, piezo_id)
    piezo_element.wall_face_set_name = piezo_wall_face_set_name
    piezo_element.set_name = piezo_cell_name

    # get part and datums
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    sketch_plane_id = plate.datum_plane_abaqus_id
    sketch_up_edge_id = plate.datum_axis_abaqus_id

    # partition the plate to get a rectangular bounding box around the piezo element
    lower_left_coord = (piezo_pos_x - BOUNDBOX_SCALE * piezo_radius, piezo_pos_y - BOUNDBOX_SCALE * piezo_radius)
    upper_right_coord = (piezo_pos_x + BOUNDBOX_SCALE * piezo_radius, piezo_pos_y + BOUNDBOX_SCALE * piezo_radius)
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

    # draw guidelines
    temp_sketch_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                        offset=plate.thickness).id
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

    s.CircleByCenterPerimeter(center=(piezo_pos_x, piezo_pos_y),
                              point1=(piezo_pos_x + piezo_radius, piezo_pos_y))

    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)

    face_array = p.faces.findAt(
        ((piezo_pos_x + piezo_radius * (1 + BOUNDBOX_SCALE) / 2, piezo_pos_y, plate.thickness),),
    )

    p.PartitionFaceBySketchThruAll(
        faces=face_array,
        sketchPlane=p.datums[temp_sketch_plane_id],
        sketchUpEdge=p.datums[sketch_up_edge_id],
        sketchPlaneSide=SIDE1,
        sketch=s)

    interface_geometry_set_name = 'piezo_{}_expl_interface'.format(piezo_id)
    interface_geometry = p.faces.getByBoundingCylinder(center1=(piezo_pos_x, piezo_pos_y, plate.thickness * 0.9),
                                                       center2=(piezo_pos_x, piezo_pos_y, plate.thickness * 1.1),
                                                       radius=piezo_radius * (1 + BOUNDBOX_SCALE) * 0.5)
    p.Set(name=interface_geometry_set_name, faces=interface_geometry)
    piezo_element.xpl_interface_set_name = interface_geometry_set_name
    del mdb.models[MODEL_NAME].sketches['__profile__']


def create_piezo_element(plate, piezo_element):
    # decompose piezo attributes
    piezo_radius = piezo_element.radius
    piezo_thickness = piezo_element.thickness
    piezo_id = piezo_element.id
    electrode_thickness = piezo_element.electrode_thickness

    piezo_part_name = "piezo_{}".format(piezo_id)
    piezo_element.part_name = piezo_part_name
    piezo_set_name = "piezo_ceramic"
    electrode_set_name = "electrode"

    # create an extrusion from two-dimensional shape
    s1 = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    s1.CircleByCenterPerimeter(center=(0, 0),
                               point1=(piezo_radius, 0))

    p = mdb.models[MODEL_NAME].Part(name=piezo_part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s1, depth=piezo_thickness + electrode_thickness)
    del mdb.models[MODEL_NAME].sketches['__profile__']

    # create cut plane
    cut_plane_abaqus_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                       offset=electrode_thickness).id

    # partition the part into two cells by cut plane (piezo-element and plate)
    p.PartitionCellByDatumPlane(cells=p.cells, datumPlane=p.datums[cut_plane_abaqus_id])
    p.Set(name=piezo_set_name, cells=p.cells.getByBoundingBox(zMin=electrode_thickness))
    p.Set(name=electrode_set_name, cells=p.cells.getByBoundingBox(zMax=electrode_thickness))

    # draw guidelines
    temp_sketch_plane_id = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                        offset=electrode_thickness + piezo_thickness).id
    sketch_up_edge_id = p.DatumAxisByTwoPoint(point1=(0, 0, 0),
                                              point2=(0, 1, 0)).id

    t = p.MakeSketchTransform(sketchPlane=p.datums[temp_sketch_plane_id],
                              sketchUpEdge=p.datums[sketch_up_edge_id],
                              sketchPlaneSide=SIDE1,
                              sketchOrientation=RIGHT,
                              origin=(0.0, 0.0, 0.0))
    s = mdb.models[MODEL_NAME].ConstrainedSketch(name='__profile__',
                                                 sheetSize=3.25,
                                                 gridSpacing=0.08,
                                                 transform=t)

    guideline_coordinates = get_guidelines(0, 0, piezo_radius)
    for coordinates in guideline_coordinates:
        s.Line(point1=coordinates[0], point2=coordinates[1])

    face_array = p.faces.findAt(
        ((piezo_radius, 0, 0.5*electrode_thickness),),
        ((piezo_radius, 0, electrode_thickness + 0.5*piezo_thickness),),
        ((0, 0, 0),)
    )
    print(face_array)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    p.PartitionFaceBySketchThruAll(
        faces=face_array,
        sketchPlane=p.datums[temp_sketch_plane_id],
        sketchUpEdge=p.datums[sketch_up_edge_id],
        sketchPlaneSide=SIDE1,
        sketch=s)

    interface_geometry_set_name = "std_interface"
    interface_geometry = p.faces.getByBoundingBox(zMax=electrode_thickness / 2)
    p.Set(name=interface_geometry_set_name, faces=interface_geometry)
    piezo_element.std_interface_set_name = interface_geometry_set_name


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


# MESH MODULE HELPER FUNCTIONS -----------------------------------------------------------------------------------------
def mesh_part_piezo_electric_approach(element_size, phased_array, defects):
    # set meshing algorithm for plate part
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    p.setMeshControls(regions=p.sets[PLATE_CELL_NAME].cells, algorithm=MEDIAL_AXIS)

    # piezo sockets
    for i in range(len(phased_array)):
        boundbox_cell_name = '{}_{}_{}'.format(PIEZO_CELL_NAME, i, BOUNDBOX_CELL_NAME)
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=ADVANCING_FRONT)

    for i in range(len(defects)):
        boundbox_cell_name = '{}_{}_{}'.format(DEFECT_CELL_NAME, i, BOUNDBOX_CELL_NAME)
        p.setMeshControls(regions=p.sets[boundbox_cell_name].cells, algorithm=ADVANCING_FRONT)

    # seed and mesh part with desired element size
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

    mesh_stats = p.getMeshStats()
    num_nodes = mesh_stats.numNodes

    # set meshing algorithm for piezo parts
    for piezo in phased_array:
        p = mdb.models[MODEL_NAME].parts[piezo.part_name]
        p.setMeshControls(regions=p.cells, algorithm=ADVANCING_FRONT)
        p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
        p.generateMesh()
        mesh_stats = p.getMeshStats()
        num_nodes += mesh_stats.numNodes

    log_info("The FE model has {} nodes.".format(num_nodes))
    return num_nodes


# ASSEMBLY MODULE HELPER FUNCTIONS -------------------------------------------------------------------------------------
def create_assembly_instantiate_plate_piezo_elements(plate, phased_array):
    # instantiate plate
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
    a = mdb.models[MODEL_NAME].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name=INSTANCE_NAME,
               part=p,
               dependent=ON)

    # instantiate piezo elements
    for piezo in phased_array:
        p = mdb.models[MODEL_NAME].parts[piezo.part_name]
        a.Instance(name=piezo.part_name,
                   part=p,
                   dependent=ON)
        a.translate(instanceList=(piezo.part_name,),
                    vector=(piezo.position_x, piezo.position_y, plate.thickness))


# STEP / LOAD MODULE HELPER FUNCTIONS ----------------------------------------------------------------------------------


def create_piezo_element_deprecated(plate, piezo_element):
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
    p = mdb.models[MODEL_NAME].parts[PLATE_PART_NAME]
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
