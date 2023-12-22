class CircularTransducer:
    def __init__(self, position_x, position_y, diameter, thickness=None, material=None, electrode_thickness=None,
                 electrode_material=None, position_z='top'):

        # properties for modes 'point_force' and 'piezo_electric'
        self.radius = diameter / 2
        self.position_x = position_x
        self.position_y = position_y
        self.position_z = position_z

        # position_z (validation)
        valid_position_z = ['top', 'bottom', 'symmetric', 'asymmetric']
        if position_z not in valid_position_z:
            raise ValueError("Invalid value for position_z. Accepted values are: {}".format(valid_position_z))
        self.position_z = position_z

        # properties for mode 'piezo_electric'
        self.thickness = thickness
        self.material = material
        self.electrode_thickness = electrode_thickness
        self.electrode_material = electrode_material

        # abaqus properties --------------------------------------------------------------------------------------------
        self.id = None
        self.name = None               # deprecated
        self.on_plate_top_set_name = None
        self.on_plate_bottom_set_name = None
        self.bounding_box_cell_set_name = None

        # abaqus properties only needed for mode 'piezo_electric' - geometry and cell sets
        self.piezo_material_cell_set_name = None
        self.electrode_material_cell_set_name = None

        self.piezo_top_surf_set_name = None
        self.piezo_bot_surf_set_name = None
        self.interface_surf_set_name = None

        # abaqus properties only needed for mode 'piezo_electric' - electrical contact node sets
        self.signal_main_node_set_name = None
        self.gnd_main_node_set_name = None
        self.signal_slave_node_set_name = None
        self.gnd_slave_node_set_name = None

    def set_identifiers(self, unique_id):
        """

        :param unique_id:

        :return: None
        """
        self.id = unique_id
        self.name = "transducer_{:02d}".format(self.id)
        self.on_plate_top_set_name = "{}_top".format(self.name)
        self.on_plate_bottom_set_name = "{}_bottom".format(self.name)

        # this will need some work since top, bot, sym, asym were introduced ...
        self.bounding_box_cell_set_name = "{}_bound_box".format(self.name)
        self.piezo_material_cell_set_name = "{}_piezo_material".format(self.name)
        self.electrode_material_cell_set_name = "{}_electrode_material".format(self.name)
        self.piezo_top_surf_set_name = "{}_top_surf".format(self.name)
        self.piezo_bot_surf_set_name = "transducer_{:d}_bot_surf".format(self.id)
        self.interface_surf_set_name = "transducer_{:d}_interface_surf".format(self.id)

        self.signal_main_node_set_name = "transducer_{:d}_sgn_master".format(self.id)
        self.gnd_main_node_set_name = "transducer_{:d}_gnd_master".format(self.id)
        self.signal_slave_node_set_name = "transducer_{:d}_sgn_slave".format(self.id)
        self.gnd_slave_node_set_name = "transducer_{:d}_gnd_slave".format(self.id)
