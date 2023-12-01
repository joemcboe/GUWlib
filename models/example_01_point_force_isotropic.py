"""
Input file for guwlib.

"""
from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 0.2
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 9
PHASED_ARRAY_RADIUS = 50e-3

# basic simulation parameters ------------------------------------------------------------------------------------------
model = FEModel()
model.max_frequency = 100e3
model.elements_per_wavelength = 20
model.elements_in_thickness_direction = 4
model.model_approach = 'point_force'

# setup plate, defects and transducers ---------------------------------------------------------------------------------
aluminum = Material(material_type='isotropic', material_name='AluminumAlloy1100')
pic255 = Material(material_type='piezoelectric', material_name='PIC255')

model.plate = IsotropicPlate(material=aluminum,
                             thickness=3e-3,
                             width=PLATE_WIDTH,
                             length=PLATE_WIDTH)

model.defects = [Hole(position_x=20e-3, position_y=50e-3, diameter=5e-3)]

phased_array = []
phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS + 1)
pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi)
pos_y = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi)

for i in range(len(phi) - 1):
    phased_array.append(CircularTransducer(position_x=pos_x[i],
                                           position_y=pos_y[i],
                                           diameter=18e-3,
                                           thickness=0.2e-3,
                                           material='pic255',
                                           electrode_thickness=1e-4,
                                           electrode_material='silver'))
model.transducers = phased_array

# set up the time / loading information --------------------------------------------------------------------------------
dirac_impulse = DiracImpulse()
for i in range(PHASED_ARRAY_N_ELEMENTS):
    piezo_signals = [None] * len(model.transducers)
    piezo_signals[i] = dirac_impulse
    i_step = LoadCase(name='impulse_piezo_{}'.format(i),
                      duration=3e-3,
                      transducer_signals=piezo_signals,
                      output_request='history')
    model.load_cases.append(i_step)
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    model.setup_in_abaqus()
