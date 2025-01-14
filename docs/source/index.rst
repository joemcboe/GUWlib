.. GUWlib documentation master file, created by
   sphinx-quickstart on Tue Dec 19 10:53:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================================================
GUWlib - Python package for Guided Ultrasonic Wave simulation with ABAQUS
=============================================================================


About
=====

**GUWlib** is a Python package that helps setting up models in the
Finite Element software ABAQUS for the simulation of Guided
Ultrasonic Wave (GUW) propagation and defect interaction in thin plates.
Simulations can be defined by simple Python scripts, which set the
geometry and loading parameters. These scripts can then be run in
ABAQUS/CAE to generate the FE model.

..
    .. image:: _static/overview_index.svg
       :width: 100%


The ABAQUS `scripting interface
<https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.6/books/cmd/default.htm?startat=pt02ch04.html>`_
is utilized to automate the modelling work in ABAQUS/CAE. Mesh size can be controlled through easy-interpretable parameters.
The required calculations are automatically performed using the stored material data.
Additionally, functions for the batch processing of models are provided, simplifying the generation, solving, and
post-processing of finite element models (either local or on a computer cluster).


Features
========

**Geometry**:

- rectangular plates
- circular through-thickness holes
- through-thickness cracks

**Meshing**:

- mesh size determination based on user-defined parameters (number of elements per wavelength / in thickness direction) and dispersion data
- appropriate partitioning of the geometry to ensure well-structured hexahedral meshes, even around defects and transducers

**Excitation**:

- transducers represented by concentrated forces, exciting either symmetric, asymmetric, or both Lamb wave modes
- (transducers represented by circular piezo-electric patches with input/output voltage)
- transducer signals: burst, unit impulse can be applied to each transducer individually as *load cases*

**Materials**:

- import of isotropic and piezoelectric material definitions through a JSON file interface
- import of dispersion data, generated by `DLR dispersion calculator <https://www.dlr.de/zlp/en/desktopdefault.aspx/tabid-14332/24874_read-61142>`_ through a TXT file interface

**Batch processing**:

- local pipeline: building and solving the models with the specified number of cores, extract history and field output and save to NumPy binary files
- cluster pipeline: wrappers for automatic upload of model scripts to the cluster via SSH, parallel solving of multiple models on multiple cores, post-processing and results download


Content
==================================

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   userguide/installation
   userguide/general
   userguide/modelfiles
   userguide/batch_local
   userguide/batch_cluster


.. toctree::
   :maxdepth: 1
   :caption: Components

   guwobjects/FEModel
   guwobjects/Plate
   guwobjects/Defects
   guwobjects/Transducer
   guwobjects/Signal
   guwobjects/Material
   guwobjects/Loadcase

..
   .. toctree::
      :maxdepth: 3
      :caption: AutoAPI

      autoapi/guwlib/index
      autoapi/guwlib/fe_model/index
      autoapi/guwlib/guw_objects/defects/index
      autoapi/guwlib/guw_objects/plate/index
      autoapi/guwlib/guw_objects/transducer/index
      autoapi/guwlib/guw_objects/signal/index


..
	.. toctree::
	   :maxdepth: 1
	   :caption: Examples

	   examples/first


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

