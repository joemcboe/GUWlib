Batch processing (local)
========================

If several model scripts are to be processed (model generation, solving and result extraction), it makes sense to automate the process (batch processing). The GUWlib package provides some :ref:`wrapper functions <Batch wrapper functions (local)>` for this purpose, which accept a list of model files and work through the required steps in sequence. For a local pipeline, this mainly includes calling ABAQUS/CAE and ABAQUS/Explicit with the respective input files or scripts.

Using the batch processing script (local)
-----------------------------------------

The script ``...\GUW\python\batch_local.py`` provides a customizable outline of how you may use the :ref:`batch functions <Batch wrapper functions (local)>` to build and solve a list of models as well as to extract the results as .NPZ files in an automated manner. Below is an example where the script is set up to 

- build the model files ``models\examples\example_01.py``,  ``models\examples\example_02.py`` and ``models\examples\tutorial.py`` in ABAQUS/CAE, 
- solve the simulations one after the other with ABAQUS/Explicit on 10 cores in parallel each,
- export the history output data to NumPy binaries.

.. literalinclude:: ../../../python/batch_local.py
   :language: python
   :lines: 9-

All files (.PY, .INP, .ODB, .NPZ and other files written by ABAQUS) will be stored in directories, named after the model files and the respective load cases, inside the ``results\`` folder.


----------------------------------------------------------------------------------------


Batch wrapper functions (local)
-------------------------------

..
	.. toggle::

.. autofunction:: guwlib.functions_batch.local.build_and_solve

.. autofunction:: guwlib.functions_batch.local.extract_results




   
   





