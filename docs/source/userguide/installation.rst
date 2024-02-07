Setup / Installation
=====================

There are two ways to use GUWlib:

- on the local computer
- on a cluster (for computationally intensive models). 

Based on the needs, different dependencies need to be fullfilled. The setup process for local solving and additional installation steps for solving models on a cluster are described below.


Setup for use on local PC
--------------------------

1. **ABAQUS:**
 
   Ensure that `ABAQUS <https://www.3ds.com/products/simulia/abaqus/cae>`_ (2019 or later version) is installed. For model generation only, the student version (`Learning Edition <https://www.3ds.com/edu/education/students/solutions/abaqus-le>`_) of ABAQUS is sufficient (solving in the Learning Edition is restricted to 1000 nodes).

2. **Python Requirements:**
 
   If batch processing scripts are to be used, `Python <https://www.python.org/downloads/>`_ (Version 3+) is necessary as well as the Python package `NumPy <https://numpy.org/>`_. NumPy can be installed e.g. with pip: ::
   
	$ pip install numpy
   
3. **Clone or Download Repository:**
 
   Clone or download the `GitLab repository <https://git.rz.tu-bs.de/j.froboese/GUW>`_ into your working directory. The downloaded files have the following structure:

   .. code-block::

       GUW\
       ├───docs\
       │   └───...
       └───python\
           │   batch_local.py
           │   batch_remote.py
           │   preview_model.py
           │
           ├───guwlib\
           │   ├───data\
           │   ├───functions_batch\
           │   ├───functions_cae\
           │   ├───functions_cluster\
           │   ├───functions_odb\
           │   ├───functions_utility\
           │   └───guw_objects\
           ├───results\
           └───models\
               └───examples\
                       example_01.py
                       example_02.py

   The ``python`` folder contains the ``guwlib`` package, along with folders for models (``models``) and results (``results``). Additionally, three scripts (``batch_local.py``, ``batch_remote.py``, ``preview_model.py``) are provided for automating model creation, solving, and post-processing, as well as for quickly opening a model in ABAQUS.

5. **Setting ABAQUS Working Directory:**
 
   ABAQUS can access the ``guwlib`` package and execute model scripts only when the ABAQUS working directory is set to the ``.../guwlib/python/`` directory or when ABAQUS is launched from this directory. To set the working directory:

   - Launch ABAQUS and navigate to `File` -> `Set working directory...`, then change it to the path where ``.../guwlib/python/`` is located.
   - On Windows, the ABAQUS shortcut can also be modified: right-click on the ABAQUS/CAE shortcut -> `Properties` -> `Start in` and set it to the ``.../guwlib/python/`` path.
	
	
Setup for use on TU BS Phoenix Cluster 
---------------------------------------

1. **Python Requirements:**
 
   An installation of `Python <https://www.python.org/downloads/>`_ (Version 3.6+) on the local computer is necessary. Additionally, the `Paramiko <https://www.paramiko.org/>`_ package for SSH communication needs to be available on the local computer and can be installed via pip: ::
	
		$ pip install paramiko
	
2. **ABAQUS:**
 
   ABAQUS is available on the Phoenix cluster by default (versions 2016, 2017, 2018, 2019, 2023). For working on the cluster only, no local installation of ABAQUS is necessary.

3. **Clone or Download Repository:**

   Clone or download the `GitLab repository <https://git.rz.tu-bs.de/j.froboese/GUW>`_ to both a local working directory as well as any working directory on the Phoenix BeeGFS filesystem, i.e. the ``/work/<username>`` directory. The latter can be done as follows, for example:	

   - Connect to TU BS network via VPN (if not already connected).
   - Open a terminal and connect to Phoenix: 

     .. code-block:: text
     
	    $ ssh <username>@phoenix.hlr.rz.tu-bs.de

   - Navigate to the work directory:

     .. code-block:: text
	 
        [<username>@login01 ~] cd /work/<username>

   - Clone the GitLab repository:
   
     .. code-block:: text

        [<username>@login01 /work/<username>] git clone https://git.rz.tu-bs.de/j.froboese/GUW.git

   The working directory of GUWlib on the Phoenix cluster would now be ``/work/<username>/GUW/python/``.

   Another option is to use a GUI like `FileZilla <https://filezilla-project.org/download.php?platform=win64>`_ to copy the directory from the local PC to Phoenix.
   
   Information on how to use the batch processing functions with the cluster, read :ref:`Batch processing (cluster)`.

	




