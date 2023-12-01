import json
import os


class Material:
    def __init__(self, material_name, material_type):
        self.material_name = material_name
        self.material_type = material_type
        self.properties = self.load_material_properties()

    def load_material_properties(self):
        script_path = os.path.abspath(__file__)
        parent_dir = os.path.dirname(os.path.dirname(script_path))

        if self.material_type == 'isotropic':
            json_path = os.path.join(parent_dir, 'data\\isotropic_materials.json')
            check_file_existence(json_path)
            material_properties = get_material_properties(json_path, self.material_name)
            validate_isotropic_material(material_properties)
            return material_properties

        elif self.material_type == 'piezoelectric':
            json_path = os.path.join(parent_dir, 'data\\piezoelectric_materials.json')
            check_file_existence(json_path)
            material_properties = get_material_properties(json_path, self.material_name)
            validate_piezoelectric_material(material_properties)
            return material_properties

        else:
            raise ValueError("Invalid material type. Use 'isotropic' or 'piezoelectric'.")


def check_file_existence(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("{} not found.".format(file_path))


def get_material_properties(json_path, material_name):
    try:
        with open(json_path, 'r') as file:
            material_list = json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding {}: {}".format(json_path, e))
    if material_name not in material_list:
        raise ValueError("Material '{}' not found in {}.".format(material_name, json_path))

    material_properties = material_list.get(material_name, {})
    return material_properties


def validate_isotropic_material(material_properties):
    required_attributes = {'density': float, 'youngs_modulus': float, 'poissons_ratio': float}
    validate_attributes(material_properties, required_attributes)


def validate_piezoelectric_material(material_properties):
    # Add validation logic for piezoelectric materials if needed
    pass


def validate_attributes(material_properties, required_attributes):
    for attribute, expected_type in required_attributes.items():
        if attribute not in material_properties:
            raise ValueError("Missing '{}' attribute.".format(attribute))
        if not isinstance(material_properties[attribute], expected_type):
            raise ValueError("Invalid type for '{}'. Expected {}.".format(attribute, expected_type))

# if __name__ == "__main__":
#     # Example usage
#     try:
#         isotropic_material = Material("AluminumAlloy6061", "isotropic")
#         print(f"Isotropic Material Properties: {isotropic_material.properties}")
#
#         piezoelectric_material = Material("PIC255", "piezoelectric")
#         print(f"Piezoelectric Material Properties: {piezoelectric_material.properties}")
#
#         # Example of handling an error
#         invalid_material = Material("InvalidMaterial", "isotropic")
#
#     except ValueError as e:
#         print(f"Error: {e}")
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
