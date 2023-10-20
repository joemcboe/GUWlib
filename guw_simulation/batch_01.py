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

from abaqus_guw.fe_model import FEModel
from abaqus_guw.plate import *
from abaqus_guw.piezo_element import PiezoElement
from abaqus_guw.signals import *
from abaqus_guw.defect import *
from abaqus_guw.logger import *

import os
import sys


# parameters
PLATE_THICKNESS = 3e-3
PLATE_WIDTH = 0.1

# create an instance of isotropic plate
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add defects
defects = [Hole(position_x=6e-3, position_y=20e-3, radius=2e-3)]

piezo_pos_x = PLATE_WIDTH/2
piezo_pos_y = PLATE_WIDTH/2
piezo_radius = 8e-3
piezo_thickness = 0.2e-3
phased_array = [PiezoElement(diameter=piezo_radius*2,
                             thickness=piezo_thickness,
                             position_x=piezo_pos_x,
                             position_y=piezo_pos_y,
                             material='pic255')]

# create a burst input signal and add to first piezo element
burst = Burst(carrier_frequency=100e3, n_cycles=3, dt=0, window='hanning')
phased_array[0].signal = burst

# create FE model from plate, defects and phased array
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects)
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4
fe_model.propagation_distance = 0.2
fe_model.sim_name = 'batch_01'

# generate in abaqus
with OutputToFile(fe_model.sim_name):
    fe_model.setup_in_abaqus()

fe_model.write_input()
