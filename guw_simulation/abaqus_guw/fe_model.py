# -*- coding: utf-8 -*-
from .abaqus_utility_functions import *
from .disperse import *
from .output import *
from abaqus_guw.defect import *
import numpy as np

DEFAULT_MAX_FREQUENCY = 50e3


class FEModel:
    """
    A class representing an Abaqus FE model for the simulation of GUW and interaction with defects.

    Instances of this class bundle attributes (main components of the FE model) and methods (geometry generation, mesh
    generation, utility functions) related to the FE model for GUW simulation.

    TODO: add description
    """

    def __init__(self, plate, defects=None, phased_array=None, steps=None,
                 model_approach='point_force',
                 max_frequency=None, nodes_per_wavelength=10, elements_in_thickness_direction=4):

        if defects is None:
            defects = []

        # spatial properties (part, property, mesh, assembly module)
        self.plate = plate
        self.defects = defects
        self.phased_array = phased_array

        # time and loading properties (step, load, job module)
        self.steps = steps

        # modelling approach
        self.model_approach = model_approach

        # mesh properties
        self.max_frequency = max_frequency  # optional
        self.nodes_per_wavelength = nodes_per_wavelength
        self.elements_in_thickness_direction = elements_in_thickness_direction

    # public methods
    def setup_in_abaqus(self):

        num_nodes = None

        # PART MODULE --------------------------------------------------------------------------------------------------
        if self.model_approach == 'point_force':
            # plate geometry
            create_plate(plate=self.plate)
            log_info("Created plate geometry: {}".format(self.plate.description))

            # defects geometry
            log_txt = ""
            for i, defect in enumerate(self.defects):
                if isinstance(defect, Hole):
                    defect.id = i
                    create_circular_hole_in_plate(plate=self.plate, hole=defect)
                    log_txt = "{}\n{:g}-mm circular hole at ({:g},{:g}) mm".format(log_txt,
                                                                             defect.radius*1e3,
                                                                             defect.position_x*1e3,
                                                                             defect.position_y*1e3)
                if isinstance(defect, Crack):
                    pass
                    # TODO

            log_info("Added {} defect(s):\n{}".format(len(self.defects), log_txt))

            # piezo geometry
            for i, piezo in enumerate(self.phased_array):
                piezo.id = i
                create_piezo_as_point_load(plate=self.plate, piezo_element=piezo)

            log_info("Added " + str(len(self.phased_array)) + " point forces, representing the piezoelectric"
                                                              " transducers.")

        if self.model_approach == 'piezoelectric':
            # plate geometry
            # defects geometry
            # piezo geometry
            pass

        # PROPERTY MODULE ----------------------------------------------------------------------------------------------
        if self.model_approach == 'point_force':
            create_material(self.plate.material)
            assign_material(set_name=self.plate.set_name, material=self.plate.material)

        if self.model_approach == 'piezoelectric':
            # create all materials needed
            materials = set()
            materials.add(self.plate.material)
            for piezo in self.phased_array:
                materials.add(piezo.material)
            for material in materials:
                create_material(material)
                log_info("Material ({}) created.".format(material))

            # assign all materials
            assign_material(set_name=self.plate.set_name, material=self.plate.material)
            for piezo in self.phased_array:
                assign_material(set_name=piezo.set_name, material=piezo.material)

        # MESH MODULE --------------------------------------------------------------------------------------------------
        max_exciting_frequency = self.determine_max_simulation_frequency()
        wavelengths = get_lamb_wavelength(material=self.plate.material,
                                          thickness=self.plate.thickness,
                                          frequency=max_exciting_frequency)
        min_wavelength = min(min(wavelengths[0]), min(wavelengths[1]))
        element_size_nodes_per_wavelength = min_wavelength / (self.nodes_per_wavelength - 1)
        element_size_thickness = self.plate.thickness / self.elements_in_thickness_direction
        element_size = min(element_size_thickness, element_size_nodes_per_wavelength)

        log_info("Element size set to {:.2e} m.\n"
                 "(Max exciting frequency:   {:.2f} kHz\n"
                 " For {:.0f} nodes per wavelength:   max element size: {:.2e} m\n"
                 " For {:.0f} elements per thickness: max element size: {:.2e} m"
                 "".format(element_size, max_exciting_frequency * 1e-3, self.nodes_per_wavelength,
                           element_size_nodes_per_wavelength, self.elements_in_thickness_direction,
                           element_size_thickness))

        if self.model_approach == 'point_force':
            pass
            # num_nodes = mesh_part(element_size=element_size, phased_array=self.phased_array)

        # ASSEMBLY MODULE ----------------------------------------------------------------------------------------------
        # create assembly and instantiate the plate
        if self.model_approach == 'point_force':
            create_assembly_instantiate_part()
            log_info("Plate instantiated in new assembly")

        # STEP MODULE --------------------------------------------------------------------------------------------------
        pass
        # if mode == 'time_domain':
        #     # add dynamic explicit step
        #     max_time_increment_condition_1 = (0.5 / ((self.nodes_per_wavelength - 1) * max_exciting_frequency))
        #     max_time_increment_condition_2 = 1 / max_exciting_frequency
        #     max_time_increment = min(max_time_increment_condition_1, max_time_increment_condition_2)
        #     wavelengths = get_lamb_wavelength(material=self.plate.material,
        #                                       thickness=self.plate.thickness,
        #                                       frequency=max_exciting_frequency)
        #     min_wavelength = min(min(wavelengths[0]), min(wavelengths[1]))
        #     min_phase_velocity = min_wavelength * max_exciting_frequency
        #     simulation_duration = self.propagation_distance / min_phase_velocity
        #     create_step_dynamic_explicit(time_period=simulation_duration, max_increment=max_time_increment)
        #     info_str = ("Abaqus/Explicit time increment\n" +
        #                 "total sim duration: {:.5e} s\n".format(simulation_duration) +
        #                 "max time increment: {:.2e} s\n".format(max_time_increment) +
        #                 "min steps needed:   {:d} steps".format(int(simulation_duration / max_time_increment)))
        #     log_info(info_str)
        #
        # if mode == 'frequency_domain':
        #     log_error('Frequency domain is not supported yet. No step created.')
        #     pass

        # LOAD MODULE --------------------------------------------------------------------------------------------------

        # if mode == 'time_domain':
        #     for piezo in self.phased_array:
        #         if piezo.signal is not None:
        #             add_piezo_load(piezo, max_time_increment)
        #
        # if mode == 'frequency_domain':
        #     pass

        # # add point force with tabular amplitude data
        # pos_x, pos_y, pos_z = self.excitation.coordinates
        # add_amplitude(signal=self.excitation.signal, excitation_id=1, max_time_increment=max_time_increment)
        # add_concentrated_force(pos_x=pos_x, pos_y=pos_y, pos_z=pos_z, amplitude=1e2, excitation_id=1)

        # DISPLAY OPTIONS ----------------------------------------------------------------------------------------------
        make_datums_invisible()
        # beautify_set_colors(self.phased_array)

        # JOB MODULE ---------------------------------------------------------------------------------------------------

        # LOGGING ------------------------------------------------------------------------------------------------------
        print("DATA: {} nodes,".format(num_nodes))
        # if mode == 'time_domain':
        #     print("DATA: {} nodes, {:.5e} s sim duration, {} nodes per thickness"
        #           ", {} nodes per wavelength".format(num_nodes, simulation_duration,
        #                                              self.nodes_per_wavelength,
        #                                              self.elements_in_thickness_direction))

    def write_input(self):
        pass
        #write_input_file(self.sim_name)

    def determine_max_simulation_frequency(self):

        # read in frequency contents of piezo elements
        max_piezo_frequencies = []
        for piezo in self.phased_array:
            if piezo.signal is not None:
                max_piezo_frequencies.append(piezo.signal.get_max_contained_frequency())

        # determine the max frequency of the simulation
        if not max_piezo_frequencies:
            if self.max_frequency is None:
                log_info("No maximum frequency set and no signals associated with piezo elements of phased array. "
                         "\nSetting the maximum frequency of this simulation to default value "
                         "of {:.2f} kHz.".format(DEFAULT_MAX_FREQUENCY * 1e-3))
                return DEFAULT_MAX_FREQUENCY

            elif self.max_frequency is not None:
                log_info("Setting the maximum frequency of this simulation to the requested "
                         "value of {:.2f} kHz".format(self.max_frequency * 1e-3))
                return self.max_frequency

        if max_piezo_frequencies:
            max_piezo_frequency = max(max_piezo_frequencies)
            if self.max_frequency is None:
                log_info("Setting the maximum frequency of this simulation according to the frequency content of the "
                         "piezo elements to a value of {:.2f} kHz ".format(max_piezo_frequency * 1e-3))
                return max_piezo_frequency

            elif max_piezo_frequency > self.max_frequency:
                log_info("Maximum frequency excited by the piezo elements is {:.2f}, which is higher than the requested"
                         "maximum frequency of {:.2f} kHz.\nSetting the maximum frequency of this simulation to a "
                         "value of {:.2f} kHz.".format(self.max_frequency * 1e-3, max_piezo_frequency * 1e-3,
                                                       max_piezo_frequency * 1e-3, ))
                return max_piezo_frequency

            elif max_piezo_frequency < self.max_frequency:
                log_info("\nSetting the maximum frequency of this simulation to the requested value of {:.2f} kHz.\n"
                         "(This might be an unnecessarily high value since the maximum frequency excited by the piezo "
                         "elements is {:.2f}) kHz".format(self.max_frequency * 1e-3, max_piezo_frequency * 1e-3))
                return self.max_frequency
