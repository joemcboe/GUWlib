class PiezoElement:
    def __init__(self, position_x, position_y, diameter, thickness=None, material=None, signal=None):
        self.radius = diameter/2
        self.position_x = position_x
        self.position_y = position_y
        self.thickness = thickness
        self.material = material
        self.signal = signal

        # private properties
        self.id = None
        self.wall_face_set_name = None
        self.set_name = None


