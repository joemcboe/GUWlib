# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def translate():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=1.30728, 
        farPlane=2.0412, width=0.306222, height=0.14187, 
        viewOffsetX=-0.0847879, viewOffsetY=-0.0586198)
    a1 = mdb.models['Model-1'].rootAssembly
    a1.translate(instanceList=('piezo_0-1', ), vector=(0.0, 0.0, 1.0))


