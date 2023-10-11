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
plate = IsotropicPlate(material='aluminum',
                       thickness=1e-3,
                       shape=((0, 0), (0.2, 0), (0.2, 0.2), (0.1, 0.18), (0.0, 0.2), (0, 0)))

# Add defects
plate.add_hole(position=(0.14, 0.04), radius=2e-3, guideline_option='asterisk')

# Create a burst input signal to excite Lamb waves
burst = Burst(carrier_frequency=100e3, n_cycles=3, dt=0, window='hanning')
point_force_excitation = PointForceExcitation(coordinates=(0.0, 0.0, 1e-3),
                                              amplitude=(0, 0, -1),
                                              signal=burst)
point_force_excitation.signal.plot()
# print("Added burst with " + str(burst.carrier_frequency / 1e3) + " kHz carrier frequency and " + str(burst.n_cycles) +
#       " cycles. Max. contained frequency is " + str(burst.get_max_contained_frequency() / 1e3) + " kHz.")

# Create an instance of FE model and link plate and excitation
fe_model = FEModel(plate=plate, excitation=point_force_excitation)
fe_model.nodes_per_wavelength = 10

# Generate the associated Abaqus geometry and mesh
fe_model.setup_in_abaqus()
# test
# test 2
