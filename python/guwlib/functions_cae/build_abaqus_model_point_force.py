from guwlib import *
from guwlib.functions_utility.rectilinear_partitioning import partition_rectangular_plate
from guwlib.functions_utility.console_output import *
from guwlib.functions_cae.helper_functions_point_force import *


def build_abaqus_model_point_force(model):
    """
    Performs the modelling of the FE model in ABAQUS/CAE. Transducers are modelled as point forces (single nodes). The
    resulting ABAQUS simulation is purely explicit (ABAQUS/EXPLICIT).

    The modelling process is divided into the following steps:

    - Create two identical plates with the desired size as parts. Mesh the 2nd plate directly and use the resulting
      structured mesh as a reference mesh when creating partitions around defects and transducers in the 1st plate.
    - Add all defects and transducers to the plate by modifying the plates' geometry. Create rectangular partitions
      around the defects and store relevant geometry features in ABAQUS sets.
    - Generate a rectilinear partitioning pattern to subdivide the remaining plate (around defects) into purely
      rectangular (cuboid) cells to allow structured meshing.
    - Create and assign the plates' material.
    - Mesh the plate with the desired elements per wavelength / thickness. Remove the reference plate.
    - Assemble the model by instantiating the plate part in a new assembly.
    - Assign seams (node-separation) at the cracks locations in ABAQUS' interaction module.
    - Create dynamic/explicit steps, amplitudes, concentrated forces and output requests for each defined load case.
    - Trigger .INP file generation, if the script is run in noGUI mode.

    :param FEModel model: The FEModel instance to set up in ABAQUS/CAE.
    :return: None
    """

    # TIME AND SPACE DISCRETIZATION ------------------------------------------------------------------------------------
    element_size_in_plane = model.get_element_size_in_plane()
    element_size_thickness = model.get_element_size_thickness()
    max_time_increment = model.get_max_time_increment()

    log_info("Element size, in-plane:          {:.2e} m (for {:.0f} elements per wavelength)\n"
             "Element size, through-thickness: {:.2e} m (for {:.0f} elements per thickness)\n"
             "Max. time increment:             {:.2e} s (for a Courant number of {:.2f})"
             "".format(element_size_in_plane, model.elements_per_wavelength,
                       element_size_thickness, model.elements_in_thickness_direction,
                       max_time_increment, model.courant_number))

    # PART MODULE ------------------------------------------------------------------------------------------------------
    # create the plate as a part in abaqus
    create_isotropic_rectangular_plate_part(model.plate)
    log_info("Created plate geometry: {}".format(model.plate.description))

    # create a pristine plate w/o defects or piezo-elements, and obtain a structured mesh for better partitioning
    create_reference_mesh_plate_part(plate=model.plate, element_size=element_size_in_plane)

    # create the defects geometry
    bounding_box_list = []
    log_txt = ""
    for i, defect in enumerate(model.defects):
        defect.set_identifiers(unique_id=i + 1)
        if isinstance(defect, Hole):
            bounding_box = create_circular_hole_in_plate(plate=model.plate,
                                                         hole=defect,
                                                         element_size=element_size_in_plane)
            bounding_box_list.append(bounding_box)
        if isinstance(defect, Crack):
            bounding_box = create_crack_in_plate(plate=model.plate,
                                                 crack=defect,
                                                 element_size=element_size_in_plane)
            bounding_box_list.append(bounding_box)

    log_info("Added {} defect(s):\n{}".format(len(model.defects), log_txt))

    # create the transducer geometry
    for i, transducer in enumerate(model.transducers):
        if isinstance(transducer, CircularTransducer):
            transducer.set_identifiers(unique_id=i + 1)
            bounding_box = create_transducer_as_vertex_on_plate(plate=model.plate, transducer=transducer,
                                                                element_size=element_size_in_plane)
            bounding_box_list.append(bounding_box)
        else:
            raise NotImplementedError("Transducer of type {} not implemented.".format(type(transducer)))

    log_info("Added " + str(len(model.transducers)) + " nodes, representing the piezoelectric transducers.")

    # partition the plate into partitions that are suitable for structured meshing
    log_info("Generating a rectilinear partitioning strategy for the plate. This might take some time...")
    cells = partition_rectangular_plate(model.plate, bounding_box_list)
    log_info("Done. Starting to create {:d} rectangular partitions on the plate part.".format(len(cells)))
    err_count = 0
    for i, cell in enumerate(cells[:-1]):
        left, bottom, right, top = (cell[0], cell[1], cell[2], cell[3])
        status, warning = add_rectangular_cell_partition_to_plate(model.plate,
                                                                  (left, bottom),
                                                                  (right, top))
        err_count += status
    if err_count > 0:
        log_warning("{} partitions could not be created. Probably the target region"
                    " was already rectangular.".format(err_count))

    # PROPERTY MODULE --------------------------------------------------------------------------------------------------
    create_isotropic_material(model.plate.material)
    assign_material(set_name=model.plate.material_cell_set_name, material=model.plate.material)

    # MESH MODULE ------------------------------------------------------------------------------------------------------
    num_nodes = mesh_part(element_size_in_plane=element_size_in_plane,
                          element_size_thickness=element_size_thickness,
                          plate=model.plate,
                          transducers=model.transducers,
                          defects=model.defects)
    log_info("The FE model has {} nodes.".format('{:,d}'.format(num_nodes).replace(',', ' ')))

    # delete the reference mesh plate
    remove_reference_mesh_plate_part()

    # ASSEMBLY MODULE --------------------------------------------------------------------------------------------------
    assemble()
    log_info("Plate instantiated in new assembly.")

    # INTERACTION MODULE -----------------------------------------------------------------------------------------------
    seam_count = 0
    for defect in enumerate(model.defects):
        if isinstance(defect, Crack):
            assign_seam(defect)
            seam_count += 1
            log_info("Assigned seams to {:d} cracks.".format(seam_count))

    # STEP / LOAD / JOB MODULE -----------------------------------------------------------------------------------------
    for i, step in enumerate(model.load_cases):

        # delete all steps except initial
        remove_all_steps()

        # create new explicit step
        step_name = 'lc_{}_{}'.format(i, step.name)
        create_step_dynamic_explicit(step_name=step_name,
                                     time_period=step.duration,
                                     max_increment=max_time_increment,
                                     previous_step_name='Initial')

        # create all amplitudes and loads
        for j, transducer_signal in enumerate(step.transducer_signals):
            if transducer_signal is not None:
                add_transducer_concentrated_force(step_name=step_name,
                                                  transducer=model.transducers[j],
                                                  signal=transducer_signal,
                                                  max_time_increment=max_time_increment)

        # create output request for piezo node sets
        remove_standard_field_output_request()
        if step.output_request == 'history':
            add_history_output_request_transducer_signals(transducers=model.transducers,
                                                          create_step_name=step_name)
            log_info("Created load case {} with history output requested.".format(step_name))

        if step.output_request == 'field':
            add_history_output_request_transducer_signals(transducers=model.transducers,
                                                          create_step_name=step_name)
            add_field_output_request_plate_surface(plate=model.plate, create_step_name=step_name,
                                                   time_interval=max_time_increment * 10)
            log_info("Created load case {} with history and field output requested.".format(step_name))

        # write ABAQUS input (.INP) file for this load case
        if model.no_gui_mode:
            output_directory = os.path.join(model.output_directory, step_name)
            write_input_file(job_name='{}_{}'.format(model.model_name, step_name), output_directory=output_directory)
            log_info("Created an ABAQUS job definition (.INP) file for "
                     "the current load case ({}.inp).".format(step_name))
        else:
            log_info("Automatic .INP-file generation is omitted when ABAQUS is run in GUI-mode. You can "
                     "create a job for the last load case manually using the ABAQUS GUI or rerun this script "
                     "with noGUI flag.")
