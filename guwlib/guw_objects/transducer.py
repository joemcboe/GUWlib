class CircularTransducer:
    def __init__(self, position_x, position_y, diameter, thickness=None, material=None, electrode_thickness=None,
                 electrode_material=None):

        # basic properties
        self.radius = diameter/2
        self.position_x = position_x
        self.position_y = position_y

        # abaqus properties --------------------------------------------------------------------------------------------
        self.id = None
        self.cell_set_name = None
        self.bounding_box_cell_set_name = None

        # properties for mode 'piezo_electric'
        self.thickness = thickness
        self.material = material
        self.electrode_thickness = electrode_thickness
        self.electrode_material = electrode_material

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
        :return:
        """
        self.id = unique_id
        self.cell_set_name = "transducer_{:02d}".format(self.id)
        self.bounding_box_cell_set_name = "transducer_{:02d}_bound_box".format(self.id)

        self.piezo_material_cell_set_name = "transducer_{:02d}_piezo_material".format(self.id)
        self.electrode_material_cell_set_name = "transducer_{:02d}_electrode_material".format(self.id)
        self.piezo_top_surf_set_name = "transducer_{:02d}_top_surf".format(self.id)
        self.piezo_bot_surf_set_name = "transducer_{:d}_bot_surf".format(self.id)
        self.interface_surf_set_name = "transducer_{:d}_interface_surf".format(self.id)

        self.signal_main_node_set_name = "transducer_{:d}_sgn_master".format(self.id)
        self.gnd_main_node_set_name = "transducer_{:d}_gnd_master".format(self.id)
        self.signal_slave_node_set_name = "transducer_{:d}_sgn_slave".format(self.id)
        self.gnd_slave_node_set_name = "transducer_{:d}_gnd_slave".format(self.id)



