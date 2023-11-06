class Hole:
    def __init__(self, position_x, position_y, diameter, guideline_option='plus'):
        self.radius = diameter / 2
        self.position_x = position_x
        self.position_y = position_y
        self.guideline_option = guideline_option

        # private properties
        self.id = None


class Crack:
    def __init__(self):
        pass


class Delamination:
    def __init__(self):
        pass
