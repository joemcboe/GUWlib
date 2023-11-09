MATERIAL_PROPERTIES = {
    "aluminum": {
        "type": "isotropic",
        "density": 2700,  # kg/m3
        "youngs_modulus": 70 * 1e9,  # N/m2
        "poissons_ratio": 0.33,  # -
    },
    "silver": {
        "type": "isotropic",
        "density": 10800,  # kg/m3
        "youngs_modulus": 76 * 1e9,  # N/m2
        "poissons_ratio": 0.37,  # -
    },
    "pic255": {
        "type": "piezo_electric",
        "density": 7800,  # kg/m3
        "elastic_engineering_constants_table":
            ((62.5e9, 62.5e9, 52.63e9,          # E1 E2 E3
              0.34, 0.34, 0.34,                 # nu12 nu13 nu23
              23.3e9, 23.3e9, 23.3e9),),        # G12 G13 G23
        "dielectric_orthotropic_table": ((1.549e-08, 1.549e-08, 1.594e-08),),
        "piezo_electric_strain_table": ((0.00, 0.00, 0.0, 0.0, 550e-12, 0.0,
                                         0.00, 0.00, 0.0, 0.0, 0.0, 550e-12,
                                         -180e-12, -180e-12, 400e-12, 0.0, 0.0, 0.0),),
        #                               d1-11, d1-22, d1-33, d1-12, d1-13, d1-23
        #                               d2-11, d2-22, d2-33, d2-12, d2-13, d2-23
        #                               d3-11, d3-22, d3-33, d3-12, d3-13, d3-23
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
