"""
Model script from the tutorial in the documentation ("Writing a model script").
"""


from guwlib import *
import numpy as np

PLATE_WIDTH = 400e-3
PLATE_LENGTH = 400e-3
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 9
PHASED_ARRAY_RADIUS = 55e-3


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters ----------------------------------------------------------------------------------
        self.max_frequency = 100e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate, defects and transducers -------------------------------------------------------------------------
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')
        self.plate = IsotropicRectangularPlate(material=aluminum, thickness=PLATE_THICKNESS, width=PLATE_WIDTH,
                                               length=PLATE_LENGTH)

        self.defects = [Crack(position_x=300e-3, position_y=60e-3, length=40e-3, angle_degrees=95),
                        Hole(position_x=250e-3, position_y=320e-3, diameter=20e-3)]

        phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS + 1)
        pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi[0:-1])
        pos_y = PLATE_LENGTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi[0:-1])

        phased_array = []
        for _, (x, y) in enumerate(zip(pos_x, pos_y)):
            phased_array.append(CircularTransducer(position_x=x, position_y=y,
                                                   position_z='asymmetric', diameter=16e-3))

        self.transducers = phased_array

        # setup time / loading information -----------------------------------------------------------------------------
        burst = Burst(center_frequency=50e3, n_cycles=3, window='hanning')
        transducer_signals = [burst, None, None, None, None, None, None, None, None]
        load_case = LoadCase(name='burst_load_case', duration=0.25e-3,
                             transducer_signals=transducer_signals,
                             output_request='field')
        self.load_cases = [load_case]


if __name__ == "__main__":
    Model().setup_in_abaqus()
