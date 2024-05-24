from datapackage import Package
from pathlib import Path
import bw_processing as bwp
import numpy as np
import json
import copy

from lcia import get_lcia_methods

DIR_DATAPACKAGE_TEMP = Path.cwd() / "export" / "temp"
DIR_DATAPACKAGE = Path.cwd() / "export" / "datapackage"
DATA_DIR = Path(__file__).parent / "data"
LCIA_METHODS = DATA_DIR / "lcia_data.json"




def convert_wurst_to_arrays(database):
    """
    Converts a wurst database (list of dictionaries) into the following:
    * numpy array of technosphere indices
    * numpy array of values for each technosphere exchange
    * numpy array of biosphere indices
    * numpy array of values for each biosphere exchange

    And save them under the temp directory.

    Parameters
    ----------
    database
        A wurst database, as a list of dictionaries.

    Returns
    -------
    None. Saves the arrays under the temp directory.

    """
    technosphere_indices, technosphere_values = [], []
    biosphere_indices, biosphere_values = [], []

    indices = {
        (a["name"], a["reference product"], a["location"]): i
        for i, a in enumerate(database)
    }

    indices_bio = {}

    signs = []

    for i, ds in enumerate(database):
        for e in ds["exchanges"]:
            if e["type"] in ["technosphere", "production"]:
                technosphere_indices.append(
                    [i, indices[(e["name"], e["product"], e["location"])]]
                )
                technosphere_values.append(e["amount"])
                signs.append(False if e["type"] == "technosphere" else True)

            elif e["type"] == "biosphere":
                key = (
                    e["name"],
                    e["categories"][0],
                    "unspecified" if len(e["categories"]) == 1 else e["categories"][1],
                )
                if key not in indices_bio:
                    indices_bio[key] = len(indices_bio)

                biosphere_indices.append([i, indices_bio[key]])
                biosphere_values.append(e["amount"])

    return (
        technosphere_indices,
        technosphere_values,
        signs,
        indices,
        biosphere_indices,
        biosphere_values,
        indices_bio,
    )


def create_datapackage(database: list, methods: list) -> [Package, dict, dict]:
    """
    Create a data package from the temp directory and save it to the datapackage directory.
    Parameters
    ----------
    name: str
        Name of the data package. Default is "test".

    Returns
    -------
    None. Saves the data package to the datapackage directory.

    """

    (
        technosphere_indices,
        technosphere_values,
        signs,
        tech_dict,
        biosphere_indices,
        biosphere_values,
        bio_dict,
    ) = convert_wurst_to_arrays(database)

    technosphere_indices = np.array(technosphere_indices)
    technosphere_indices = np.array(
        list(
            zip(
                technosphere_indices[:, 1].astype(int),
                technosphere_indices[:, 0].astype(int),
            )
        ),
        dtype=bwp.INDICES_DTYPE,
    )

    technosphere_values = np.array(technosphere_values)

    biosphere_indices = np.array(biosphere_indices)
    biosphere_indices = np.array(
        list(
            zip(
                biosphere_indices[:, 1].astype(int), biosphere_indices[:, 0].astype(int)
            )
        ),
        dtype=bwp.INDICES_DTYPE,
    )

    biosphere_values = np.array(biosphere_values)

    signs = np.array(signs)

    dict_lcia = get_lcia_methods(methods)

    datapackages = []

    for method in methods:
        dp = bwp.create_datapackage()
        dp.add_persistent_vector(
            matrix="technosphere_matrix",
            indices_array=technosphere_indices,
            data_array=technosphere_values,
            flip_array=signs,
        )

        dp.add_persistent_vector(
            matrix="biosphere_matrix",
            indices_array=biosphere_indices,
            data_array=biosphere_values,
        )

        c_indices = [
            [(bio_dict[flow_name], bio_dict[flow_name])]
            for flow_name in dict_lcia[method]
            if flow_name in bio_dict
        ]
        c_indices = np.squeeze(np.array(c_indices, dtype=bwp.INDICES_DTYPE))

        c_data = np.array([dict_lcia[method][flow_name]
                           for flow_name in dict_lcia[method]
                           if flow_name in bio_dict])

        dp.add_persistent_vector(
            matrix='characterization_matrix',
            indices_array=c_indices,
            data_array=c_data,
        )

        datapackages.append(dp)

    return datapackages, tech_dict, bio_dict
