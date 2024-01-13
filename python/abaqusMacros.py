# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def view():
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
    a = mdb.models['guw_model'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
    session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
    session.viewports['Viewport: 1'].assemblyDisplay.geometryOptions.setValues(
        datumPoints=OFF, datumAxes=OFF, datumPlanes=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.25525, farPlane=0.409669, cameraPosition=(-3.044590, -4.635415, 5.748052), cameraUpVector=(0.373843,0.612867,0.69615), cameraTarget=(0.362526,0.594315,-0.71788))
    session.viewports['Viewport: 1'].setColor(initialColor='#409EF0')
    cmap = session.viewports['Viewport: 1'].colorMappings['Part geometry']
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()

