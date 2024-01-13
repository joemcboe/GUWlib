from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 1.0
PLATE_LENGTH = 1.0
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 9
PHASED_ARRAY_RADIUS = 55e-3


class MyModel(FEModel):
    def setup_parameters(self):
        # basic simulation parameters ----------------------------------------------------------------------------------
        self.max_frequency = 300e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate, defects and transducers -------------------------------------------------------------------------
        aluminum = Material(material_type='isotropic', material_name='AluminumAlloy1100')

        self.plate = IsotropicRectangularPlate(material=aluminum,
                                               thickness=3e-3,
                                               width=PLATE_WIDTH,
                                               length=PLATE_LENGTH)

        phased_array = []
        phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS + 1)
        pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi[0:-1])
        pos_y = PLATE_LENGTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi[0:-1])

        for i, (x, y) in enumerate(zip(pos_x, pos_y)):
            phased_array.append(CircularTransducer(position_x=x,
                                                   position_y=y,
                                                   position_z='asymmetric',
                                                   diameter=16e-3))

        self.defects = []
        self.transducers = phased_array

        # set up the time / loading information ------------------------------------------------------------------------

        # add load cases: dirac impulses on every transducer
        dirac_impulse = DiracImpulse()
        for i in range(PHASED_ARRAY_N_ELEMENTS):
            transducer_signals = [None] * len(self.transducers)
            transducer_signals[i] = dirac_impulse
            i_step = LoadCase(name='impls_pzt_{}'.format(i),
                              duration=2e-3,
                              transducer_signals=transducer_signals,
                              output_request='history')
            self.load_cases.append(i_step)

        # add one additional control step
        burst = Burst(center_frequency=220e3, n_cycles=3)
        transducer_signals = [None] * len(self.transducers)
        transducer_signals[0] = burst
        control_step = LoadCase(name='control',
                                duration=2e-3,
                                transducer_signals=transducer_signals,
                                output_request='history')
        self.load_cases.append(control_step)


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    MyModel().setup_in_abaqus()
