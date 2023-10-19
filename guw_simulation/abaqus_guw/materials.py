MATERIAL_PROPERTIES = {
    "aluminum": {
        "density": 2700,  # kg/m3
        "youngs_modulus": 70 * 1e9,  # N/m2
        "poissons_ratio": 0.33,  # -
    },
    "pic255": {
        "density": 7800,  # kg/m3
        "youngs_modulus": 154 * 1e9,  # N/m2
        "poissons_ratio": 0.31,  # -
    },
}


def get_material_properties(material_name):
    # Try to retrieve the properties for the given material name
    try:
        properties = MATERIAL_PROPERTIES[material_name]
        return properties
    except KeyError:
        # Raise an error if the material is not known
        raise ValueError("Material '{}' is not in the database of known materials.".format(material_name))
