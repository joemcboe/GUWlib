class IsotropicPlate:
    """A class representing an isotropic plate."""

    def __init__(self, material, thickness, length=None, width=None, shape=None):
        """
        Initialize an IsotropicPlate.

        Parameters:
            material (str):                     The material of the plate.
            thickness (float):                  The thickness of the plate.
            length (float, optional):           The length of the plate (for rectangular shape).
            width (float, optional):            The width of the plate (for rectangular shape).
            shape (list of tuple, optional):    The shape of the plate as a list of coordinate tuples.

        Raises:
            ValueError: If the input is not valid.
        """
        self.material = material
        self.thickness = thickness
        self.defects = []
        self.datum_plane_abaqus_id = None
        self.datum_axis_abaqus_id = None

        input_is_rectangle = length is not None and width is not None
        input_is_shape = shape is not None and is_valid_coordinate_list(shape)
        input_is_valid = (input_is_shape and not input_is_rectangle) or (input_is_rectangle and not input_is_shape)

        if input_is_valid:
            if input_is_shape:
                self.shape = shape
            if input_is_rectangle:
                self.shape = ((0, 0), (length, 0), (length, width), (0, width), (0, 0))
        else:
            raise ValueError("Invalid input. Provide either 'shape' as a valid coordinate list or 'length' and "
                             "'width' (but not both).")

    def add_hole(self, position, radius, guideline_option='none'):
        hole = {"type": "hole", "position": position, "radius": radius, "guideline_option": guideline_option}
        self.defects.append(hole)


def is_valid_coordinate_list(variable):
    if isinstance(variable, tuple) and all(
            isinstance(inner_tuple, tuple) and len(inner_tuple) == 2 for inner_tuple in variable):
        return all(isinstance(item, (int, float)) for inner_tuple in variable for item in inner_tuple)
    return False
