"""
This file contains functions to read the input data from the user.
"""
import warnings
import pandas as pd
import openpyxl
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message=".*Data Validation extension.*"
)


def read_input_excel_file(
        user_input_directory="../data",
        user_input_template_filename="user_input_template.xlsm",
):
    """Function that reads the user input excel template file filed out by the user and returns the information
    stored in a DataFrame.

    Parameters
    ----------
    user_input_directory: str or pathlib.Path, default="../data"
        Name of the directory where the Excel file that contains the input data from the user is located.
    user_input_template_filename: str, default="user_input_template.xlsm"
        Name of the input Excel file that contains the input data from the user.

    Returns
    -------
    df_total: pd.DataFrame
        DataFrame containing information on the electricity fuel mix by technology and periods for different
        scenarios and locations.
    """
    # Make sure the file exists
    user_input_filepath = validate_file_exists(
        filepath=Path(user_input_directory) / user_input_template_filename, expected_extension=".xlsm"
    )

    # Load the workbook
    workbook = openpyxl.load_workbook(filename=user_input_filepath, data_only=True)

    # Initialize the list of DataFrame
    list_df = []

    # Iterate over all the sheets that contain inputs
    for sheet_name in workbook.sheetnames:
        if sheet_name not in ["README", "Dropdown_list", "default_dataset", "Input_template"]:
            sheet = workbook[sheet_name]
            # Get scenario name and location
            scn_name = sheet['C7'].value
            location = sheet['C9'].value
            # Get the index of the last cell in the worksheet
            last_cell = str(sheet.calculate_dimension()).split(":")[1]

            # Read information and store in DataFrame
            df = range_to_df(sheet["I5:{}".format(last_cell)])

            # Format the DataFrame
            df = pd.melt(df, id_vars=["Technology list"], var_name="period")
            df.rename(columns={"Technology list": "technology"}, inplace=True)
            df["scenario"] = scn_name
            df["location"] = location

            # Add the DataFrame to the list
            list_df.append(df)

    # Concatenate all the DataFrames
    df_total = pd.concat(list_df, axis=1)
    return df_total


def range_to_df(worksheet, remove_nan=True):
    """
    Convert a worksheet range to a DataFrame.

    Parameters
    ----------
    worksheet: openpyxl.Worksheet
        Worksheet range to convert into a DataFrame.
    remove_nan: bool
        True, if rows and columsn containing all NaN values should be removed.

    Returns
    -------
    df: pd.DataFrame
        DataFrame containing the information that was in the Worksheet range.

    """
    # Read the cell values into a list of lists
    data_rows = []
    for row in worksheet:
        data_cols = []
        for cell in row:
            data_cols.append(cell.value)
        data_rows.append(data_cols)

    # Add the data into a DataFrame
    df = pd.DataFrame(data_rows[1:])
    df.columns = data_rows[0]

    # Remove rows and columns that contains all NaN, if required
    if remove_nan:
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)

    return df


def validate_file_exists(filepath, expected_extension=None):
    """Check file exists and transform string representation of filepath to pathlib Path

    Parameters
    ----------
    filepath: str or pathlib.Pathread_excel
        Path to file to be validated.
    expected_extension: str
        Extension the file should have (including the period, e.g. '.csv').

    Returns
    -------
    filepath: pathlib.Path
        Filepath as Path object, if all validation went through.
    """
    filepath = Path(filepath)

    # Check if directory exists
    if not filepath.parent.exists():
        raise FileNotFoundError("No directory at {}".format(
            filepath.parent.resolve()
        ))

    # Check if file exists
    if not filepath.exists():
        raise FileNotFoundError("No file named {} in {}".format(
            filepath.name, filepath.parent.resolve()
        ))

    # Check if expected extension
    if expected_extension:
        if not filepath.suffix == expected_extension:
            raise ValueError("Extension {} does not match expected extension {}".format(
                filepath.suffix, expected_extension
            ))

    return filepath
