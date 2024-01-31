"""
This package contains the code that is dispatched to build the FE model in ABAQUS using the ABAQUS/CAE scripting
interface. It thereby represents the interface between the data container (guwlib.fe_model.FEModel) and
the actual ABAQUS model.

Since the modelling process depends very much on whether the transducers are to be represented as point forces or
as piezo-electric elements, two separate functions are implemented:

    - build_abaqus_model_point_force(model)
    - build_abaqus_model_piezo_electric(model)

and their respective bottom-level (ABAQUS/CAE interface) helper functions.
"""