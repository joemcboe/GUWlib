import json
import os


class Material(object):
    """
    Base class to represent materials by their properties and by their material-dependent dispersion data.
    """

    def __init__(self, material_name):
        """
        :param str material_name: Name of the material for which to load the data.

        :ivar str name: Name of the material.
        :ivar dict properties: Dictionary storing the material properties.
        """
        self.name = material_name
        self.properties = self._load_material_properties()

    def _load_material_properties(self):
        """
        Loads material properties from the respective *.JSON or *.TXT files in the  ``guwlib/data`` folder.
        """
        return None


class IsotropicMaterial(Material):
    """
    Represents an isotropic material, e.g. 1100 aluminum alloy.

    An ``IsotropicMaterial`` instance is initialized by passing a valid  material name to its constructor.
    The respective material properties are then loaded from the ``guwlib/data/isotropic_materials.json`` file.

    :raises: ValueError: If the material name doesn't exist in the material library (*.JSON file).
    """

    def __init__(self, material_name):
        """
        :param str material_name: Name of the isotropic material for which to load the data.
        """
        super(IsotropicMaterial, self).__init__(material_name=material_name)

    def _load_material_properties(self):
        """
        Loads material properties from the respective *.JSON file in the  ``guwlib/data`` folder.

        :return: (dict) Material properties.
        """
        script_path = os.path.abspath(__file__)
        parent_dir = os.path.dirname(os.path.dirname(script_path))
        json_path = os.path.join(parent_dir, 'data', 'isotropic_materials.json')
        material_properties = extract_properties_from_json(json_file_path=json_path,
                                                           target_item_name=self.name)
        validate_isotropic_material(material_properties)
        return material_properties


class PiezoElectricMaterial(Material):
    """
    Represents a piezoelectric material, e.g. PIC255.

    A ``PiezoelectricMaterial`` instance is initialized by passing a valid  material name to its constructor.
    The respective material properties are then loaded from the ``guwlib/data/piezoelectric_materials.json`` file.

    :raises: ValueError: If the material name doesn't exist in the material library (*.JSON file).
    """

    def __init__(self, material_name):
        """
        :param str material_name: Name of the piezoelectric material for which to load the data.
        """
        super(PiezoElectricMaterial, self).__init__(material_name)

    def _load_material_properties(self):
        """
        Loads material properties from the respective *.JSON file in the  ``guwlib/data`` folder.

        :return: (dict) Material properties.
        """
        script_path = os.path.abspath(__file__)
        parent_dir = os.path.dirname(os.path.dirname(script_path))
        json_path = os.path.join(parent_dir, 'data', 'piezoelectric_materials.json')
        material_properties = extract_properties_from_json(json_file_path=json_path,
                                                           target_item_name=self.name)
        validate_piezoelectric_material(material_properties)
        return material_properties


def validate_isotropic_material(material_properties):
    """
    Validation wrapper to check if the right key-value pairs are stored in an isotropic material properties' dict.

    :raises: ValueError: If the properties dict is not valid.
    """
    required_key_value_pairs = {'density': float,
                                'youngs_modulus': float,
                                'poissons_ratio': float}

    for material_property, expected_type in required_key_value_pairs.items():
        if material_property not in material_properties:
            raise ValueError("Missing '{}' attribute.".format(material_property))
        if not isinstance(material_properties[material_property], expected_type):
            raise ValueError("Invalid type for '{}'. Expected {}.".format(material_property, expected_type))


def validate_piezoelectric_material(material_properties):
    """
    Validation wrapper to check if the right key-value pairs are stored in a piezoelectric material properties' dict.

    :raises: ValueError: If the properties dict is not valid.
    """
    required_key_value_pairs = {
        'density': float,
        'elastic_engineering_constants': list,
        'dielectric_orthotropic': list,
        'piezoelectric_strain': list
    }

    required_list_lengths = {
        'elastic_engineering_constants': 9,
        'dielectric_orthotropic': 3,
        'piezoelectric_strain': 18
    }

    for material_property, expected_type in required_key_value_pairs.items():
        if material_property not in material_properties:
            raise ValueError("Missing '{}' attribute.".format(material_property))
        if not isinstance(material_properties[material_property], expected_type):
            raise ValueError("Invalid type for '{}'. Expected {}.".format(material_property, expected_type))

    for material_property, expected_length in required_list_lengths.items():
        if len(material_properties[material_property]) != expected_length:
            raise ValueError(
                "Invalid length for '{}'. Expected {} elements.".format(material_property, expected_length))


def extract_properties_from_json(json_file_path, target_item_name):
    """
    Helper function to extract a dictionary of properties for a given item name from a *.JSON file.

    :param str json_file_path: Path to the *.JSON file.
    :param str target_item_name: Name of the item for which the properties dictionary is to be extracted.

    :return: (dict) Item properties.
    """
    if not os.path.exists(json_file_path):
        raise IOError("{} not found.".format(json_file_path))

    try:
        with open(json_file_path, 'r') as file:
            item_list = json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding {}: {}".format(json_file_path, e))

    if target_item_name not in item_list:
        raise ValueError("Item '{}' not found in {}.".format(target_item_name, json_file_path))

    item_properties = item_list.get(target_item_name, {})
    return item_properties


# if __name__ == "__main__":
#     # Example usage
#     try:
#         isotropic_material = IsotropicMaterial("AluminumAlloy6061")
#         print(f"Isotropic Material Properties: {isotropic_material.properties}")
#         #
#         # isotropic_material = IsotropicMaterial("AluminumAlloy050")
#         # print(f"Isotropic Material Properties: {isotropic_material.properties}")
#
#         piezoelectric_material = PiezoElectricMaterial("PIC255")
#         print(f"Piezoelectric Material Properties: {piezoelectric_material.properties}")
#
#         # Example of handling an error
#         invalid_material = Material("InvalidMaterial")
#
#     except ValueError as e:
#         print(f"Error: {e}")
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
