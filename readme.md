# GUWlib
More detailed documentation on GitLab pages: [GUWlib documentation](https://guw-j-froboese-7e83bff35047dd42a62d8fb269d632ab5d9e6a1d5b2d7867.gitlab-pages.rz.tu-bs.de/index.html). This project is no longer maintained from 02/2024.

## Description
<!--- Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors. --->

A python package to simulate Guided Ultrasonic Wave (GUW) propagation and defect interaction in simple plates using ABAQUS. The package facilitates the setup of models through simple Python scripts, defining geometry and loading parameters for subsequent execution in ABAQUS/CAE.

#### Key Features:

- **Geometry**: Supports rectangular plates, circular through-thickness holes, and through-thickness cracks.
- **Meshing**: Allows mesh size determination based on user-defined parameters and dispersion data, ensuring optimal hexahedral meshes around defects and transducers.
- **Excitation**: Represents transducers with concentrated forces, enabling the excitation of symmetric, asymmetric, or both Lamb wave modes. Transducer signals, such as burst or unit impulse, can be applied individually as load cases.
- **Materials**: Imports isotropic and piezoelectric material definitions through a JSON file interface, along with dispersion data generated by the DLR dispersion calculator.
- **Batch Processing**: Provides local and cluster pipelines for automated model building, solving, post-processing, and results extraction.


<!--- ## Visuals --->
<!--- Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method. --->
## Example
<!--- Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README. --->

```python
from guwlib import *

class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters
        self.max_frequency = 100e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')
        self.plate = IsotropicRectangularPlate(material=aluminum, thickness=3e-3, width=100e-3, length=100e-3)

        # setup two transducers
        self.transducers = [
            CircularTransducer(position_x=20e-3, position_y=50e-3, position_z='symmetric', diameter=16e-3),
            CircularTransducer(position_x=80e-3, position_y=50e-3, position_z='symmetric', diameter=16e-3)]

        # setup defects
        self.defects = [Crack(position_x=50e-3, position_y=75e-3, length=15e-3, angle_degrees=12),
                        Hole(position_x=60e-3, position_y=30e-3, diameter=8e-3)]

        # set up the time / loading information (burst on 1st transducer)
        burst = Burst(center_frequency=100e3, n_cycles=3)
        transducer_signals = [burst, None]
        self.load_cases = [LoadCase(name='control_step', duration=0.25e-3, transducer_signals=transducer_signals, output_request='field')]
        
if __name__ == "__main__":
    Model().setup_in_abaqus()
```

Running this script in ABAQUS will set up the following FE model of a 100 x 100 x 3 mm aluminum plate:

<p>
  <img src="./docs/source/_static/minimal_example_model.png" width="500"  />
  <img src="./docs/source/_static/minimal_example_model_mesh.png" width="500" />
</p>

Solving in ABAQUS yields the following result (excitation of ≈ 100 kHz symmetric Lamb waves):


## Installation and dependencies
No installation required. To work with GUWlib, it is only necessary to copy this repository into a local working directory.
Basic external requirements for solving FE models locally:
- [ ] ABAQUS 2019 (or later)
- [ ] Python 3 and [NumPy](https://numpy.org/) (for batch processing handlers)

The project includes additional functions for batch processing of FE models on the [TUBS Phoenix cluster](https://doku.rz.tu-bs.de/doku.php?id=hlr:phoenix), which requires additional dependencies:
- [ ] User account for the Phoenix cluster, (VPN) connection to the TU BS network
- [ ] Python packages: [paramiko](https://www.paramiko.org/) (for SSH connections)

<!--- Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection. --->



## Project status
<!--- If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers. -->

This project is no longer maintained from 02/2024. Some features are currently not fully integrated or need revision:
- [ ] Piezo-electric transducers, which require an implicit solver (at least for the piezo-electric part of the model). 
    The option of building the model with piezo-electrical transducers is implemented in principle, however, the bottom-level
    ABAQUS/Python API code is not up-to-date with the rest of the project.
- [ ] The helper function for field-output export does not export node-connectivity data.

The modular structure should make it easy to add features. A few inspirations for what could be added with little to moderate effort are:
- [ ] Option to specify the solver and element type. Currently, the solver is always set to ABAQUS/Explicit and element type is always set
    to ``C3D8R``.
- [ ] Option to implement the excitation as a prescribed nodal displacement (currently, excitation is always realized as a concentrated force).
- [ ] Implementation of more signals, such as a "read from CSV data" type signal that allows for user-defined signals.
- [ ] Options to specify the interval with which field output is written to the output database. Currently, 
    field output is written at intervals of 10 * max time increment.
- [ ] More options to request field output for a load case. Currently, users can only request field output for the 
    top surface of the plate, but not for e.g. the whole plate.
- [ ] Anisotropic material for the plate.
- [ ] More types of defects.
- [ ] Non-rectangular or polygon-shaped plates.
- [ ] Multi-layered anisotropic plates.

Feel free to fork the project and add your own functionality.
<!---
    ```mermaid
    classDiagram
        note "note 01"
        note for model "test\ntest\ntest"
        steps --|> model : time data
        plate --|> model : spatial data
        class model{
            - max_frequency
            - model_mode
            - nodes_per_wavelength
            - elements_in_thickness_direction
            setup_in_abaqus()
        }
        class steps{
        }
        class plate{
        }
    ```
--->
