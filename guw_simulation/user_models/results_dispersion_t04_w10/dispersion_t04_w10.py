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
PLATE_WIDTH = 0.5

# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add phased array -----------------------------------------------------------------------------------------------------
phased_array = [PiezoElement(position_x=PLATE_WIDTH * 0.5,
                             position_y=PLATE_WIDTH * 0.5,
                             diameter=18e-3)]

# create one step / load case ------------------------------------------------------------------------------------------

load_cases = []

# apply dirac impulse on piezo 0
burst = Burst(carrier_frequency=50e3, n_cycles=3, dt=0, window='hanning')
dirac_impulse = DiracImpulse()
piezo_signals = [dirac_impulse]
i_step = LoadCase(name='impulse_piezo_{}'.format(0),
                  duration=0.25e-3,
                  piezo_signals=piezo_signals,
                  output_request='history')
load_cases.append(i_step)

# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=[], load_cases=load_cases)
fe_model.max_frequency = 100e3
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4
fe_model.model_approach = 'point_force'
fe_model.element_type_temp = 'continuum'
fe_model.num_cores = 6

# generate in abaqus
fe_model.setup_in_abaqus()
