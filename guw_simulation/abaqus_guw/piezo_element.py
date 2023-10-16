class PiezoElement:
    def __init__(self, diameter, position_x, position_y, thickness, material, signal=None):
        self.radius = diameter/2
        self.position_x = position_x
        self.position_y = position_y
        self.thickness = thickness
        self.material = material
        self.signal = signal

        self.id = None
        self.wall_face_set = None
        self.set_name = None


