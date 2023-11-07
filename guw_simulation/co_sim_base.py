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
PHASED_ARRAY_RADIUS = PLATE_WIDTH/4
PHASED_ARRAY_N_ELEMENTS = 2

# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add defects ----------------------------------------------------------------------------------------------------------
defects = [Hole(position_x=100e-3, position_y=100e-3, diameter=20e-3)]

# add phased array -----------------------------------------------------------------------------------------------------
phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS+1)
pos_x = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.cos(phi)
pos_y = PLATE_WIDTH/2 + PHASED_ARRAY_RADIUS * np.sin(phi)
for i in range(len(phi) - 1):
    phased_array.append(PiezoElement(position_x=pos_x[i],
                                     position_y=pos_y[i],
                                     diameter=18e-3))


# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, load_cases=[])
fe_model.max_frequency = 40e3
fe_model.nodes_per_wavelength = 6
fe_model.elements_in_thickness_direction = 1
fe_model.model_approach = 'piezo_electric'

# generate in abaqus
fe_model.setup_in_abaqus()
