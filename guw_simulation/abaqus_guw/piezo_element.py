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
        self.wall_face_set_name = None
        self.set_name = None

        # properties for standard/explicit cosimulation
        self.part_name = None
        self.xpl_interface_set_name = None
        self.std_interface_set_name = None


