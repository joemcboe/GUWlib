import math


class Defect(object):
    """
    Base class to represent plate defects.
    """

    def __init__(self, position_x, position_y):
        """
        :param float position_x: Position of the defect in x-direction from the coordinate origin.
        :param float position_y: Position of the defect in y-direction from the coordinate origin.

        :ivar float position_x: Position of the defect in x-direction from the coordinate origin.
        :ivar float position_y: Position of the defect in y-direction from the coordinate origin.
        :ivar int id: Unique identification number of the defect.
        :ivar str bounding_box_cell_set_name: Unique name for the ABAQUS cell set of the defects bounding box.
        """
        self.position_x = position_x
        self.position_y = position_y

        # the following attributes should rather be properties with decorators, but not supported in Python 2.7
        self.id = None
        self.bounding_box_cell_set_name = None

    def set_identifiers(self, unique_id):
        """
        Sets a unique ID and ABAQUS cell set name for this defects' bounding box.

        :param int unique_id: Unique ID of this defect.
        """
        self.id = unique_id
        self.bounding_box_cell_set_name = "{}_{:02d}_bound_box".format(self.__class__.__name__.lower(), self.id)


class Hole(Defect):
    """
    Represents a simple, circular through-thickness hole.
    """
    def __init__(self, position_x, position_y, diameter):
        """
        :param float position_x: Position of the hole in x-direction from the coordinate origin.
        :param float position_y: Position of the hole in y-direction from the coordinate origin.
        :param float diameter: Diameter of the hole.

        :ivar float radius: Radius of the hole.
        """
        super(Hole, self).__init__(position_x, position_y)
        self.radius = diameter / 2


class Crack(Defect):
    def __init__(self, position_x, position_y, length, angle_degrees=0):
        """
        Represents a simple, through-thickness crack (realised by node-separation in the FE model).

        The crack is oriented along the y-axis if ``angle_degrees`` is set to ``0`` (default).

        :param float position_x: Position of the crack midpoint in x-direction from the coordinate origin.
        :param float position_y: Position of the crack midpoint in y-direction from the coordinate origin.
        :param float length: Length of the crack.
        :param float angle_degrees: Rotation angle of the crack, in degrees (counterclockwise rotation).

        :ivar float length: Length of the crack.
        :ivar float angle: Rotation angle of the crack, in radians (counterclockwise rotation).
        :ivar str seam_face_set_name: Name for the ABAQUS face set containing the crack edge faces.
        """
        super(Crack, self).__init__(position_x, position_y)
        self.length = length
        self.angle = angle_degrees * math.pi / 180.0
        self.seam_face_set_name = None

    def set_identifiers(self, unique_id):
        """
        Sets a unique ID and ABAQUS cell set name for this cracks' bounding box and seam face set.

        :param int unique_id: Unique ID of this crack.
        """
        super(Crack, self).set_identifiers(unique_id)
        self.seam_face_set_name = "crack_{:02d}_seam".format(self.id)
