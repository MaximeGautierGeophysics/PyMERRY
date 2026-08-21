# PyMERRY v2.0

**PyMERRY** (Python solution for an improved interpretation of Electrical Resistivity Tomography images) is a Python tool designed to assess the reliability and uncertainty of 2D Electrical Resistivity Tomography (ERT) images.

PyMERRY is a post-processing tool that can be applied to 2D resistivity models obtained from ERT inversion. It estimates the reliability of the resistivity model by computing coverage and resistivity errors associated with the measurement accuracy and the spatial resolution of the model.

The methodology is described in:

> Gautier, M., Gautier, S., & Cattin, R. (2023).  
> PyMERRY: A Python solution for an improved interpretation of electrical resistivity tomography images.  
> *Geophysics*, 89(1), F23–F39.  
> https://doi.org/10.1190/geo2023-0105.1

If you use PyMERRY in your research, please cite this publication.

---

## Important information about PyMERRY v2.0

This repository contains **PyMERRY v2.0**.

The original version of PyMERRY was published together with the scientific article and an example without topography.

**PyMERRY v2.0 now takes topography into account.**

A new example using a 2D triangular mesh including topography is provided in this repository.
If topography is detected a notification is displayed when code is running, DOI coefficient are automatically set to 0.2.

> **Important:** The `user_manual.pdf` included in this repository was written for an earlier version of PyMERRY. It therefore states that topography is not taken into account. This information is outdated for PyMERRY v2.0.
>
> For the current functionality, please refer to the v2.0 code and to the examples provided in this repository.

---

# Repository structure

The main repository is organized as follows:

```text
PyMERRY/
│
├── README.md
├── CITATION.cff
├── .gitignore
│
├── run_pymerry.py
├── create_synthetic_data_with_topo.py
│
├── parameter_file_template.txt
│
├── docs/
│   ├── user_manual.pdf
│   ├── agu_2023.pdf
│   └── gautier_et_al_2023.pdf
│
├── installation/
│   ├── pymerry_env_linux_fedora.yml
│   ├── pymerry_env_linux_ubuntu.yml
│   ├── pymerry_env_linux_macos.yml
│   └── pymerry_env_linux_windows.yml
│
├── tools/
│   └── PyMERRY.py
│
└── examples/
    │
    ├── example_without_topography/
    │   ├── input_data/
    │   │   ├── ert_data.dat
    │   │   ├── mesh_cells_table.txt
    │   │   ├── mesh_nodes_table.txt
    │   │   └── model.txt
    │   │
    │   ├── parameters.txt
    │   └── results/
    │       └── ...
    │
    └── example_with_topography/
        ├── input_data/
        │   ├── ert_data.dat
        │   ├── mesh_cells_table.txt
        │   ├── mesh_nodes_table.txt
        │   └── model.txt
        │
        ├── parameters.txt
        └── results/
            └── ...
```

# Installation

PyMERRY requires a Python environment with the packages necessary to run the code.

Environment files (`.yml`) are provided in the `installation` directory for the supported operating systems:

```text
installation/
├── pymerry_env_linux_fedora.yml
├── pymerry_env_linux_ubunto.yml
├── pymerry_env_linux_macos.yml
└── pymerry_env_linux_windows.yml
```

These files can be used to create the required Python environment using Conda.

The complete installation procedure, including the creation and activation of the Python environment and the installation of the required dependencies, is described in detail in:

```text
docs/user_manual.pdf
```

**Please refer to the user manual before running PyMERRY for the first time.**

> **Note:** PyMERRY uses multiprocessing during the error assessment. For this reason, the code should not be run directly from a Jupyter Notebook. Spyder or execution from a terminal is recommended.

# How PyMERRY works

PyMERRY uses:

- ERT data;
- a 2D triangular mesh;
- a resistivity model associated with the mesh cells;
- measurement accuracy parameters;
- Depth of Investigation (DOI) parameters.

The general workflow is:

```text
Input data
    │
    ├── ERT data
    ├── 2D triangular mesh
    └── Resistivity model
             │
             ▼
      Parameter file
             │
             ▼
       run_pymerry.py
             │
             ▼
          PyMERRY
             │
       ┌─────┴─────┐
       ▼           ▼
   Coverage    Error assessment
       │           │
       └─────┬─────┘
             ▼
          Results
```

# Input files

PyMERRY requires four input files describing the ERT dataset, the 2D triangular mesh and the resistivity model.

The input files must be organized as follows:

```text
input_data/
├── ert_data.dat
├── mesh_cells_table.txt
├── mesh_nodes_table.txt
└── model.txt
```

## ert_data.dat
This file contains the ERT data used during the inversion process. This .dat file type is commonly used in ERT and describe the electrodes positions and measurements. (for a use in the PyGIMLi geophysical library, please visit: https://www.pygimli.org/)
For example : 
```text
21
# x y z
-15.0    0.0    0.0
-13.5    0.0    0.0
-12.0    0.0    0.0
...
0.0      0.0    0.0
...
12.0     0.0    0.0
13.5     0.0    0.0
15.0     0.0    0.0
171
# a b m n err i ip iperr k r rhoa u valid
1    2    3    4    1.0000e-02    0.0    0.0    0.0    -28.27       0.0    93.07    0.0    1
2    3    4    5    1.0000e-02    0.0    0.0    0.0    -28.27       0.0    92.90    0.0    1
3    4    5    6    1.0000e-02    0.0    0.0    0.0    -28.27       0.0    92.78    0.0    1
...
6    7    8    9    1.0000e-02    0.0    0.0    0.0    -28.27       0.0    95.22    0.0    1
...
1    2    20   21   1.0568e-02    0.0    0.0    0.0    -32232.74   0.0    56.34    0.0    1
0
```

## Mesh description
A mesh is described using tables of cells and nodes.
If you save a PyGIMLi mesh object in a 'mesh' variable, you can use the dedicated method available in the PyMERRY.py code to create and save these tables.
```text
import numpy as np
import tools.PyMERRY as PM

nodes_table, cells_table, = PM.InputTools.mesh_tables(mesh)
np.savetxt(os.path.join("input_data_with_topo", "mesh_cells_table.txt"),
           cells_table, delimiter=";", fmt=["%d", "%d", "%d", "%d"])
np.savetxt(os.path.join("input_data_with_topo", "mesh_nodes_table.txt"),
           nodes_table, delimiter=";", fmt=["%d", "%.6f", "%.6f", "%.6f"])

```

### mesh_cells_table.txt
This file defines the triangular cells of the 2D mesh.
Each line contains four integer values separated by semicolons:
```text
0;163;233;270
1;3;763;4
2;229;237;132
3;722;837;13
4;719;15;14
5;837;14;13
...
30;315;148;28
31;291;234;271
32;154;249;319
33;38;123;193
...

```

### mesh_nodes_table.txt
The file `mesh_nodes_table.txt` contains the coordinates of the nodes of the 2D triangular mesh.
Each line contains four values separated by semicolons:
```text
0;-30.000000;0.000000;0.000000
1;-29.000000;0.576000;0.000000
2;-28.500000;0.693000;0.000000
3;-28.000000;0.611000;0.000000
4;-27.500000;0.682000;0.000000
5;-27.000000;0.716000;0.000000
...
20;-19.500000;1.314000;0.000000
21;-19.000000;1.539000;0.000000
22;-18.500000;1.326000;0.000000
23;-18.000000;1.247000;0.000000
24;-17.500000;1.056000;0.000000
25;-17.000000;0.845000;0.000000
...
```


## model.txt
The file `model.txt` contains the electrical resistivity value associated with each mesh cell.

Each line contains two values separated by a semicolon:

```text
0;95.6856
1;72.4285
2;97.3476
3;72.9112
4;72.9878
5;72.9398
6;73.0248
7;78.3813
8;97.1180
9;72.0726
10;73.9295
11;97.2638
12;75.8160
...
20;72.5509
21;72.4048
22;105.5689
...
```

# Output files

When PyMERRY is run, the results are saved in the output directory specified in the parameter file.

For example:

```text
-> directory to save results : results
```

## Temporary files

During a PyMERRY run, a temporary directory ```temp``` is created to store intermediate files required for the calculation.

These files are only used during the execution of PyMERRY and are automatically removed when the calculation is completed.

The temporary files are therefore not part of the final results and do not need to be manually deleted.

# Parameter file

PyMERRY uses a parameter file to define the input files, output directory, and calculation parameters.

A parameter file template is provided in the repository:
```text
parameter_file_template.txt
```
The examples also contain their own parameter files:

examples/example_without_topography/parameters.txt  
examples/example_with_topography/parameters.txt  

Users are strongly encouraged to start from the provided template or from one of the example parameter files.

The parameter file has a fixed structure. **Do not add, delete, or move lines in the parameter file.** Only modify the values located after `:` on the lines explicitly marked with `->`.

For example:
```text
-> mesh cells table  : input_data/mesh_cells_table.txt
-> mesh nodes table  : input_data/mesh_nodes_table.txt
-> resistivity model : input_data/model.txt
-> data file         : input_data/ert_data.dat
```
The paths should be adapted to the location of the user's input files.

The output directory can also be modified:
```text
-> directory to save results : results
```
The other parameters control the measurement accuracies, Depth of Investigation (DOI), and plotting options.

For a detailed description of each parameter, please refer to `docs/user_manual.pdf`.

### Topography and DOI

When using a model that includes topography, the DOI coefficient is automatically set to **0.2**:

Therefore see:  topographic example provided with PyMERRY v2.0.

> **Important:** PyMERRY v2.0 takes topography into account. The `user_manual.pdf` was written for an earlier version and therefore contains outdated information stating that topography is not taken into account.
## Running PyMERRY

PyMERRY can be run either directly from Python/Spyder or from a Linux terminal.

### Running from Spyder

The script `run_pymerry.py` can be executed directly from Spyder.

Before running the script, open `run_pymerry.py` and specify the parameter file in the `PARAMETER_FILE` variable:

    PARAMETER_FILE = "examples/example_with_topography/parameters.txt"

You can replace this path with the parameter file you want to use.

Then run `run_pymerry.py` from Spyder.

The parameter file specified in `PARAMETER_FILE` is used when the script is executed from Spyder without a command-line argument.

### Running from the terminal

PyMERRY can also be run directly from a terminal by providing the parameter file as an argument:

    python run_pymerry.py parameters.txt

For example, to run the example without topography:

    python run_pymerry.py examples/example_without_topography/parameters.txt

To run the example including topography:

    python run_pymerry.py examples/example_with_topography/parameters.txt

The parameter file provided as an argument is used to load the input data, define the PyMERRY parameters, and specify the output directory.

If no parameter file is provided when running PyMERRY from the terminal, the program stops and displays an error message explaining how to provide one.

### Important: multiprocessing

PyMERRY uses multiprocessing to speed up the error assessment calculations.

For this reason, PyMERRY should not be run directly from a Jupyter Notebook.

It is recommended to use Spyder or to run the code directly from a terminal.

The computation time can vary significantly depending on the size of the mesh, the number of ERT measurements, and the selected parameters. Large meshes and datasets may require a substantial amount of computation time.

## Figures and visualization

The figures automatically generated by PyMERRY and saved in the `results` directory are provided as default visualizations of the calculation results.

These figures are intended to illustrate the main outputs of the PyMERRY error assessment. Users are strongly encouraged to read the associated publication to understand the methodology, results, and interpretation:

Maxime Gautier, Stéphanie Gautier, Rodolphe Cattin; *PyMERRY: A Python solution for an improved interpretation of electrical resistivity tomography images*. Geophysics, 89(1), F23–F39, 2023. DOI: https://doi.org/10.1190/geo2023-0105.1

The visualization code is included in `run_pymerry.py`. Users are therefore encouraged to adapt the plotting section of this script to their own datasets, visualization requirements, and scientific applications.

The default figures should not necessarily be considered as the only or most appropriate way to visualize the results. Additional plots can be created from the numerical output files saved in the `results` directory.