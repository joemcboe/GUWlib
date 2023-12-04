import sys
import inspect
import os


class FEModel:
    """

    """

    def __init__(self):
        """

        """
        # attributes
        self.plate = None
        self.transducers = []
        self.defects = []
        self.load_cases = []

        # simulation parameters
        self.max_frequency = None
        self.elements_per_wavelength = 20
        self.elements_in_thickness_direction = 4
        self.courant_number = 0.1
        self.model_approach = 'point_force'

        # other parameters
        input_file_name = os.path.basename(inspect.getouterframes(inspect.currentframe())[1][1])
        self.input_file_name = os.path.splitext(input_file_name)[0]
        self.no_gui_mode = any(arg == "-noGUI" for arg in sys.argv)

    def setup_in_abaqus(self):
        """
        Checks the model for inconsistencies and calls an appropriate function to implement the model in Abaqus.
        :return:
        """

        self.check_model()

        if self.model_approach == 'piezo_electric':
            from guwlib.functions_cae.build_abaqus_model_piezo_electric import build_abaqus_model_piezo_electric
            build_abaqus_model_piezo_electric(model=self)

        if self.model_approach == 'point_force':
            from guwlib.functions_cae.build_abaqus_model_point_force import build_abaqus_model_point_force
            build_abaqus_model_point_force(model=self)

    def generate_report(self):
        """
        Generates a visual representation of the model and an easy-to-read summary of its parameters as a Latex file.
        :return:
        """
        pass

    def check_model(self):
        """

        :return:
        """
        if self.courant_number <= 0 or self.courant_number > 1.0:
            self.courant_number = 0.1

        self.adjust_max_frequency()

    def adjust_max_frequency(self):
        pass

    def get_element_size_thickness(self):
        """
        Compute the required element size thickness direction of the plate.
        :return:
        """
        element_size_thickness = self.plate.thickness / self.elements_in_thickness_direction
        return element_size_thickness

    def get_element_size_in_plane(self):
        """
        Compute the required in-plane element size of the plate.
        :return:
        """
        from guwlib.functions_utility.dispersion import get_minimal_lamb_wavelength
        frequency_range = [0, self.max_frequency]
        min_wavelength, min_wavelength_frequency = get_minimal_lamb_wavelength(material=self.plate.material,
                                                                               thickness=self.plate.thickness,
                                                                               frequency_range=frequency_range)
        element_size_in_plane = min_wavelength / self.elements_per_wavelength
        return element_size_in_plane

    def get_max_time_increment(self):
        """
        Compute the maximal time increment according to the CFL condition with the desired courant number.
        :return:
        """
        max_time_increment = self.courant_number / (self.elements_per_wavelength * self.max_frequency)
        return max_time_increment