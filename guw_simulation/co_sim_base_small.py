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
PLATE_WIDTH = 0.05

# create an instance of isotropic plate --------------------------------------------------------------------------------
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=PLATE_WIDTH,
                       width=PLATE_WIDTH)

# add defects ----------------------------------------------------------------------------------------------------------
defects = []

# add phased array -----------------------------------------------------------------------------------------------------
phased_array = [PiezoElement(position_x=PLATE_WIDTH/2,
                             position_y=PLATE_WIDTH/2,
                             diameter=18e-3,
                             thickness=0.2e-3,
                             material='pic255',
                             electrode_thickness=1e-4)]

# create FE model from plate, defects and phased array -----------------------------------------------------------------
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects, load_cases=[])
fe_model.max_frequency = 40e3
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4
fe_model.model_approach = 'piezo_electric'

# generate in abaqus
fe_model.setup_in_abaqus()
