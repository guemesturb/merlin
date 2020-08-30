# MERLIN (uc3M EnviRonment for Lbm sImulatioNs)

MERLIN is a Python library developed at the Experimental Aerodynamics and Propulsion Laboratory of the Universidad Carlos III de MAdrid and used for processing simulations generated with Lattice Boltzmann Method.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies for Palabos UC3M.

```bash
pip install -r requirements.txt
```

## Usage

```python
from merlin import MERLIN

directory_input = "/path/to/your/palabos/files"
directory_output = "/path/to/store/your/processed/files"
flow_type = "jet"

postprocesser = MERLIN(
    flow_type
)

# Convert Palabos files into Matlab files

postprocesser.generate_readable_files(  
    delete_files=False, 
    directory_input=directory_input, 
    directory_output=directory_output, 
    geometry='3D', 
    method='nearest',
    resolution_x=0.1, 
    resolution_y=0.1, 
    resolution_z=0.1,
    save_mesh=True, 
    save_data=True, 
    save_data_type='matlab'
)

# Compute ststistics

postprocesser.compute_statistics()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
