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

    Attributes:
        plate (plate): plate in which the GUWs propagate
        excitation (phased_array): array of piezoelectric transducers

    Methods:
         generate_geometry: generates the geometry of the plate with all defects
         generate_mesh: meshes the created parts in Abaqus
    """

    def __init__(self, plate, defects=None, phased_array=None, propagation_distance=0.2, nodes_per_wavelength=10,
                 elements_in_thickness_direction=4, max_frequency=None):

        if defects is None:
            defects = []

        self.plate = plate
        self.defects = defects
        self.phased_array = phased_array
        self.propagation_distance = propagation_distance
        self.nodes_per_wavelength = nodes_per_wavelength
        self.elements_in_thickness_direction = elements_in_thickness_direction
        self.max_frequency = max_frequency

    def setup_in_abaqus(self):

        # PART MODULE --------------------------------------------------------------------------------------------------
        # plate geometry
        create_plate(plate=self.plate)
        log_info("Created plate geometry.")

        # defects geometry
        for defect in self.defects:
            if isinstance(defect, Hole):
                log_warning("Hole not instantiated.")

        log_info("Added " + str(len(self.defects)) + " defect(s).")

        # piezo geometry
        for i in range(len(self.phased_array)):
            piezo = self.phased_array[i]
            piezo.id = i
            create_piezo_element(plate=self.plate, piezo_element=piezo)

        log_info("Added " + str(len(self.phased_array)) + " piezo elements.")

        # PROPERTY MODULE ----------------------------------------------------------------------------------------------
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

        str1 = 'Max exciting frequency:   {:.2f} kHz'.format(max_exciting_frequency / 1e3)
        str2 = 'Min occurring wavelength: {:.2f} mm'.format(min_wavelength * 1e3)
        str3 = 'For {:.0f} nodes per wavelength:   Max element size {:.2e} m'.format(
            self.nodes_per_wavelength, element_size_nodes_per_wavelength)
        str4 = 'For {:.0f} elements per thickness: Max element size: {:.2e} m'.format(
            self.elements_in_thickness_direction, element_size_thickness)
        log_info("Element size set to {:.2e} m.\n{}\n{}\n{}\n{}".format(element_size, str1, str2, str3, str4))

        mesh_part(element_size=element_size, phased_array=self.phased_array)

        # ASSEMBLY MODULE ----------------------------------------------------------------------------------------------
        # create assembly and instantiate the plate
        create_assembly_instantiate_part()
        log_info("Plate instantiated in new assembly")

        # STEP MODULE --------------------------------------------------------------------------------------------------
        # add dynamic explicit step
        max_time_increment_condition_1 = (0.5 / ((self.nodes_per_wavelength - 1) * max_exciting_frequency))
        max_time_increment_condition_2 = 1 / max_exciting_frequency
        max_time_increment = min(max_time_increment_condition_1, max_time_increment_condition_2)
        wavelengths = get_lamb_wavelength(material=self.plate.material,
                                          thickness=self.plate.thickness,
                                          frequency=max_exciting_frequency)
        min_wavelength = min(min(wavelengths[0]), min(wavelengths[1]))
        min_phase_velocity = min_wavelength * max_exciting_frequency
        simulation_duration = self.propagation_distance / min_phase_velocity
        create_step_dynamic_explicit(time_period=simulation_duration, max_increment=max_time_increment)
        info_str = ("Abaqus/Explicit time increment\n" +
                    "total sim duration: {:.2f}e-3 s\n".format(simulation_duration * 1e3) +
                    "max time increment: {:.2f}e-6 s\n".format(max_time_increment * 1e6) +
                    "min steps needed:   {:d} steps".format(int(simulation_duration / max_time_increment)))
        log_info(info_str)

        # LOAD MODULE --------------------------------------------------------------------------------------------------
        # # add point force with tabular amplitude data
        # pos_x, pos_y, pos_z = self.excitation.coordinates
        # add_amplitude(signal=self.excitation.signal, excitation_id=1, max_time_increment=max_time_increment)
        # add_concentrated_force(pos_x=pos_x, pos_y=pos_y, pos_z=pos_z, amplitude=1e2, excitation_id=1)

        # DISPLAY OPTIONS ----------------------------------------------------------------------------------------------
        make_datums_invisible()
        # beautify_set_colors(self.phased_array)

        # JOB MODULE ---------------------------------------------------------------------------------------------------

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

            elif max_piezo_frecuency > self.max_frequency:
                log_info("Maximum frequency excited by the piezo elements is {:.2f}, which is higher than the requested"
                         "maximum frequency of {:.2f} kHz.\nSetting the maximum frequency of this simulation to a "
                         "value of {:.2f} kHz.".format(self.max_frequency * 1e-3, max_piezo_frequency * 1e-3,
                                                       max_piezo_frequency * 1e-3, ))
                return max_piezo_frequency

            elif max_piezo_frecuency < self.max_frequency:
                log_info("\nSetting the maximum frequency of this simulation to the requested value of {:.2f} kHz.\n"
                         "(This might be an unnecessarily high value since the maximum frequency excited by the piezo "
                         "elements is {:.2f}) kHz".format(self.max_frequency * 1e-3, max_piezo_frequency * 1e-3))
                return self.max_frequency
