import math


class Defect(object):
    def __init__(self, position_x, position_y):
        self.position_x = position_x
        self.position_y = position_y

        # private properties
        self.id = None
        self.bounding_box_cell_set_name = None

    def set_identifiers(self, unique_id):
        self.id = unique_id
        self.bounding_box_cell_set_name = "{}_{:02d}_bound_box".format(self.__class__.__name__.lower(), self.id)


class Hole(Defect):
    def __init__(self, position_x, position_y, diameter):
        super(Hole, self).__init__(position_x, position_y)
        self.radius = diameter / 2


class Crack(Defect):
    def __init__(self, position_x, position_y, length, angle_degrees=0):
        super(Crack, self).__init__(position_x, position_y)
        self.length = length
        self.angle = angle_degrees * math.pi / 180.0
        self.seam_face_set_name = None

    def set_identifiers(self, unique_id):
        super(Crack, self).set_identifiers(unique_id)
        self.seam_face_set_name = "crack_{:02d}_seam".format(self.id)
