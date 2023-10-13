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

from abaqus_guw.plate import IsotropicPlate
from abaqus_guw.fe_model import FEModel
from abaqus_guw.excitation import PointForceExcitation
from abaqus_guw.signals import Burst

# Create an instance of isotropic plate
THICKNESS = 3e-3
# plate = IsotropicPlate(material='aluminum',
#                        thickness=THICKNESS,
#                        shape=((0, 0), (0.2, 0), (0.2, 0.2), (0.1, 0.18), (0.0, 0.2), (0, 0)))

plate = IsotropicPlate(material='aluminum',
                       thickness=THICKNESS,
                       length=0.2,
                       width=0.2)

# Add defects
plate.add_hole(position=(0.10, 0.10), radius=2e-3, guideline_option='asterisk')
# plate.add_hole(position=(0.14, 0.11-1e-3), radius=2e-3, guideline_option='asterisk')

phi = np.linspace(0, 2 * np.pi, 10)
pos_x = 0.05 * np.cos(phi) + 0.1
pos_y = 0.05 * np.sin(phi) + 0.1


# Create a burst input signal to excite Lamb waves
burst = Burst(carrier_frequency=300e3, n_cycles=3, dt=0, window='hanning')
# point_force_excitation = PointForceExcitation(coordinates=(0.0, 0.0, THICKNESS),
#                                               amplitude=(0, 0, -1),
#                                               signal=burst)
# point_force_excitation.signal.plot()

# Create an instance of FE model and link plate and excitation
fe_model = FEModel(plate=plate, excitation=point_force_excitation)
fe_model.nodes_per_wavelength = 10
fe_model.elements_in_thickness_direction = 4

# Generate the associated Abaqus geometry and mesh
fe_model.setup_in_abaqus()
