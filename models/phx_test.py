"""
Input file for guwlib.
"""

from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 0.5
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 2
PHASED_ARRAY_RADIUS = 90e-3

# basic simulation parameters ------------------------------------------------------------------------------------------
model = FEModel()
model.max_frequency = 200e3
model.elements_per_wavelength = 25
model.elements_in_thickness_direction = 4
model.model_approach = 'point_force'

# setup plate, defects and transducers ---------------------------------------------------------------------------------
aluminum = Material(material_type='isotropic', material_name='AluminumAlloy1100')
pic255 = Material(material_type='piezoelectric', material_name='PIC255')

phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS + 1)
pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi)
pos_y = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi)

for i in range(len(phi) - 1):
    phased_array.append(CircularTransducer(position_x=pos_x[i],
                                           position_y=pos_y[i],
                                           diameter=18e-3))

model.plate = IsotropicPlate(material=aluminum, thickness=3e-3, width=PLATE_WIDTH, length=PLATE_WIDTH)
model.defects = [Hole(position_x=20e-3, position_y=25e-3, diameter=10e-3)]
model.transducers = phased_array

# set up the time / loading information --------------------------------------------------------------------------------
# dirac impulses on every transducer
# dirac_impulse = DiracImpulse()
# for i in range(PHASED_ARRAY_N_ELEMENTS):
#     transducer_signals = [None] * len(model.transducers)
#     transducer_signals[i] = dirac_impulse
#     i_step = LoadCase(name='impulse_piezo_{}'.format(i),
#                       duration=3e-3,
#                       transducer_signals=transducer_signals,
#                       output_request='history')
#     model.load_cases.append(i_step)

transducer_signals = [None] * len(model.transducers)
transducer_signals[0] = Burst(center_frequency=50e3, n_cycles=3)
control_step = LoadCase(name='control_step',
                        duration=3e-3,
                        transducer_signals=transducer_signals,
                        output_request='history')
model.load_cases.append(control_step)

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    model.setup_in_abaqus()
