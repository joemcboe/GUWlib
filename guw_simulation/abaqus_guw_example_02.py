"""
abaqus_guw_example_02
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
PLATE_WIDTH = 50e-3
PHASED_ARRAY_RADIUS = PLATE_WIDTH/4
PHASED_ARRAY_N_ELEMENTS = 3



# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)


# add defects ----------------------------------------------------------------------------------------------------------
defects = [Hole(position_x=40e-3, position_y=40e-3, diameter=4e-3)]

# add phased array -----------------------------------------------------------------------------------------------------
phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS+1)
pos_x = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.cos(phi)
pos_y = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.sin(phi)
for i in range(len(phi) - 1):
    phased_array.append(PiezoElement(position_x=pos_x[i],
                                     position_y=pos_y[i],
                                     diameter=10e-3))

# add steps ------------------------------------------------------------------------------------------------------------
# add one step for each piezo element and apply impulse on this, and no signal on the other piezo elements
dirac_impulse = DiracImpulse()
load_cases = []
for i in range(len(phased_array)):
    piezo_signals = [None] * len(phased_array)
    piezo_signals[i] = dirac_impulse
    i_step = LoadCase(name='impulse_piezo_{}'.format(i),
                      duration=0.1,
                      piezo_signals=piezo_signals,
                      output_request='history')
    load_cases.append(i_step)

# add one additional step and apply a burst signal on piezo element 2
burst = Burst(carrier_frequency=10e3, n_cycles=3, dt=0, window='hanning')
piezo_signals = [None] * len(phased_array)
piezo_signals[i] = burst
load_cases.append(LoadCase(name='control_step',
                           duration=0.1,
                           piezo_signals=piezo_signals,
                           output_request='field'))


# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, load_cases=load_cases)
fe_model.max_frequency = 20e3
fe_model.nodes_per_wavelength = 6
fe_model.elements_in_thickness_direction = 1
fe_model.model_approach = 'point_force'

# generate in abaqus
fe_model.setup_in_abaqus()
