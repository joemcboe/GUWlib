"""
The core module of my example project
"""

# -*- coding: utf-8 -*-
from .abaqus_utility_functions import *
from .abaqus_utility_functions_advanced import *
from .disperse import *
from .output import *
from .signals import *
from .defect import *
from .plate import *
from .rectilinear_partitioning import partition_rectangular_plate

DEFAULT_MAX_FREQUENCY = 50e3


class FEModel:
    """
    Represents an Abaqus Finite Element (FE) model for structural analysis.

    This class serves as a container for various components and information needed to set up
    and perform a finite element analysis using Abaqus.

    :param IsotropicPlate plate: The isotropic plate to be analyzed.
    :param list[Hole] defects: List of defects.
    :param list[PiezoElement] phased_array: List of piezo elements for phased array.
    :param list[LoadCase] load_cases: List of load cases.
    :param str model_approach: The modeling approach. Choose from:

        - *'point_force'*: Point force modeling.
        - *'piezo_electric'*: Piezoelectric modeling.

    :param float max_frequency: Maximum frequency for analysis.
    :param int nodes_per_wavelength: Number of nodes per wavelength.
    :param int elements_in_thickness_direction: Number of elements in the thickness direction.
    """

    def __init__(self, plate, defects=None, phased_array=None, load_cases=None, model_approach='point_force',
                 max_frequency=None, nodes_per_wavelength=10, elements_in_thickness_direction=4):

        if defects is None:
            defects = []
        if load_cases is None:
            load_cases = []

        # spatial properties (part, property, mesh, assembly module)
        self.plate = plate
        self.defects = defects
        self.phased_array = phased_array

        # time and loading properties (step, load, job module)
        self.load_cases = load_cases

        # modelling approach ('point_force' vs 'piezoelectric')
        self.model_approach = model_approach

        # mesh properties
        self.max_frequency = max_frequency  # optional
        self.nodes_per_wavelength = nodes_per_wavelength
        self.elements_in_thickness_direction = elements_in_thickness_direction

    # public methods
    def setup_in_abaqus(self):

        # PRELIMINARY --------------------------------------------------------------------------------------------------

        # determine the element size according to CFL condition
        all_signals = [signal for step in self.load_cases for signal in step.piezo_signals]
        max_exciting_frequency, info_string = self.determine_max_signals_frequency(all_signals)
        log_info(info_string)

        wavelengths = get_lamb_wavelength(material=self.plate.material,
                                          thickness=self.plate.thickness,
                                          frequency=max_exciting_frequency)
        min_wavelength = min(min(wavelengths[0]), min(wavelengths[1]))
        element_size_nodes_per_wavelength = min_wavelength / (self.nodes_per_wavelength - 1)
        element_size_thickness = self.plate.thickness / self.elements_in_thickness_direction
        # element_size = min(element_size_thickness, element_size_nodes_per_wavelength)

        log_info("Max exciting frequency:          {:.2f} kHz\n"
                 "Element size, in-plane:          {:.2e} m (for {:.0f} nodes per wavelength)\n"
                 "Element size, through-thickness: {:.2e} m (for {:.0f} elements per thickness)"
                 "".format(max_exciting_frequency * 1e-3,
                           element_size_nodes_per_wavelength, self.nodes_per_wavelength,
                           element_size_thickness, self.elements_in_thickness_direction))

        # create a pristine plate w/o defects or piezo-elements, and obtain a structured mesh for better partitioning
        create_reference_mesh_plate(plate=self.plate, element_size=element_size_nodes_per_wavelength)

        # PART MODULE --------------------------------------------------------------------------------------------------
        # plate geometry
        create_plate(plate=self.plate)
        log_info("Created plate geometry: {}".format(self.plate.description))

        # defects geometry
        bounding_box_list = []
        log_txt = ""
        for i, defect in enumerate(self.defects):
            defect.id = i
            if isinstance(defect, Hole):
                bounding_box = create_circular_hole_in_plate(plate=self.plate, hole=defect,
                                                             element_size=element_size_nodes_per_wavelength)
                bounding_box_list.append(bounding_box)
                log_txt = "{}\n{:g}-mm circular hole at ({:g},{:g}) mm".format(log_txt,
                                                                               defect.radius * 2e3,
                                                                               defect.position_x * 1e3,
                                                                               defect.position_y * 1e3)
            if isinstance(defect, Crack):
                pass
                # TODO

        log_info("Added {} defect(s):\n{}".format(len(self.defects), log_txt))

        # piezo geometry
        if self.model_approach == 'point_force':
            for i, piezo in enumerate(self.phased_array):
                piezo.id = i
                bounding_box = create_piezo_as_point_load(plate=self.plate, piezo_element=piezo,
                                                          element_size=element_size_nodes_per_wavelength)
                bounding_box_list.append(bounding_box)

            log_info("Added " + str(len(self.phased_array)) + " point forces, representing the piezoelectric"
                                                              " transducers.")

        if self.model_approach == 'piezo_electric':
            for i, piezo in enumerate(self.phased_array):
                piezo.id = i
                create_piezo_element(plate=self.plate, piezo_element=piezo)

        # partition the plate into partitions that are suitable for structured meshing
        log_info("Generating a rectilinear partitioning strategy for the plate. This might take some time...")
        cells = partition_rectangular_plate(self.plate, bounding_box_list)
        log_info("Done. Starting to create {:d} rectangular partitions on the plate part.".format(len(cells)))
        err_count = 0
        for i, cell in enumerate(cells[:-1]):
            left, bottom, right, top = (cell[0], cell[1], cell[2], cell[3])
            status, warning = add_rectangular_partition_to_plate(self.plate, left, bottom, right, top)
            err_count += status
        if err_count > 0:
            log_warning("{} partitions could not be created. Probably the target region"
                        " was already rectangular".format(err_count))

        # delete the reference mesh plate
        remove_reference_mesh_plate()

        # PROPERTY MODULE ----------------------------------------------------------------------------------------------
        if self.model_approach == 'point_force':
            create_material(self.plate.material)
            assign_material(set_name=self.plate.material_cell_set_name, material=self.plate.material)

        if self.model_approach == 'piezo_electric':
            pass
            # materials will be assigned after splitting the model for co-simulation

        # MESH MODULE --------------------------------------------------------------------------------------------------
        if self.model_approach == 'point_force':
            num_nodes = mesh_part_point_force_approach(element_size_in_plane=element_size_nodes_per_wavelength,
                                                       element_size_thru_thickness=element_size_thickness,
                                                       phased_array=self.phased_array,
                                                       defects=self.defects)

        if self.model_approach == 'piezo_electric':
            num_nodes = mesh_part_piezo_electric_approach(element_size=element_size_nodes_per_wavelength,
                                                          phased_array=self.phased_array,
                                                          defects=self.defects)
            create_mesh_parts()
            split_mesh_parts(self.plate, self.phased_array)
            create_electric_interface(self.phased_array)

        # ASSEMBLY MODULE ----------------------------------------------------------------------------------------------
        # create assembly and instantiate the plate
        if self.model_approach == 'point_force':
            assemble()
            log_info("Plate instantiated in new assembly")

        if self.model_approach == 'piezo_electric':
            assemble_co_sim()

        # INTERACTION MODULE -------------------------------------------------------------------------------------------
        # split model and create electrical interface
        if self.model_approach == 'piezo_electric':
            split_model_for_co_sim()
            setup_electric_interface(self.phased_array)

        # PROPERTY MODULE ----------------------------------------------------------------------------------------------
        if self.model_approach == 'piezo_electric':
            # create and assign materials in individual models (dielectric materials are not permitted in XPL model)
            create_materials_co_sim(self.plate, self.phased_array)
            assign_material_co_sim(self.plate, self.phased_array)

        # STEP / LOAD / JOB MODULE -------------------------------------------------------------------------------------
        max_time_increment_condition_1 = (0.5 / ((self.nodes_per_wavelength - 1) * max_exciting_frequency))
        max_time_increment_condition_2 = 1 / max_exciting_frequency
        max_time_increment = min(max_time_increment_condition_1, max_time_increment_condition_2)
        info_str = ("Time discretization:\n" +
                    "max time increment: {:.2e} s\n".format(max_time_increment))
        log_info(info_str)

        if self.model_approach == 'point_force':
            for i, step in enumerate(self.load_cases):

                # delete all steps except initial
                remove_all_steps()

                # create new explicit step
                step_name = 'load_case_{}_{}'.format(i, step.name)
                create_step_dynamic_explicit(step_name=step_name,
                                             time_period=step.duration,
                                             max_increment=max_time_increment,
                                             previous_step_name='Initial')

                # create history output request for piezo node sets
                remove_standard_field_output_request()
                if step.output_request == 'history':
                    add_piezo_signal_history_output_request(phased_array=self.phased_array,
                                                            create_step_name=step_name)

                if step.output_request == 'field':
                    add_piezo_signal_history_output_request(phased_array=self.phased_array,
                                                            create_step_name=step_name)
                    add_field_output_request(plate=self.plate, create_step_name=step_name,
                                             time_interval=max_time_increment*40)

                # create all amplitudes and loads
                for j, signal in enumerate(step.piezo_signals):
                    if signal is not None:
                        add_piezo_point_force(load_name='piezo_{}_{}'.format(j, signal.__class__.__name__),
                                              step_name=step_name,
                                              piezo=self.phased_array[j],
                                              signal=signal,
                                              max_time_increment=max_time_increment)

                # write input file for this load case
                # write_input_file(job_name=step_name, num_cpus=1)

                log_info("Created a job definition for the current load case. To run or view this load case,"
                         "please refer to the created input file '{}.inp'. ".format(step_name))

        if self.model_approach == 'piezo_electric':
            for i, step in enumerate(self.load_cases):

                # delete all steps except initial
                remove_all_steps_co_sim()

                # create new steps in explicit and standard models
                step_name = 'load_case_{}_{}'.format(i, step.name)
                create_steps_co_sim(step_name=step_name,
                                    time_period=step.duration,
                                    max_increment=max_time_increment,
                                    previous_step_name='Initial')

                # create co-sim-interaction
                create_interaction_std_xpl_co_sim(plate=self.plate, step_name=step_name)

                # create history output request for piezo node sets
                remove_standard_field_output_request_co_sim()
                if step.output_request == 'history':
                    add_piezo_signal_history_output_request_co_sim(phased_array=self.phased_array,
                                                                   create_step_name=step_name)
                #
                if step.output_request == 'field':
                    add_piezo_signal_history_output_request_co_sim(phased_array=self.phased_array,
                                                                   create_step_name=step_name)
                    add_field_output_request_co_sim(create_step_name=step_name)

                # create all amplitudes and loads
                add_piezo_boundary_conditions_co_sim(step_name, self.phased_array)
                for j, signal in enumerate(step.piezo_signals):
                    if signal is not None:
                        add_piezo_potential_co_sim(load_name='sgn_{}_{}'.format(self.phased_array[j].cell_set_name,
                                                                                signal.__class__.__name__),
                                                   step_name=step_name,
                                                   piezo=self.phased_array[j],
                                                   signal=signal,
                                                   max_time_increment=max_time_increment)

                # # write input file for this load case
                write_input_file(job_name=step_name, num_cpus=4)
                log_info("Created a job definition for the current load case. To run or view this load case,"
                         "please refer to the created input file '{}.inp'. ".format(step_name))

        # DISPLAY OPTIONS ----------------------------------------------------------------------------------------------
        make_datums_invisible()

    def determine_max_signals_frequency(self, signals):
        # read in frequency contents of signals
        max_signal_frequencies = []
        for signal in signals:
            if signal is not None:
                if isinstance(signal, DiracImpulse):
                    pass
                else:
                    max_signal_frequencies.append(signal.get_max_contained_frequency())

        # determine the max frequency of the simulation
        if not max_signal_frequencies:
            if self.max_frequency is None:
                info = ("No maximum frequency set and no signals associated with piezo elements of phased array. "
                        "\nSetting the maximum frequency of this simulation to default value "
                        "of {:.2f} kHz.".format(DEFAULT_MAX_FREQUENCY * 1e-3))
                return DEFAULT_MAX_FREQUENCY, info

            elif self.max_frequency is not None:
                info = ("Setting the maximum frequency of this simulation to the requested "
                        "value of {:.2f} kHz".format(self.max_frequency * 1e-3))
                return self.max_frequency, info

        if max_signal_frequencies:
            max_piezo_frequency = max(max_signal_frequencies)
            if self.max_frequency is None:
                info = ("Setting the maximum frequency of this simulation according to the frequency content of the "
                        "piezo elements to a value of {:.2f} kHz ".format(max_piezo_frequency * 1e-3))
                return max_piezo_frequency, info

            elif max_piezo_frequency > self.max_frequency:
                info = ("Maximum frequency excited by the piezo elements is {:.2f}, which is higher than the requested"
                        "maximum frequency of {:.2f} kHz.\nSetting the maximum frequency of this simulation to a "
                        "value of {:.2f} kHz.".format(max_piezo_frequency * 1e-3, self.max_frequency * 1e-3,
                                                      max_piezo_frequency * 1e-3, ))
                return max_piezo_frequency, info

            elif max_piezo_frequency < self.max_frequency:
                info = ("Setting the maximum frequency of this simulation to the requested value of {:.2f} kHz.\n"
                        "(This might be an unnecessarily high value since the maximum frequency excited by the piezo "
                        "elements is {:.2f}) kHz".format(self.max_frequency * 1e-3, max_piezo_frequency * 1e-3))
                return self.max_frequency, info
