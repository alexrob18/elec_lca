"""elec_lca."""

__all__ = (
    "__version__",
    # Add functions and variables you want exposed in `elec_lca.` namespace here
    "read_input_excel_file",
)

__version__ = "0.0.1"

from .reading import read_input_excel_file