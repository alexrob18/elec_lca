"""elec_lca."""

__all__ = (
    "__version__",
    # Add functions and variables you want exposed in `elec_lca.` namespace here
    "read_user_input_template_excel_file",
    "mapping",
    "searching_dataset",
    "new_electricity_market"
)

__version__ = "0.0.1"

from .reading import read_user_input_template_excel_file
from .create_datasets import mapping, searching_dataset, new_electricity_market