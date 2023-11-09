class PiezoElement:
    def __init__(self, position_x, position_y, diameter, thickness=None, material=None, electrode_thickness=None,
                 electrode_material=None):

        # basic properties
        self.radius = diameter/2
        self.position_x = position_x
        self.position_y = position_y

        # properties for mode 'piezo_electric'
        self.thickness = thickness
        self.material = material
        self.electrode_thickness = electrode_thickness
        self.electrode_material = electrode_material

        # private properties
        self.id = None
        self.cell_set_name = None
        self.bounding_box_cell_set_name = None

        # properties only needed for standard/explicit co-simulation ---------------------------------------------------
        self.piezo_material_cell_set_name = None
        self.electrode_material_cell_set_name = None

        self.piezo_top_surf_set_name = None
        self.piezo_bot_surf_set_name = None
        self.interface_surf_set_name = None

        # electrical contact node sets
        self.signal_main_node_set_name = None
        self.gnd_main_node_set_name = None
        self.signal_slave_node_set_name = None
        self.gnd_slave_node_set_name = None





