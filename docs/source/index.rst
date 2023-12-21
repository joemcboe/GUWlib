.. GUWlib documentation master file, created by
   sphinx-quickstart on Tue Dec 19 10:53:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================================================
GUWlib - A python module for Guided Ultrasonic Wave simulation in thin plates
=============================================================================


About 
=====

**GUWlib** is a Python module that helps setting up models in the
Finite Element software ABAQUS for the simulation of Guided
Ultrasonic Waves (GUW) in thin plates. After importing ``guwlib``,
you can define simulations by writing simple Python scripts, in
which geometry and loading parameters are set. These files can then be
run in ABAQUS/CAE to generate the FE model.

..
   |pic1| --> |pic2|

   .. |pic1| image:: _static/testpic.png
      :width: 45%

   .. |pic2| image:: _static/testpic.png
      :width: 45%

The **GUWlib** module utilizes the ABAQUS `Scripting Interface
<https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.6/books/cmd/default.htm?startat=pt02ch04.html>`_
to automate the modelling work in ABAQUS/CAE. It also handles some essential considerations,
like choosing an appropriate mesh density based on your input parameters.






Features
========
This module is capable of:

- test
- test

This module right now isn't capable to:

- test


Content
==================================

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   usage/installation
   usage/first

.. toctree::
   :maxdepth: 1
   :caption: Workflow

   workflow/general
   workflow/modelfiles
   workflow/viewing
   workflow/solving
   workflow/postprocess


.. toctree::
   :maxdepth: 1
   :caption: Objects

   guwobjects/FEModel
   guwobjects/Plate
   guwobjects/Defects
   guwobjects/Transducer
   guwobjects/Signal
   guwobjects/Material
   guwobjects/Loadcase

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/first






   



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

