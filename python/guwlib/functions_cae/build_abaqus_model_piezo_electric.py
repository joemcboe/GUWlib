"""
PIEZO ELECTRIC APPROACH IS UNDOCUMENTED AND NOT PROPERLY INTEGRATED. LAST COMMIT WHERE THESE FUNCTIONS WERE TESTED WAS
NOV 15 2023. DO NOT IMPORT THIS MODULE!
"""


def build_abaqus_model_piezo_electric(model):
    """
    Undocumented and not integrated. Do not use this function.
    """
    raise NotImplementedError('Piezo-electric modelling approach not implemented.')

    # TIME AND SPACE DISCRETIZATION --------------------------------------------------------------------------------
    # determine the element size according to CFL condition
    wavelengths = get_lamb_wavelength(material=model.plate.material,
                                      thickness=model.plate.thickness,
                                      frequency=max_exciting_frequency)
    min_wavelength = min(min(wavelengths[0]), min(wavelengths[1]))
    element_size_nodes_per_wavelength = min_wavelength / (model.nodes_per_wavelength - 1)
    element_size_thickness = model.plate.thickness / model.elements_in_thickness_direction
    element_size = min(element_size_thickness, element_size_nodes_per_wavelength)

    log_info("Element size set to {:.2e} m.\n"
             "(Max exciting frequency:   {:.2f} kHz\n"
             " For {:.0f} nodes per wavelength:   max element size: {:.2e} m\n"
             " For {:.0f} elements per thickness: max element size: {:.2e} m)"
             "".format(element_size, max_exciting_frequency * 1e-3, model.nodes_per_wavelength,
                       element_size_nodes_per_wavelength, model.elements_in_thickness_direction,
                       element_size_thickness))

    # create a pristine plate w/o defects or piezo-elements, and obtain a structured mesh for better partitioning
    create_reference_mesh_plate(plate=model.plate, element_size=element_size)

    # PART MODULE --------------------------------------------------------------------------------------------------
    # plate geometry
    create_plate(plate=model.plate)
    log_info("Created plate geometry: {}".format(model.plate.description))

    # defects geometry
    bounding_box_list = []
    log_txt = ""
    for i, defect in enumerate(model.defects):
        defect.id = i
        if isinstance(defect, Hole):
            bounding_box = create_circular_hole_in_plate(plate=model.plate, hole=defect, element_size=element_size)
            bounding_box_list.append(bounding_box)
            log_txt = "{}\n{:g}-mm circular hole at ({:g},{:g}) mm".format(log_txt,
                                                                           defect.radius * 2e3,
                                                                           defect.position_x * 1e3,
                                                                           defect.position_y * 1e3)
        if isinstance(defect, Crack):
            pass
            # TODO

    log_info("Added {} defect(s):\n{}".format(len(model.defects), log_txt))

    if model.model_approach == 'piezo_electric':
        for i, piezo in enumerate(model.phased_array):
            piezo.id = i
            create_piezo_element(plate=model.plate, piezo_element=piezo)

    # partition the plate into partitions that are suitable for structured meshing
    log_info("Generating a rectilinear partitioning strategy for the plate. This might take some time...")
    cells = partition_rectangular_plate(model.plate, bounding_box_list)
    log_info("Done. Starting to create {:d} rectangular partitions on the plate part.".format(len(cells)))
    for i, cell in enumerate(cells[:-1]):
        left, bottom, right, top = (cell[0], cell[1], cell[2], cell[3])
        add_rectangular_partition_to_plate(model.plate, left, bottom, right, top)

    # delete the reference mesh plate
    remove_reference_mesh_plate()

    # PROPERTY MODULE ----------------------------------------------------------------------------------------------

    if model.model_approach == 'piezo_electric':
        pass
        # materials will be assigned after splitting the model for co-simulation

    # MESH MODULE --------------------------------------------------------------------------------------------------
    if model.model_approach == 'piezo_electric':
        num_nodes = mesh_part_piezo_electric_approach(element_size=element_size,
                                                      phased_array=model.phased_array,
                                                      defects=model.defects)
        create_mesh_parts()
        split_mesh_parts(model.plate, model.phased_array)
        create_electric_interface(model.phased_array)

    # ASSEMBLY MODULE ----------------------------------------------------------------------------------------------
    # create assembly and instantiate the plate

    if model.model_approach == 'piezo_electric':
        assemble_co_sim()

    # INTERACTION MODULE -------------------------------------------------------------------------------------------
    # split model and create electrical interface
    if model.model_approach == 'piezo_electric':
        split_model_for_co_sim()
        setup_electric_interface(model.phased_array)

    # PROPERTY MODULE ----------------------------------------------------------------------------------------------
    if model.model_approach == 'piezo_electric':
        # create and assign materials in individual models (dielectric materials are not permitted in XPL model)
        create_materials_co_sim(model.plate, model.phased_array)
        assign_material_co_sim(model.plate, model.phased_array)

    # STEP / LOAD / JOB MODULE -------------------------------------------------------------------------------------
    max_time_increment_condition_1 = (0.5 / ((model.nodes_per_wavelength - 1) * max_exciting_frequency))
    max_time_increment_condition_2 = 1 / max_exciting_frequency
    max_time_increment = min(max_time_increment_condition_1, max_time_increment_condition_2)
    info_str = ("Time discretization:\n" +
                "max time increment: {:.2e} s\n".format(max_time_increment))
    log_info(info_str)

    if model.model_approach == 'piezo_electric':
        for i, step in enumerate(model.load_cases):

            # delete all steps except initial
            remove_all_steps_co_sim()

            # create new steps in explicit and standard models
            step_name = 'load_case_{}_{}'.format(i, step.name)
            create_steps_co_sim(step_name=step_name,
                                time_period=step.duration,
                                max_increment=max_time_increment,
                                previous_step_name='Initial')

            # create co-sim-interaction
            create_interaction_std_xpl_co_sim(plate=model.plate, step_name=step_name)

            # create history output request for piezo node sets
            remove_standard_field_output_request_co_sim()
            if step.output_request == 'history':
                add_piezo_signal_history_output_request_co_sim(phased_array=model.phased_array,
                                                               create_step_name=step_name)
            #
            if step.output_request == 'field':
                add_piezo_signal_history_output_request_co_sim(phased_array=model.phased_array,
                                                               create_step_name=step_name)
                add_field_output_request_co_sim(create_step_name=step_name)

            # create all amplitudes and loads
            add_piezo_boundary_conditions_co_sim(step_name, model.phased_array)
            for j, signal in enumerate(step.piezo_signals):
                if signal is not None:
                    add_piezo_potential_co_sim(load_name='sgn_{}_{}'.format(model.phased_array[j].cell_set_name,
                                                                            signal.__class__.__name__),
                                               step_name=step_name,
                                               piezo=model.phased_array[j],
                                               signal=signal,
                                               max_time_increment=max_time_increment)

            # # write input file for this load case

            log_info("Created a job definition for the current load case. To run or view this load case,"
                     "please refer to the created input file '{}.inp'. ".format(step_name))

    # DISPLAY OPTIONS ----------------------------------------------------------------------------------------------
    make_datums_invisible()
