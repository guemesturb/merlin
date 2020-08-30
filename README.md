# Palabos UC3M

Palabos UC3M is a Python library for processing the Palabos simulations generated at the Experimental Aerodynamics and Propulsion Laboratory.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies for Palabos UC3M.

```bash
pip install -r requirements.txt
```

## Usage

```python
from palabos_uc3m import Palabos_UC3M

directory_input = /path/to/your/palabos/files
directory_output = /path/to/stored/your/processed/files

postprocesser = Palabos_UC3M(
    directory_input,
    directory_output
)

# Convert Palabos files into Matlab files

postprocesser.generate_readable_files()

# Compute ststistics

postprocesser.compute_statistics()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
