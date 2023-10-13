# -*- coding: utf-8 -*-
from .abaqus_utility_functions import *
from .disperse import *
from .output import *
import numpy as np


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

    def __init__(self, plate=None, excitation=None, propagation_distance=0.2, nodes_per_wavelength=6,
                 elements_in_thickness_direction=4):
        self.excitation = excitation  # maybe change so that  multiple excitations are possible, similar to defect array
        self.plate = plate
        self.propagation_distance = propagation_distance
        self.nodes_per_wavelength = nodes_per_wavelength
        self.elements_in_thickness_direction = elements_in_thickness_direction

    def setup_in_abaqus(self):

        # geometry
        create_plate(plate=self.plate)
        log_info("Created plate geometry.")
        for defect in self.plate.defects:
            if defect["type"] == "hole":
                pass
                # add_circular_hole_to_plate(plate=self.plate,
                #                            circle_pos_x=defect["position"][0],
                #                            circle_pos_y=defect["position"][1],
                #                            circle_radius=defect["radius"],
                #                            guideline_option=defect["guideline_option"])
            if defect["type"] == "crack":
                pass
        log_info("Added " + str(len(self.plate.defects)) + " defect(s).")



        # for i in range(len(phi)-1):
        #     create_piezo_element(plate=self.plate, piezo_pos_x=pos_x[i], piezo_pos_y=pos_y[i], piezo_radius=8e-3,
        #                          piezo_thickness=2e-4,
        #                          piezo_id=i)

        # # add vertices to add excitations
        # pos_x, pos_y, pos_z = self.excitation.coordinates
        # add_vertex_to_plate(pos_x=pos_x, pos_y=pos_y)

        # hide datums
        make_datums_invisible()

        # # create and assign material
        # assign_material(self.plate.material)
        # log_info("Material (" + self.plate.material + ") created and assigned to plate.")
        #
        # mesh the part
        max_exciting_frequency = self.excitation.signal.get_max_contained_frequency()
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

        mesh_part(element_size=element_size)

        # create assembly and instantiate the plate
        create_assembly_instantiate_plate()
        log_info("Plate instantiated in new assembly")

        # add dynamic explicit step
        max_time_increment_condition_1 = (0.5 / ((self.nodes_per_wavelength - 1) * max_exciting_frequency))
        max_time_increment_condition_2 = 1 / max_exciting_frequency
        max_time_increment = min(max_time_increment_condition_1, max_time_increment_condition_2)
        wavelengths_carrier = get_lamb_wavelength(material=self.plate.material,
                                                  thickness=self.plate.thickness,
                                                  frequency=self.excitation.signal.carrier_frequency)
        min_wavelength = min(min(wavelengths_carrier[0]), min(wavelengths_carrier[1]))
        min_phase_velocity = min_wavelength * self.excitation.signal.carrier_frequency
        simulation_duration = self.propagation_distance / min_phase_velocity
        create_step_dynamic_explicit(time_period=simulation_duration, max_increment=max_time_increment)
        info_str = ("Abaqus/Explicit time increment\n" +
                    "total sim duration: {:.2f}e-3 s\n".format(simulation_duration * 1e3) +
                    "max time increment: {:.2f}e-6 s\n".format(max_time_increment * 1e6) +
                    "min steps needed:   {:d} steps".format(int(simulation_duration / max_time_increment)))
        log_info(info_str)

        # # add point force with tabular amplitude data
        # pos_x, pos_y, pos_z = self.excitation.coordinates
        # add_amplitude(signal=self.excitation.signal, excitation_id=1, max_time_increment=max_time_increment)
        # add_concentrated_force(pos_x=pos_x, pos_y=pos_y, pos_z=pos_z, amplitude=1e2, excitation_id=1)

    # ------------------------------------------------------------------------------------------------------------------
    # WARNING: deprecated methods
    def generate_geometry(self):
        # WARNING: deprecated
        create_plate(plate=self.plate)
        for defect in self.plate.defects:
            if defect["type"] == "hole":
                add_circular_hole_to_plate(plate=self.plate,
                                           circle_pos_x=defect["position"][0],
                                           circle_pos_y=defect["position"][1],
                                           circle_radius=defect["radius"],
                                           guideline_option=defect["guideline_option"])
            if defect["type"] == "crack":
                pass
        make_datums_invisible()

    def generate_mesh(self):
        # WARNING: deprecated
        mesh_part(element_size=self.element_size)

    # def take_screenshot(self):
    #     i = 0
    #     for defect in self.plate.defects:
    #         if defect["type"] == "hole":
    #             circle_pos_x = defect["position"][0]
    #             circle_pos_y = defect["position"][1]
    #             save_viewport_to_png(center_x=circle_pos_x,
    #                                  center_y=circle_pos_y)
    #             i = i + 1
