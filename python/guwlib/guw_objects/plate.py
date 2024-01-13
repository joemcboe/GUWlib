class Plate(object):
    """
    Base class to represent thin plates in which GUW can propagate.
    """

    def __init__(self):
        pass


class IsotropicRectangularPlate(Plate):
    """A class representing a simple isotropic, rectangular plate.

    The bottom left-hand corner of the plate marks the reference (coordinate origin) for all other
    objects (:class:`Defect`, :class:`Transducer`).
    """

    def __init__(self, material, thickness, width=None, length=None):
        """
        :param IsotropicMaterial material:  Plate material, e.g. 1100 aluminum alloy.
        :param float thickness: Plate thickness.
        :param float width: Plate width (ABAQUS x-direction).
        :param float length: Plate length (ABAQUS y-direction).

        :ivar IsotropicMaterial material:  Plate material, e.g. 1100 aluminum alloy.
        :ivar float thickness: Plate thickness.
        :ivar float width: Plate width (ABAQUS x-direction).
        :ivar float length: Plate length (ABAQUS y-direction).
        :ivar str description: A short description of the plate for logging.
        :ivar int datum_xy_plane_id: ABAQUS feature ID of a datum xy-plane (modelling aid).
        :ivar int datum_y_axis_id: ABAQUS feature ID of a datum y-axis (modelling aid).
        :ivar int datum_z_axis_id: ABAQUS feature ID of a datum z-axis (modelling aid).
        :ivar str cell_set_name: Name for the ABAQUS cell set containing the entire plate
            (excluding defect and transducer bounding boxes).
        :ivar str material_cell_set_name: Name for the ABAQUS cell set containing the entire plate
            (including all defect and transducer bounding boxes).
        :ivar str top_surf_face_set_name: Name for the ABAQUS face set containing the top surface of the plate
            (excluding defect and transducer bounding boxes).
        :ivar str field_output_face_set_name: Name for the ABAQUS face set containing the top surface of the plate
            (including defect and transducer bounding boxes).
        :ivar str std_interface_node_set_name: Name for the ABAQUS node set containing all nodes of the
            STD-XPL interface between plate and transducers, on the STD part of the model (relevant only if
            ``modeling_approach`` is set to ``piezo_electric``).
        :ivar str xpl_interface_node_set_name: Name for the ABAQUS node set containing all nodes of the
            STD-XPL interface between plate and transducers, on the XPL part of the model (relevant only if
            ``modeling_approach`` is set to ``piezo_electric``).

        """
        super(IsotropicRectangularPlate, self).__init__()

        # geometry and material attributes
        self.material = material
        self.thickness = thickness
        self.width = width
        self.length = length

        # attributes to store abaqus feature ids
        self.datum_xy_plane_id = None
        self.datum_y_axis_id = None
        self.datum_z_axis_id = None

        # the following attributes should rather be properties with decorators, but not supported in Python 2.7
        self.description = "{} plate with size {} x {} x {} mm.".format(self.material.name,
                                                                        width * 1e3,
                                                                        length * 1e3,
                                                                        thickness * 1e3)
        # attributes to store ABAQUS set names
        self.cell_set_name = 'plate'
        self.material_cell_set_name = 'plate-material'
        self.top_surf_face_set_name = 'plate-top-surface'
        self.field_output_face_set_name = 'plate-field-output'
        self.std_interface_node_set_name = 'plate-std-interface'
        self.xpl_interface_node_set_name = 'plate-xpl-interface'
