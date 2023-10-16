# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def nlgeom():
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
    mdb.models['Model-1'].steps['lamb_excitation'].setValues(nlgeom=OFF)


def wall_pressure():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.549648, 
        farPlane=0.785624, width=0.0188695, height=0.00905723, cameraPosition=(
        0.458728, 0.522601, 0.37665), cameraTarget=(0.0732683, 0.137141, 
        -0.00880965))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.549546, 
        cameraPosition=(0.46073, 0.51844, 0.378809), cameraTarget=(0.0752705, 
        0.13298, -0.00665062))
    session.viewports['Viewport: 1'].view.setValues(cameraPosition=(0.459228, 
        0.51766, 0.381091), cameraTarget=(0.0737685, 0.1322, -0.00436841))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.541051, 
        farPlane=0.769283, cameraPosition=(0.590341, 0.360489, 0.351685), 
        cameraUpVector=(-0.673587, -0.409893, 0.615036), cameraTarget=(
        0.0737686, 0.1322, -0.00436844))
    session.viewports['Viewport: 1'].view.setValues(cameraUpVector=(-0.573545, 
        -0.579712, 0.578775), cameraTarget=(0.0737686, 0.1322, -0.00436844))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.49756, 
        farPlane=0.755511, cameraPosition=(0.657717, -0.1202, 0.185436), 
        cameraUpVector=(-0.74579, -0.55579, 0.36728), cameraTarget=(0.0724863, 
        0.141348, -0.00120449))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.494773, 
        farPlane=0.758298, width=0.0530585, height=0.0254677, cameraPosition=(
        0.658786, -0.119045, 0.183702), cameraTarget=(0.0735555, 0.142503, 
        -0.00293873))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.494487, 
        farPlane=0.758584, cameraPosition=(0.660662, -0.105583, 0.196686), 
        cameraTarget=(0.075431, 0.155965, 0.0100452))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.569141, 
        farPlane=0.732187, cameraPosition=(0.554416, 0.170725, 0.463556), 
        cameraUpVector=(-0.175698, -0.957303, -0.229567), cameraTarget=(
        0.0824006, 0.137839, -0.00746121))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.59408, 
        farPlane=0.713865, cameraPosition=(-0.222261, 0.105747, 0.571967), 
        cameraUpVector=(0.835152, -0.54755, 0.0520623), cameraTarget=(0.102659, 
        0.139534, -0.0102889))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.544957, 
        farPlane=0.786967, cameraPosition=(-0.523506, 0.276959, 0.159118), 
        cameraUpVector=(0.560313, -0.00945217, 0.828227), cameraTarget=(
        0.108953, 0.135957, -0.00166334))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.546993, 
        farPlane=0.784931, width=0.0285781, height=0.0137173, cameraPosition=(
        -0.523418, 0.279239, 0.157465), cameraTarget=(0.109041, 0.138237, 
        -0.0033159))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.547157, 
        farPlane=0.784767, cameraPosition=(-0.525701, 0.26935, 0.157154), 
        cameraTarget=(0.106758, 0.128348, -0.00362686))
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['plate'].faces
    side1Faces1 = s1.getSequenceFromMask(mask=('[#243fc00 ]', ), )
    region = a.Surface(side1Faces=side1Faces1, name='Surf-1')
    mdb.models['Model-1'].Pressure(name='Load-1', createStepName='lamb_excitation', 
        region=region, distributionType=UNIFORM, field='', magnitude=1.0, 
        amplitude='amp-piezo-0')


