"""
Minimal example from the GitLab readme.md file. This script creates a 100 x 100 x 3 mm plate from 1100 aluminum alloy
with two transducers as well as a crack and a through-thickness hole. A 100 kHz 3-cycle burst is applied on the first
transducer. Field and history output is requested. The model is discretized with 16 elements per wavelength in-plane
and 8 elements per thickness.
"""
from guwlib import *


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters
        self.max_frequency = 100e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')
        self.plate = IsotropicRectangularPlate(material=aluminum, thickness=3e-3, width=100e-3, length=100e-3)

        # setup two transducers
        self.transducers = [
            CircularTransducer(position_x=20e-3, position_y=50e-3, position_z='symmetric', diameter=16e-3),
            CircularTransducer(position_x=80e-3, position_y=50e-3, position_z='symmetric', diameter=16e-3)]

        # setup defects
        self.defects = [Crack(position_x=50e-3, position_y=75e-3, length=15e-3, angle_degrees=12),
                        Hole(position_x=60e-3, position_y=30e-3, diameter=8e-3)]

        # set up the time / loading information (burst on 1st transducer)
        burst = Burst(center_frequency=100e3, n_cycles=3)
        transducer_signals = [burst, None]
        self.load_cases = [LoadCase(name='control_step', duration=0.25e-3, transducer_signals=transducer_signals,
                                    output_request='field')]


if __name__ == "__main__":
    Model().setup_in_abaqus()
