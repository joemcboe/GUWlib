# GUW
A python module to simulate Guided Ultrasonic Wave (GUW) propagation and defect interaction in simple plates using ABAQUS. 

## Usage
Please refer to the documentation on GitLab pages: [GUWlib documentation](https://guw-j-froboese-7e83bff35047dd42a62d8fb269d632ab5d9e6a1d5b2d7867.gitlab-pages.rz.tu-bs.de/index.html).


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
