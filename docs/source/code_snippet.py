from guwlib import *
import numpy as np

PLATE_WIDTH = 0.2
PLATE_LENGTH = 0.2
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 7
PHASED_ARRAY_RADIUS = 0.25 * PLATE_WIDTH


class SimpleModel(FEModel):
    def setup_parameters(self):
        self.max_frequency = 300e3
        self.elements_per_wavelength = 20
        self.elements_in_thickness_direction = 1
        self.model_approach = 'point_force'
