class MyClass:
    """A brief description of the MyClass.

    This is a more detailed description of the class.

    Attributes:
        attribute1 (int): Description of attribute1.
        attribute2 (str): Description of attribute2.

    """

    def __init__(self, attribute1, attribute2):
        """Initialize the MyClass object.

        Args:
            attribute1 (int): Description of attribute1.
            attribute2 (str): Description of attribute2.

        """
        self.attribute1 = attribute1
        self.attribute2 = attribute2

    @property
    def property1(self):
        """Get the value of property1."""
        return self._property1

    @property1.setter
    def property1(self, value):
        """Set the value of property1.

        Args:
            value: The new value for property1.

        """
        self._property1 = value

    def method1(self, arg1, arg2):
        """Perform a task using arg1 and arg2.

        Args:
            arg1: Description of arg1.
            arg2: Description of arg2.

        Returns:
            The result of the task.

        """
        # Implementation of the method

    def method2(self):
        """Perform another task.

        Returns:
            A result related to the task.

        """
        # Implementation of the method
