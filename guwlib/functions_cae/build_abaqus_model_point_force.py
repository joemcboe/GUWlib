import guwlib.fe_model as fe_model
from guwlib.functions_utility.rectilinear_partitioning import partition_rectangular_plate
from guwlib.guw_objects.defect import *
from guwlib.guw_objects.loadcase import *
from guwlib.guw_objects.material import *
from guwlib.guw_objects.plate import *
from guwlib.guw_objects.signals import *
from guwlib.guw_objects.transducer import *
from guwlib.functions_cae.helper_functions_point_force import *
from guwlib.functions_utility.console_output import *


def build_abaqus_model_point_force(model):
    """
    :param fe_model.FEModel model:
    :return:
    """

    # TIME AND SPACE DISCRETIZATION ------------------------------------------------------------------------------------
    element_size_in_plane = model.get_element_size_in_plane()
    element_size_thickness = model.get_element_size_thickness()
    max_time_increment = model.get_max_time_increment()

    log_info("Element size, in-plane:          {:.2e} m (for {:.0f} elements per wavelength)\n"
             "Element size, through-thickness: {:.2e} m (for {:.0f} elements per thickness)\n"
             "Max. time increment:             {:.2e} s (for a Courant number of 0.1)"
             "".format(element_size_in_plane, model.elements_per_wavelength,
                       element_size_thickness, model.elements_in_thickness_direction,
                       max_time_increment))

    # PART MODULE ------------------------------------------------------------------------------------------------------
    # create the plate as a part in abaqus
    create_plate_part(model.plate)
    log_info("Created plate geometry: {}".format(model.plate.description))

    # create a pristine plate w/o defects or piezo-elements, and obtain a structured mesh for better partitioning
    create_reference_mesh_plate(plate=model.plate, element_size=element_size_in_plane)

    # create the defects geometry
    bounding_box_list = []
    log_txt = ""
    for i, defect in enumerate(model.defects):
        defect.set_identifiers(unique_id=i)
        if isinstance(defect, Hole):
            bounding_box = create_circ_hole_in_plate(plate=model.plate, hole=defect, element_size=element_size_in_plane)
            bounding_box_list.append(bounding_box)
    log_info("Added {} defect(s):\n{}".format(len(model.defects), log_txt))

    # piezo geometry
    for i, transducer in enumerate(model.transducers):
        transducer.set_identifiers(unique_id=i)
        bounding_box = create_transducer_as_point_load(plate=model.plate, transducer=transducer,
                                                       element_size=element_size_in_plane)
        bounding_box_list.append(bounding_box)
    log_info("Added " + str(len(model.transducers)) + " nodes, representing the piezoelectric transducers.")

    # partition the plate into partitions that are suitable for structured meshing
    log_info("Generating a rectilinear partitioning strategy for the plate. This might take some time...")
    cells = partition_rectangular_plate(model.plate, bounding_box_list)
    log_info("Done. Starting to create {:d} rectangular partitions on the plate part.".format(len(cells)))
    err_count = 0
    for i, cell in enumerate(cells[:-1]):
        left, bottom, right, top = (cell[0], cell[1], cell[2], cell[3])
        status, warning = add_rectangular_partition_to_plate(model.plate, left, bottom, right, top)
        err_count += status
    if err_count > 0:
        log_warning("{} partitions could not be created. Probably the target region"
                    " was already rectangular".format(err_count))
