Material
=======

``Material``
--------------
.. toggle::

    .. autoclass:: guwlib.guw_objects.Material

------------------------------------------------------

``IsotropicMaterial``
-----------------------
.. autoclass:: guwlib.guw_objects.IsotropicMaterial
    :show-inheritance:

------------------------------------------------------

``PiezoElectricMaterial``
-----------------------
.. autoclass:: guwlib.guw_objects.PiezoElectricMaterial
    :show-inheritance:


-------------------------------------------------------

Adding materials to the material library
-----------------------------------------

A lot of materials are already available by default and can be loaded by providing their name.
All material data is stored in the *data* directory (``guwlib/data/``) in respective .JSON
and .TXT files. By default, the content of this directory looks like this:

.. code-block:: none

    guwlib/
    │   ...
    │
    ├───data/
    │       AluminumAlloy1100_A_Lamb.txt
    │       AluminumAlloy1100_S_Lamb.txt
    │       isotropic_materials.json
    │       piezoelectric_materials.json
    │
    ├───...

For each material class, the respective .JSON file stores material properties,
like Youngs modulus and density. Please inspect these files to see which materials are
available. To add your own materials, follow the format of the existing entries.


If a material is used for the :class:`Plate`, GUWlib will
also try to obtain analytical dispersion data for this material. This dispersion data has to
be stored in two .TXT files for each material, and the files have to be named after this
convention:

    - ``<material_name>_S_Lamb.txt`` (symmetric modes data)
    - ``<material_name>_A_Lamb.txt`` (antisymmetric modes data)

These files can be created with `DLR Dispersion Calculator
<https://www.dlr.de/zlp/en/desktopdefault.aspx/tabid-14332/24874_read-61142/>`_.
Make sure that your .TXT files are formatted the same way as the existing example files
for 1100 aluminum alloy.






