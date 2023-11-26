"""
This script generates a non-rectangular Abaqus/CAE plate measuring approximately 0.2 x 0.2 x 0.02 meters. It adds
a 2 mm diameter through-thickness hole and applies a point force, transmitting a burst signal through it.

Usage:
    (1) Ensure that the package "abaqus_guw" is in the same directory as this script.
    (2) Open Abaqus/CAE.
    (3) Set the Abaqus working directory to the path of this python script via "File > Set working directory ..."
    (4) Run this script in Abaqus/CAE via "File > Run script ..."

Author: j.froboese(at)tu-braunschweig.de
Created on: September 20, 2023
"""

from abaqus_guw.fe_model import *
from abaqus_guw.plate import *
from abaqus_guw.piezo_element import *
from abaqus_guw.signals import *
from abaqus_guw.defect import *
from abaqus_guw.load_case import *

# parameters
PLATE_THICKNESS = 3e-3
PLATE_WIDTH = 1.0
PHASED_ARRAY_RADIUS = 55e-3
PHASED_ARRAY_N_ELEMENTS = 9

# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add defects ----------------------------------------------------------------------------------------------------------
r = PHASED_ARRAY_RADIUS * 5
phi = 120.0*np.pi/180
pos_x = PLATE_WIDTH/2 + r * np.cos(phi)
pos_y = PLATE_WIDTH/2 + r * np.sin(phi)
defects = [Hole(position_x=pos_x, position_y=pos_y, diameter=15e-3)]

# add phased array -----------------------------------------------------------------------------------------------------                            
phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS+1)
pos_x = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.cos(phi)
pos_y = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.sin(phi)
for i in range(len(phi) - 1):
    print(pos_x[i])
    print(pos_y[i])
    phased_array.append(PiezoElement(position_x=pos_x[i],
                                     position_y=pos_y[i],
                                     diameter=18e-3,
                                     thickness=0.2e-3,
                                     material='pic255',
                                     electrode_thickness=1e-4,
                                     electrode_material='silver'))

# create one step / load case ------------------------------------------------------------------------------------------
dirac_impulse = DiracImpulse()
load_cases = []
for i in range(len(phased_array)):
    piezo_signals = [None] * len(phased_array)
    piezo_signals[i] = dirac_impulse
    i_step = LoadCase(name='impulse_piezo_{}'.format(i),
                      duration=3e-3,
                      piezo_signals=piezo_signals,
                      output_request='history')
    load_cases.append(i_step)
    
# apply a burst signal on piezo element 2
burst = Burst(carrier_frequency=200e3, n_cycles=3, dt=0, window='hanning')
piezo_signals = [None] * len(phased_array)
piezo_signals[0] = burst
load_cases.append(LoadCase(name='control_step',
                           duration=3e-3,
                           piezo_signals=piezo_signals,
                           output_request='history'))

# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, load_cases=load_cases)
fe_model.nodes_per_wavelength = 8
fe_model.elements_in_thickness_direction = 4
fe_model.model_approach = 'point_force'

# generate in abaqus
fe_model.setup_in_abaqus()
