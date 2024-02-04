from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 0.2
PLATE_LENGTH = 0.2
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 4
PHASED_ARRAY_RADIUS = 0.25 * PLATE_WIDTH


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters ----------------------------------------------------------------------------------
        self.max_frequency = 300e3
        self.elements_per_wavelength = 8
        self.elements_in_thickness_direction = 2
        self.model_approach = 'point_force'

        # setup plate, defects and transducers -------------------------------------------------------------------------
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')

        phased_array = []
        phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS)
        pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi[0:-1])
        pos_y = PLATE_LENGTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi[0:-1])
        position_z_values = ['top', 'bottom', 'symmetric', 'asymmetric']

        for i, (x, y) in enumerate(zip(pos_x, pos_y)):
            phased_array.append(CircularTransducer(position_x=x,
                                                   position_y=y,
                                                   position_z=position_z_values[i % 4],
                                                   diameter=16e-3))

        self.plate = IsotropicRectangularPlate(material=aluminum,
                                               thickness=3e-3,
                                               width=PLATE_WIDTH,
                                               length=PLATE_LENGTH)

        self.defects = [Crack(position_x=2e-2, position_y=4e-2, length=10e-3, angle_degrees=0),
                        Hole(position_x=15e-2, position_y=3e-2, diameter=12e-3)]
        self.transducers = phased_array

        # set up the time / loading information ------------------------------------------------------------------------
        burst = Burst(center_frequency=200e3, n_cycles=3)
        transducer_signals = [burst, None, None, None]
        control_step_0 = LoadCase(name='burst_td0',
                                  duration=0.1e-3,
                                  transducer_signals=transducer_signals,
                                  output_request='history')

        transducer_signals = [None, burst, None, None]
        control_step_1 = LoadCase(name='burst_td0',
                                  duration=0.1e-3,
                                  transducer_signals=transducer_signals,
                                  output_request='history')
        self.load_cases = [control_step_0, control_step_1]

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Model().setup_in_abaqus()
