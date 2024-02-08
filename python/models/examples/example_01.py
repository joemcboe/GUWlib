"""
Minimal example from the GitLab readme.md file. This script creates a 200 x 200 x 3 mm plate from 1100 aluminum alloy
with two transducers as well as a crack and a through-thickness hole. A 180 kHz 3-cycle burst is applied on the first
transducer. Field and history output is requested. The model is discretized with 16 elements per wavelength in-plane
and 8 elements per thickness.
"""
from guwlib import *


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters
        self.max_frequency = 300e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')
        self.plate = IsotropicRectangularPlate(material=aluminum, thickness=3e-3, width=200e-3, length=200e-3)

        # setup two transducers
        self.transducers = [
            CircularTransducer(position_x=100e-3, position_y=150e-3, position_z='asymmetric', diameter=16e-3),
            CircularTransducer(position_x=100e-3, position_y=50e-3, position_z='asymmetric', diameter=16e-3)]

        # setup defects
        self.defects = [Crack(position_x=45e-3, position_y=80e-3, length=20e-3, angle_degrees=10),
                        Hole(position_x=155e-3, position_y=105e-3, diameter=12e-3)]

        # set up the time / loading information (burst on 1st transducer)
        burst = Burst(center_frequency=180e3, n_cycles=3)
        transducer_signals = [burst, None]
        self.load_cases = [LoadCase(name='control_step', duration=0.1e-3, transducer_signals=transducer_signals,
                                    output_request='field')]


if __name__ == "__main__":
    Model().setup_in_abaqus()
