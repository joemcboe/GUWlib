class PiezoElement:
    def __init__(self, diameter, position_x, position_y, thickness, material):
        self.radius = diameter/2
        self.position_x = position_x
        self.position_y = position_y
        self.thickness = thickness
        self.material = material

        self.id = None
        self.wall_set = None

