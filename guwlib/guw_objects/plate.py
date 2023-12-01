class IsotropicPlate:
    """A class representing an isotropic plate."""

    def __init__(self, material, thickness, width=None, length=None):
        """

        """
        # geometry and material attributes
        self.material = material
        self.thickness = thickness
        self.width = width
        self.length = length

        # convenience
        self.description = "Plate size is {} x {} x {} mm.".format(width * 1e3, length * 1e3, thickness * 1e3)

        # attributes to store abaqus set names and feature ids
        self.datum_xy_plane_id = None
        self.datum_y_axis_id = None
        self.datum_z_axis_id = None
        self.cell_set_name = 'plate'
        self.material_cell_set_name = 'plate-material'
        self.top_surf_face_set_name = 'plate-top-surface'
        self.field_output_face_set_name = 'plate-field-output'
        self.std_interface_node_set_name = 'plate-std-interface'
        self.xpl_interface_node_set_name = 'plate-xpl-interface'


