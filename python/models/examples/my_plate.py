from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 10e-2
PLATE_LENGTH = 10e-2
PLATE_THICKNESS = 5e-3


class SimpleModel(FEModel):
    def setup_parameters(self):
        # basic simulation parameters ----------------------------------------------------------------------------------
        self.max_frequency = 50e3
        self.elements_per_wavelength = 10
        self.elements_in_thickness_direction = 4
        self.model_approach = 'point_force'

        # setup plate, defects and transducers -------------------------------------------------------------------------
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')

        self.defects = [Crack(position_x=0.6*PLATE_WIDTH,
                              position_y=0.6*PLATE_LENGTH,
                              length=0.4*PLATE_WIDTH,
                              angle_degrees=35)]

        # Hole(position_x=0.4 * PLATE_WIDTH, position_y=0.6 * PLATE_LENGTH,
        #                              diameter=3*PLATE_THICKNESS),

        # for i, (x, y) in enumerate(zip(pos_x, pos_y)):
        #     phased_array.append(CircularTransducer(position_x=x,
        #                                            position_y=y,
        #                                            position_z=position_z_values[i % 4],
        #                                            diameter=16e-3))

        self.plate = IsotropicRectangularPlate(material=aluminum,
                                               thickness=3e-3,
                                               width=PLATE_WIDTH,
                                               length=PLATE_LENGTH)

        # self.defects = [Crack(position_x=2e-2, position_y=4e-2, length=10e-3, angle_degrees=0),
        #                 Hole(position_x=15e-2, position_y=3e-2, diameter=12e-3)]
        # self.transducers = phased_array


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    SimpleModel().setup_in_abaqus()
