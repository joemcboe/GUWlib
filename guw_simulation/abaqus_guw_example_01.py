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

# Create an instance of isotropic plate
plate = IsotropicPlate(material='aluminum',
                       thickness=PLATE_THICKNESS,
                       length=0.2,
                       width=0.2)

# Add defects
defects = [Hole(position_x=6e-3, position_y=20e-3, radius=2e-3)]

# Add piezo elements and arrange in circular phased array
phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS+1)
pos_x = PHASED_ARRAY_RADIUS * np.cos(phi) + 0.1
pos_y = PHASED_ARRAY_RADIUS * np.sin(phi) + 0.1
for i in range(len(phi) - 6):
    phased_array.append(PiezoElement(diameter=16e-3,
                                     thickness=0.2e-3,
                                     position_x=pos_x[i],
                                     position_y=pos_y[i],
                                     material='aluminum'))

# Create a burst input signal
burst = Burst(carrier_frequency=300e3, n_cycles=3, dt=0, window='hanning')
phased_array[0].signal = burst

# Create an instance of FE model and link plate and piezo array
fe_model = FEModel(plate=plate, phased_array=phased_array, defects=defects)
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4

# Generate the associated Abaqus geometry and mesh
fe_model.setup_in_abaqus()
