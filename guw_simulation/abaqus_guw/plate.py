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

        input_is_rectangle = length is not None and width is not None
        input_is_shape = shape is not None and is_valid_coordinate_list(shape)
        input_is_valid = (input_is_shape and not input_is_rectangle) or (input_is_rectangle and not input_is_shape)

        if input_is_valid:
            if input_is_shape:
                self.shape = shape
                self.description = "Plate thickness: {} mm.".format(thickness*1e3)
            if input_is_rectangle:
                self.shape = ((0, 0), (length, 0), (length, width), (0, width), (0, 0))
                self.description = "Plate size is {} x {} x {} mm.".format(length*1e3, width*1e3, thickness*1e3)
        else:
            raise ValueError("Invalid input. Provide either 'shape' as a valid coordinate list or 'length' and "
                             "'width' (but not both).")

        # private attributes
        self.datum_plane_abaqus_id = None
        self.datum_axis_abaqus_id = None
        self.cell_set_name = None
        self.material_cell_set_name = None
        self.top_surf_face_set_name = None
        self.std_interface_node_set_name = None
        self.xpl_interface_node_set_name = None


def is_valid_coordinate_list(variable):
    if isinstance(variable, tuple) and all(
            isinstance(inner_tuple, tuple) and len(inner_tuple) == 2 for inner_tuple in variable):
        return all(isinstance(item, (int, float)) for inner_tuple in variable for item in inner_tuple)
    return False
