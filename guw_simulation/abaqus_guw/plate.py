class IsotropicPlate:
    """A class representing an isotropic plate."""

    def __init__(self, material, thickness, length=None, width=None):
        """
        Initialize an IsotropicPlate.

        Parameters:
            material (str):                     The material of the plate.
            thickness (float):                  The thickness of the plate.
            length (float):                     The length of the plate (for rectangular shape).
            width (float):                      The width of the plate (for rectangular shape).

        Raises:
            ValueError: If the input is not valid.
        """

        # geometry and material
        self.material = material
        self.thickness = thickness
        self.width = length         # todo clean!
        self.height = width         # todo clean!
        self.shape = ((0, 0), (length, 0), (length, width), (0, width), (0, 0))
        self.description = "Plate size is {} x {} x {} mm.".format(length*1e3, width*1e3, thickness*1e3)

        # private attributes
        self.datum_xy_plane_id = None
        self.datum_y_axis_id = None
        self.datum_z_axis_id = None
        self.cell_set_name = None
        self.material_cell_set_name = None
        self.top_surf_face_set_name = None
        self.std_interface_node_set_name = None
        self.xpl_interface_node_set_name = None
