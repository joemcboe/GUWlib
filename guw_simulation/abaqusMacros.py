# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def add_step():
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
    mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial', 
        timePeriod=0.1, maxIncrement=1e-10, nlgeom=OFF, improvedDtMethod=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
        predefinedFields=ON, connectors=ON, adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1'].rootAssembly
    region = a.instances['plate'].sets['piezo_0_node']
    mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1', 
        region=region, cf3=1.0, amplitude='step_0_piezo_0_DiracImpulse', 
        distributionType=UNIFORM, field='', localCsys=None)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF, 
        predefinedFields=OFF, connectors=OFF, adaptiveMeshConstraints=ON)
    regionDef=mdb.models['Model-1'].rootAssembly.allInstances['plate'].sets['piezo_0_node']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2', 
        createStepName='Step-1', variables=('U1', 'U2', 'U3'), frequency=1, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'U', 'V'), numIntervals=100)


def add_load():
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
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        step='step_0_impulse_piezo_0')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
        predefinedFields=ON, connectors=ON, adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1'].rootAssembly
    region = a.instances['plate'].sets['piezo_0_node']
    mdb.models['Model-1'].ConcentratedForce(name='Load-1', 
        createStepName='step_0_impulse_piezo_0', region=region, cf3=1.0, 
        amplitude='step_0_piezo_0_DiracImpulse', distributionType=UNIFORM, 
        field='', localCsys=None)


def inpfile():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.633059, 
        farPlane=1.02524, width=0.3999, height=0.18527, viewOffsetX=0.00769299, 
        viewOffsetY=0.00639101)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF, 
        predefinedFields=OFF, connectors=OFF)
    mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, 
        nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
        contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
        resultsFormat=ODB)


def fullfield():
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
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        step='load_case_7_control_step')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        adaptiveMeshConstraints=ON)
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-1', 
        createStepName='load_case_7_control_step', variables=('U', ), 
        numIntervals=200, timeMarks=ON, position=NODES)


def fullfield_2():
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
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2', 
        createStepName='load_case_7_control_step', variables=('U', ), 
        timeInterval=EVERY_TIME_INCREMENT, position=NODES)


