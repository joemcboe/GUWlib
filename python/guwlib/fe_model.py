import sys
import inspect
import os
import shutil
from datetime import datetime


class FEModel:
    """
    Abstract class, acting as a container for simulation parameters (e.g. discretization level) as well as spatial and
    time/loading data (e.g. plate, defects, transducers, excitation signals).

    To create a valid GUWlib model, you have to instantiate an :class:`FEModel` object in your python script. Override
    its :meth:`setup_parameters` method to define your simulation by setting its variables. To set the model up in
    ABAQUS/CAE, call its :meth:`setup_in_abaqus` method. See models/examples for reference.

    :ivar IsotropicPlate plate: Plate of the FE model
    :ivar List[CircularTransducer] transducers: A list with the transducers applied to the plate
    :ivar List[Defect] defects: A list with the defects (cracks, holes, ...) of the plate
    :ivar List[LoadCase] load_cases: A list with loadcases for the simulation
    :ivar Float max_frequency: Specifies the maximum frequency up to which the plate will be excited
    :ivar Int elements_per_wavelength: Number of elements that shall be used for discretization per one wavelength
        (smallest wavelength in range [0, max_frequency] that occurs in the plate, according to the dispersion data of
        the material), Default: 16
    :ivar Int elements_in_thickness_direction: Number of elements that shall be used for discretization along the
        thickness direction of the plate, Default: 8
    :ivar Float courant_number: Used for the computation of the maximum time increment according to CFL condition,
        Default: 0.5
    :ivar String model_approach: Specifies which script shall be used to build the FE model in ABAQUS/CAE, either
        'point_force' or 'piezo_electric'
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
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.courant_number = 0.5
        self.model_approach = 'point_force'

        # other parameters
        input_file_path = inspect.getouterframes(inspect.currentframe())[1][1]
        input_file_name = os.path.basename(input_file_path)
        self.input_file_name = os.path.splitext(input_file_name)[0]
        self.input_file_path = input_file_path
        self.output_directory = os.path.join('results', self.input_file_name)
        self.no_gui_mode = any(arg == "-noGUI" for arg in sys.argv)

    # @abstractmethod
    def setup_parameters(self):
        """
        Abstract method to be overridden in inherent classes to set up the models parameters.

        :return: None
        """
        pass

    def setup_in_abaqus(self):
        """
        Calls the function that creates the FE model in ABAQUS/CAE, depending on the model_approach attribute.
        A basic check for inconsistencies in the model definition is performed beforehand.

        :return: None
        """

        self.setup_parameters()
        self.__check_model()

        if self.no_gui_mode:
            self.__make_output_directory()

        if self.model_approach == 'piezo_electric':
            from guwlib.functions_cae.build_abaqus_model_piezo_electric import build_abaqus_model_piezo_electric
            build_abaqus_model_piezo_electric(model=self)

        if self.model_approach == 'point_force':
            from guwlib.functions_cae.build_abaqus_model_point_force import build_abaqus_model_point_force
            build_abaqus_model_point_force(model=self)

    def generate_report(self):
        """
        Generates a visual representation of the model and an easy-to-read summary of its parameters as a Latex file.

        :return: None
        """
        pass

    def get_element_size_thickness(self):
        """
        Compute the required element size in thickness direction of the plate.

        :return: (Float) Element size used for in-thickness discretization of the plate.
        """
        element_size_thickness = self.plate.thickness / self.elements_in_thickness_direction
        return element_size_thickness

    def get_element_size_in_plane(self):
        """
        Compute the required in-plane element size of the plate, based on the minimal wavelength
        occurring in the range [0, :attr:`max_frequency`].

        :return: (Float) Element size used for in-plane discretization of the plate.
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
        Computes the maximal time increment according to the CFL condition with the desired courant number.

        :return: (Float) Maximum time increment used for time integration in ABAQUS/Explicit.
        """
        max_time_increment = self.courant_number / (self.elements_per_wavelength * self.max_frequency)
        return max_time_increment

    def __check_model(self):
        """

        :return:
        """
        if self.courant_number <= 0 or self.courant_number > 1.0:
            self.courant_number = 0.5

    def __make_output_directory(self):
        if os.path.exists(self.output_directory):
            # Archive the existing directory by renaming it with a timestamp
            timestamp = datetime.now().strftime("%d_%m_%y_%H-%M")
            archived_directory = "{}_archived_{}".format(self.output_directory, timestamp)
            os.rename(self.output_directory, archived_directory)

        # Create the output directory
        os.makedirs(self.output_directory)

        # Copy the model file to the output directory
        src = self.input_file_path
        dst = os.path.join(self.output_directory, self.input_file_name + '.mdl')
        shutil.copy(src, dst)


