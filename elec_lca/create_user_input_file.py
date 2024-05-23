from pathlib import Path
import shutil
import pkg_resources


def create_user_input_file(output_directory, warn_if_dir_created=True,  force_overwrite=False):
    """
    This function creates an macro enabled Excel that can be used by the user to provide electric grid mix that will be
    analysed by this package.

    Parameters
    ----------
    output_directory : Path
        Output directory where the user input file will be created
    warn_if_dir_created : bool
        If true, the code will print a warning when creating a new folder
    force_overwrite :
        This parameter allow the user to overwrite the user input file

    Returns: pathlib.Path
        returns the filepath of the user input that was just created.

    -------

    """
    if not Path(output_directory).is_dir():
        if warn_if_dir_created:
            print(f"A directory has been created to save the user input file:\n\t...{output_directory}")
        Path(output_directory).mkdir(parents=True, exist_ok=True)

    if (Path(output_directory) / "Elec_lca_user_input.xlsm").is_file() and not force_overwrite:
        print("This command was canceled since the file already exist, if you want to overwrite it you can use the "
              "function with the following argument:\n"
              "\t\tforce_overwrite=True")
        return Path(output_directory) / "Elec_lca_user_input.xlsm"

    current_file = Path(pkg_resources.resource_stream(__name__, "__init__.py").name)
    shutil.copy(current_file.parent.parent / "data/user_input_template.xlsm",
                Path(output_directory) / "Elec_lca_user_input.xlsm")
    print(f'File created at {Path(output_directory) / "Elec_lca_user_input.xlsm"}')
    print("***Make sure to enable macro when the file opens.***")

    return Path(output_directory) / "Elec_lca_user_input.xlsm"


if __name__ == "__main__":
    create_user_input_file(output_directory=Path(r"C:\modelling\spring_school\elec_lca\elec_lca\dev"))