# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def solid_circ_extrusion():
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
    p = mdb.models['Model-1'].parts['plate']
    f, e = p.faces, p.edges
    t = p.MakeSketchTransform(sketchPlane=f[11], sketchUpEdge=e[35], 
        sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.066088, 
        0.116776, 0.003))
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=0.48, 
        gridSpacing=0.01, transform=t)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['plate']
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.388547, 
        farPlane=0.436645, width=0.247784, height=0.120985, cameraPosition=(
        0.0761775, 0.115307, 0.414096), cameraTarget=(0.0761775, 0.115307, 
        0.003))
    s.CircleByCenterPerimeter(center=(-0.0025, 0.005), point1=(0.008, 0.0))
    p = mdb.models['Model-1'].parts['plate']
    f1, e1 = p.faces, p.edges
    p.SolidExtrude(sketchPlane=f1[11], sketchUpEdge=e1[35], sketchPlaneSide=SIDE1, 
        sketchOrientation=RIGHT, sketch=s, depth=0.0002, 
        flipExtrudeDirection=OFF)
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']


