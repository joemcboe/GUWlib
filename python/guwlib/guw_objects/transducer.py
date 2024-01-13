class Transducer(object):
    """
    Base class to represent (piezoelectric) transducers.
    """

    def __init__(self):
        pass

    def set_identifiers(self, unique_id):
        """
        Sets the names to identify different ABAQUS geometry / mesh parts of the transducer.

        :param int unique_id: A unique ID of this transducer.
        """


class CircularTransducer(Transducer):
    """
    Represents a circular (piezoelectric) transducer.

    The transducer may be realised in the FE model as a concentrated force or as a piezoelectric patch with an electric
    potential applied to its surfaces, depending on whether ``model_approach`` is set to ``point_force`` or
    ``piezo_electric``, respectively.
    """

    def __init__(self, position_x, position_y, diameter, position_z='top', thickness=None, material=None,
                 electrode_thickness=None, electrode_material=None):
        """
        :param float position_x: Position of the transducer in x-direction from the coordinate origin.
        :param float position_y: Position of the transducer in y-direction from the coordinate origin.
        :param float diameter: Diameter of the circular transducer.
        :param str position_z: Position of the transducer with respect to the plate surface, either
            ``top``, ``bottom``, ``symmetric`` or ``asymmetric``.
        :param float thickness: Thickness of the piezo-electric material part of the transducer (required only
            if ``FEModel.model_approach`` is set to ``piezo_electric``.)
        :param PiezoElectricMaterial material: Material used to model the transducer (required only
            if ``FEModel.model_approach`` is set to ``piezo_electric``.)
        :param float electrode_thickness: Thickness of the electrode material part of the transducer (required only
            if ``FEModel.model_approach`` is set to ``piezo_electric``.)
        :param IsotropicMaterial electrode_material: Material used to model the transducers' electrode
            (required only if ``FEModel.model_approach`` is set to ``piezo_electric``.)


        :ivar float radius: Radius of the circular transducer.
        :ivar float position_x: Position of the transducer in x-direction from the coordinate origin.
        :ivar float position_y: Position of the transducer in y-direction from the coordinate origin.
        :ivar str position_z: Position of the transducer with respect to the plate surface.
        :ivar float thickness: Thickness of the piezo-electric material part of the transducer.
        :ivar PiezoElectricMaterial material: Material used to model the transducer.
        :ivar float electrode_thickness: Thickness of the electrode material part of the transducer.
        :ivar IsotropicMaterial electrode_material: Material used to model the transducers' electrode.

        :ivar int id: A unique ID of this transducer.
        :ivar str name: A unique, descriptive name of this transducer.
        :ivar str on_plate_top_set_name: Name for the ABAQUS set containing the transducer which is applied to the
            top surface of the plate.
        :ivar str on_plate_bottom_set_name: Name for the ABAQUS set containing the transducer which is applied to the
            top surface of the plate.
        :ivar str bounding_box_cell_set_name: Name for the ABAQUS set containing the transducers bounding box.
        """

        # instance variables for modes 'point_force' and 'piezo_electric'
        super(CircularTransducer, self).__init__()
        self.radius = diameter / 2
        self.position_x = position_x
        self.position_y = position_y

        # position_z (validation)
        valid_position_z = ['top', 'bottom', 'symmetric', 'asymmetric']
        if position_z not in valid_position_z:
            raise ValueError("Invalid value for position_z. "
                             "Accepted values are: {}".format(valid_position_z))
        self.position_z = position_z

        # instance variables only for mode 'piezo_electric'
        self.thickness = thickness
        self.material = material
        self.electrode_thickness = electrode_thickness
        self.electrode_material = electrode_material

        # instance variables to store ABAQUS cell set names
        self.id = None
        self.name = None
        self.on_plate_top_set_name = None
        self.on_plate_bottom_set_name = None
        self.bounding_box_cell_set_name = None

    def set_identifiers(self, unique_id):
        """
        Sets the names to identify different ABAQUS geometry / mesh parts of the transducer.

        :param int unique_id: A unique ID of this transducer.
        """
        self.id = unique_id
        self.name = "transducer_{:02d}".format(self.id)
        self.on_plate_top_set_name = "{}_top".format(self.name)
        self.on_plate_bottom_set_name = "{}_bottom".format(self.name)
        self.bounding_box_cell_set_name = "{}_bound_box".format(self.name)

        # # this will need some rework since top, bot, sym, asym were introduced ...
        # self.piezo_material_cell_set_name = "{}_piezo_material".format(self.name)
        # self.electrode_material_cell_set_name = "{}_electrode_material".format(self.name)
        # self.piezo_top_surf_set_name = "{}_top_surf".format(self.name)
        # self.piezo_bot_surf_set_name = "transducer_{:d}_bot_surf".format(self.id)
        # self.interface_surf_set_name = "transducer_{:d}_interface_surf".format(self.id)
        #
        # self.signal_main_node_set_name = "transducer_{:d}_sgn_master".format(self.id)
        # self.gnd_main_node_set_name = "transducer_{:d}_gnd_master".format(self.id)
        # self.signal_slave_node_set_name = "transducer_{:d}_sgn_slave".format(self.id)
        # self.gnd_slave_node_set_name = "transducer_{:d}_gnd_slave".format(self.id)
