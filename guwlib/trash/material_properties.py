"""
This file stores material properties. If the material is used for an isotropic plate, a *.txt file generated with
Dispersion Calculator containing the dispersion curves must be in this folder.
"""

from guwlib.guw_objects.material import Isotropic, PiezoElectric


MATERIAL_PROPERTIES = {
    # isotropic materials ----------------------------------------------------------------------------------------------
    # 
    # "isotropic_material_name": {
    #     "type": Isotropic,
    #     "density": density,
    #     "young's_modulus": young's_modulus,
    #     "poisson's_ratio": poisson's_ratio,
    # },
    #
    "aluminum": {
        "type": Isotropic,
        "density": 2700,
        "young's_modulus": 70 * 1e9,
        "poisson's_ratio": 0.33,
    },
    "silver": {
        "type": Isotropic,
        "density": 10800,
        "young's_modulus": 76 * 1e9,
        "poisson's_ratio": 0.37,
    },

    # piezoelectric materials ------------------------------------------------------------------------------------------
    #
    # "piezo_electric_material_name": {
    #     "type":
    #         PiezoElectric,
    #     "density":
    #         density,
    #     "elastic_engineering_constants_table":
    #         ((E1,   E2,   E3,
    #           nu12, nu13, nu23,
    #           G12,  G13,  G23),),
    #     "dielectric_orthotropic_table":
    #         ((1.549e-08, 1.549e-08, 1.594e-08),),
    #     "piezo_electric_strain_table":
    #         ((d1-11, d1-22, d1-33, d1-12, d1-13, d1-23,
    #           d2-11, d2-22, d2-33, d2-12, d2-13, d2-23,
    #           d3-11, d3-22, d3-33, d3-12, d3-13, d3-23)),
    # },
    #
    "pic255": {
        "type":
            PiezoElectric,
        "density":
            7800,
        "elastic_engineering_constants_table":
            ((62.5e9, 62.5e9, 52.63e9,
              0.34, 0.34, 0.34,
              23.3e9, 23.3e9, 23.3e9),),
        "dielectric_orthotropic_table":
            ((1.549e-08, 1.549e-08, 1.594e-08),),
        "piezo_electric_strain_table":
            ((0.00, 0.00, 0.0, 0.0, 550e-12, 0.0,
              0.00, 0.00, 0.0, 0.0, 0.0, 550e-12,
              -180e-12, -180e-12, 400e-12, 0.0, 0.0, 0.0),),
    },
}
