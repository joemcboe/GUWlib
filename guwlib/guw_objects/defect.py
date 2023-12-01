class Hole:
    def __init__(self, position_x, position_y, diameter):
        self.radius = diameter / 2
        self.position_x = position_x
        self.position_y = position_y

        # private properties
        self.id = None
        self.bounding_box_cell_set_name = None

    def set_identifiers(self, unique_id):
        self.id = unique_id
        self.bounding_box_cell_set_name = "hole_{:02d}_bound_box".format(self.id)
