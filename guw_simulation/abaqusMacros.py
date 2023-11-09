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


def gen_orphan():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.229368, 
        farPlane=0.328612, width=0.0390345, height=0.0181353, cameraPosition=(
        0.205781, -0.146414, 0.158264), cameraTarget=(0.0411164, 0.0111458, 
        0.0143706))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.245431, 
        farPlane=0.319721, cameraPosition=(0.153356, -0.109805, 0.228199), 
        cameraUpVector=(-0.538396, 0.780919, 0.316694), cameraTarget=(
        0.0393382, 0.0123875, 0.0167426))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.240508, 
        farPlane=0.324644, width=0.102276, height=0.0475173, cameraPosition=(
        0.158134, -0.110008, 0.225505), cameraTarget=(0.0441165, 0.012185, 
        0.0140491))
    p = mdb.models['Model-1'].parts['plate']
    p.PartFromMesh(name='orphan', copySets=True)
    p1 = mdb.models['Model-1'].parts['orphan']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.167583, 
        farPlane=0.279826, width=0.129402, height=0.0601199, cameraPosition=(
        0.180132, 0.156697, 0.127289), cameraTarget=(0.050976, 0.0275411, 
        -0.00186712))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.17369, 
        farPlane=0.270384, cameraPosition=(0.199039, 0.0532729, 0.16384), 
        cameraUpVector=(-0.195974, 0.889395, -0.413003), cameraTarget=(
        0.050976, 0.0275411, -0.00186713))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.178571, 
        farPlane=0.259783, cameraPosition=(0.108532, -0.110053, 0.164076), 
        cameraUpVector=(-0.0635475, 0.933374, 0.353234), cameraTarget=(
        0.0516555, 0.0287673, -0.0018689))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.160397, 
        farPlane=0.279747, cameraPosition=(0.182091, -0.136164, 0.0724873), 
        cameraUpVector=(-0.296229, 0.554867, 0.777413), cameraTarget=(
        0.0501361, 0.0293066, 2.29208e-05))
    session.viewports['Viewport: 1'].partDisplay.setValues(mesh=OFF)
    session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
        meshTechnique=OFF)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    p1 = mdb.models['Model-1'].parts['orphan']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models['Model-1'].Part(name='orphan-plate', 
        objectToCopy=mdb.models['Model-1'].parts['orphan'])
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.164339, 
        farPlane=0.283069, cameraPosition=(0.207808, -0.0362485, 0.147899), 
        cameraUpVector=(-0.223537, 0.965222, 0.135565), cameraTarget=(0.05, 
        0.025, 0.00164999))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.162731, 
        farPlane=0.284678, cameraPosition=(0.175006, -0.118102, 0.119713), 
        cameraUpVector=(-0.159194, 0.826942, 0.539281), cameraTarget=(0.05, 
        0.025, 0.00165))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.162731, 
        farPlane=0.284678, cameraPosition=(0.175006, -0.118102, 0.119713), 
        cameraUpVector=(-0.461882, 0.631463, 0.622832), cameraTarget=(0.05, 
        0.025, 0.00165))


def delete_orphan_parts():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.191915, 
        farPlane=0.255493, width=0.0897396, height=0.0415756, cameraPosition=(
        0.0312228, -0.198704, 0.00114914), cameraTarget=(0.0312228, 0.025, 
        0.00114914))
    session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
    session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
        meshTechnique=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    mdb.meshEditOptions.setValues(enableUndo=True, maxUndoCacheElements=0.5)
    p = mdb.models['Model-1'].parts['orphan-piezo']
    p.deleteElement(elements=p.sets['plate-material'], deleteUnreferencedNodes=ON)


def assign_elem_type():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.185422, 
        farPlane=0.278078, width=0.0309414, height=0.0143753, cameraPosition=(
        0.140761, -0.168004, 0.0938314), cameraTarget=(0.0388367, 0.0116324, 
        0.00789416))
    elemType1 = mesh.ElemType(elemCode=C3D8E, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D6E, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D4E, elemLibrary=STANDARD)
    p = mdb.models['Model-1'].parts['plate']
    c = p.cells
    cells = c.getSequenceFromMask(mask=('[#40 ]', ), )
    pickedRegions =(cells, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
        elemType3))


def del_set():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.174249, 
        farPlane=0.273126, width=0.0652347, height=0.0302227, cameraPosition=(
        0.171074, 0.162608, 0.130256), cameraTarget=(0.0419277, 0.0334617, 
        0.00111063))
    del mdb.models['Model-1'].parts['plate-mesh'].sets['transducer_0_bot_surf']


def lineasr_constraint():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.18043, 
        farPlane=0.285877, width=0.0994471, height=0.046073, 
        viewOffsetX=0.00133349, viewOffsetY=0.0113521)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.183936, 
        farPlane=0.282372, width=0.0498791, height=0.0231086, 
        viewOffsetX=-0.00958739, viewOffsetY=0.00496563)
    mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 
        'XPL_mesh.transducer_0_GND_slave', 9), (-1.0, 
        'XPL_mesh.transducer_0_GND', 9)))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.184999, 
        farPlane=0.281308, width=0.0325325, height=0.015072, 
        viewOffsetX=-0.0131378, viewOffsetY=0.00382096)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        renderStyle=WIREFRAME)


def split_model():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.172212, 
        farPlane=0.261583, width=0.134212, height=0.0621795, cameraPosition=(
        -0.0040378, -0.149646, 0.118472), cameraTarget=(0.0547105, 0.0275255, 
        -0.00482599))
    mdb.Model(name='Model-1-STD', objectToCopy=mdb.models['Model-1'])
    a = mdb.models['Model-1-STD'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    mdb.models.changeKey(fromName='Model-1', toName='Model-1-XPL')
    a = mdb.models['Model-1-XPL'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a = mdb.models['Model-1-STD'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        adaptiveMeshConstraints=OFF)
    mdb.models['Model-1-STD'].linkInstances(instancesMap=(('XPL_mesh', 
        mdb.models['Model-1-XPL'].rootAssembly.instances['XPL_mesh']), ))
    a = mdb.models['Model-1-STD'].rootAssembly
    a.excludeFromSimulation(instances=(a.instances['XPL_mesh'], ), exclude=True)
    a = mdb.models['Model-1-XPL'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    mdb.models['Model-1-XPL'].linkInstances(instancesMap=(('STD_mesh', 
        mdb.models['Model-1-STD'].rootAssembly.instances['STD_mesh']), ))
    a = mdb.models['Model-1-XPL'].rootAssembly
    a.excludeFromSimulation(instances=(a.instances['STD_mesh'], ), exclude=True)


def create_piezo_material():
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
    mdb.models['Model-1'].Material(name='piezo_material')
    mdb.models['Model-1'].materials['piezo_material'].Density(table=((7800.0, ), ))
    mdb.models['Model-1'].materials['piezo_material'].Elastic(
        type=ENGINEERING_CONSTANTS, table=((60610000000.0, 48310000000.0, 
        60610000000.0, 0.512, 0.289, 0.408, 23000000000.0, 23500000000.0, 
        23000000000.0), ))
    mdb.models['Model-1'].materials['piezo_material'].Dielectric(type=ORTHOTROPIC, 
        table=((1.505e-08, 1.301e-08, 1.505e-08), ))
    mdb.models['Model-1'].materials['piezo_material'].Piezoelectric(type=STRAIN, 
        table=((0.0, 0.0, 0.0, 7.41e-10, 0.0, 0.0, -2.74e-10, 5.93e-10, 
        -2.74e-10, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.41e-10), ))


def cosim_interaction():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.189733, 
        farPlane=0.293358, width=0.0933355, height=0.0414071, 
        viewOffsetX=-0.000525917, viewOffsetY=0.0048358)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=OFF, 
        constraints=OFF, connectors=OFF, engineeringFeatures=OFF, 
        adaptiveMeshConstraints=ON)
    mdb.models['Model-1-XPL'].ExplicitDynamicsStep(name='Step-1', 
        previous='Initial', nlgeom=OFF, improvedDtMethod=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON, 
        adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1-XPL'].rootAssembly
    region=a.instances['XPL_mesh'].sets['XPL_interface_nodes']
    mdb.models['Model-1-XPL'].StdXplCosimulation(name='Int-1', 
        createStepName='Step-1', region=region, incrementation=LOCKSTEP, 
        stepSizeDefinition=DEFAULT, stepSize=0.0)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.191743, 
        farPlane=0.291348, width=0.0732191, height=0.0324827, 
        viewOffsetX=0.00265824, viewOffsetY=0.00876566)
    a = mdb.models['Model-1-STD'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Initial')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=OFF, 
        constraints=OFF, connectors=OFF, engineeringFeatures=OFF, 
        adaptiveMeshConstraints=ON)
    mdb.models['Model-1-STD'].ImplicitDynamicsStep(name='Step-1', 
        previous='Initial')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.193061, 
        farPlane=0.29003, width=0.0463231, height=0.0205507, 
        viewOffsetX=-0.0117741, viewOffsetY=0.00787984)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON, 
        adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1-STD'].rootAssembly
    region=a.instances['STD_mesh'].sets['STD_interface_nodes']
    mdb.models['Model-1-STD'].StdXplCosimulation(name='Int-1', 
        createStepName='Step-1', region=region, incrementation=LOCKSTEP, 
        stepSizeDefinition=DEFAULT, stepSize=0.0)


def add_piezo_bc():
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
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.193818, 
        farPlane=0.292414, width=0.0750557, height=0.0332975, 
        viewOffsetX=0.000716028, viewOffsetY=0.00279548)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        step='load_case_0_control_step')
    a = mdb.models['Model-1-STD'].rootAssembly
    region = a.instances['STD_mesh'].sets['transducer_0_SIGNAL']
    mdb.models['Model-1-STD'].ElectricPotentialBC(name='BC-1', 
        createStepName='load_case_0_control_step', region=region, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', magnitude=1.0, 
        amplitude='piezo_1_Burst')
    a = mdb.models['Model-1-STD'].rootAssembly
    region = a.instances['STD_mesh'].sets['transducer_0_GND']
    mdb.models['Model-1-STD'].ElectricPotentialBC(name='BC-2', 
        createStepName='load_case_0_control_step', region=region, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', magnitude=0.0, amplitude=UNSET)


