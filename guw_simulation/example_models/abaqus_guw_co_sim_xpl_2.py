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
PLATE_WIDTH = 33e-3

# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH*2,
                       width=PLATE_WIDTH*2)

# add defects ----------------------------------------------------------------------------------------------------------
defects = [Hole(position_x=PLATE_WIDTH, position_y=(3.0/2.0)*PLATE_WIDTH, diameter=10e-3)]

# add phased array -----------------------------------------------------------------------------------------------------
phased_array = [PiezoElement(position_x=PLATE_WIDTH/2,
                             position_y=PLATE_WIDTH/2,
                             diameter=18e-3,
                             thickness=0.2e-3,
                             material='pic255',
                             electrode_thickness=1e-4,
                             electrode_material='silver'),
                PiezoElement(position_x=PLATE_WIDTH * 3 / 2,
                             position_y=PLATE_WIDTH / 2,
                             diameter=18e-3,
                             thickness=0.2e-3,
                             material='pic255',
                             electrode_thickness=1e-4,
                             electrode_material='silver')]

# create one step / load case ------------------------------------------------------------------------------------------
dirac_impulse = DiracImpulse()
load_cases = []
for i in range(len(phased_array)):
    piezo_signals = [None] * len(phased_array)
    piezo_signals[i] = dirac_impulse
    i_step = LoadCase(name='impulse_piezo_{}'.format(i),
                      duration=5e-3,
                      piezo_signals=piezo_signals,
                      output_request='history')
    load_cases.append(i_step)
    
# apply a burst signal on piezo element 2
burst = Burst(carrier_frequency=10e3, n_cycles=3, dt=0, window='hanning')
piezo_signals = [None] * len(phased_array)
piezo_signals[0] = burst
load_cases.append(LoadCase(name='control_step',
                           duration=5e-3,
                           piezo_signals=piezo_signals,
                           output_request='history'))

# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, load_cases=load_cases)
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4
fe_model.model_approach = 'point_force'

# generate in abaqus
fe_model.setup_in_abaqus()
