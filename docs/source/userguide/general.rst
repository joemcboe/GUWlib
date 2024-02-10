General workflow
=================

The general workflow when working with the Finite Element (FE) program ABAQUS (and the GUWlib package) can be broken down into the following steps:

.. image:: ../_static/workflow_general_html.svg
    :width: 100%

- **Preprocessing:**
   Involves creating the Finite Element model, including generating the geometry, defining material parameters, specifying loads, and performing meshing. This phase is often labor-intensive for the user. 
   
   GUWlib's core purpose is to simplify the preprocessing phase by providing a user-friendly interface to the ABAQUS `Python scripting API <https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.6/books/cmd/default.htm?startat=pt02ch04.html>`_, specifically tailored for creating models for Guided Ultrasonic Wave (GUW) simulation. Users can compose a *model script* where they assemble a model from predefined "building blocks" such as plates, defects, and piezoelectric transducers. This *model script* can then be executed in ABAQUS/CAE, where ABAQUS/CAE constructs the model and generates so-called .INP files. The next section, :ref:`Writing a model script`, describes how models can be defined with GUWlib.

- **Solving:**
   In the solving phase, the numerical solutions for the previously defined model's equation systems are computed. The .INP files are loaded into the solver, typically ABAQUS/Explicit, and the calculations are performed. ABAQUS/Explicit writes Output-Database files (.ODB) containing the requested result data, e.g., displacement history of transducer nodes (history output) or displacements on the entire plate's top surface (field output).

- **Post-Processing:**
   The results from the solver need to be interpreted and processed. ABAQUS stores the results in its proprietary .ODB format, which can be visualized and analyzed using ABAQUS/Viewer. 
   
   To enable further processing of result data in Python, GUWlib provides functions to effortlessly and automatically read and store the result data (history/field) in the NumPy format (.NPZ).

The entire process of preprocessing, solving, as well as the process of result extraction can be automated using the batch scripts provided by GUWlib. The sections :ref:`Batch processing (local)` and :ref:`Batch processing (cluster)` deal with the topic on how to use the batch processing scripts on the local PC or the Phoenix cluster, respectively. 



