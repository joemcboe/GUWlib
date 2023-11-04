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

# parameters
PHASED_ARRAY_RADIUS = 0.05
PHASED_ARRAY_N_ELEMENTS = 9
PLATE_THICKNESS = 3e-3
PLATE_WIDTH = 0.2

# create an instance of isotropic plate
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add defects
defects = [Hole(position_x=6e-3, position_y=20e-3, radius=2e-3)]

# add two piezo elements
piezo_radius = 8e-3
piezo_thickness = 0.2e-3
phased_array = [PiezoElement(diameter=piezo_radius*2,
                             thickness=piezo_thickness,
                             position_x=PLATE_WIDTH*0.33,
                             position_y=PLATE_WIDTH*0.5,
                             material='pic255'),
                PiezoElement(diameter=piezo_radius * 2,
                             thickness=piezo_thickness,
                             position_x=PLATE_WIDTH * 0.66,
                             position_y=PLATE_WIDTH * 0.5,
                             material='pic255')]


# create FE model from plate, defects and phased array
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, max_frequency=200e3)
fe_model.nodes_per_wavelength = 8
fe_model.elements_in_thickness_direction = 4
fe_model.model_approach = 'point_force'

# generate in abaqus
fe_model.setup_in_abaqus()
