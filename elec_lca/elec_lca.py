import pandas
from elec_lca.reading import read_user_input_template_excel_file
from elec_lca.create_datasets import new_electricity_market
from elec_lca.create_user_input_file import create_user_input_file


class Elec_LCA:
    """

    """

    user_input_location_dir = None
    user_input_location_filename = None
    df_scenario = None
    original_database = None
    modified_database = {}
    mapping_filepath = None

    def __init__(self, original_database):
        self.original_database = original_database

    def load_custom_mapping_to_ei(self):

        self.mapping_filepath()

    def create_input_file(self, output_directory):
        filepath = create_user_input_file(
            output_directory,
            warn_if_dir_created=True,
            force_overwrite=False
            )
        self.user_input_location_dir = filepath.parent
        self.user_input_location_filename = filepath.name

    def load_user_input_file(self, use_default_user_input_file=True, custom_csv_filepath=None):

        if custom_csv_filepath is not None and not use_default_user_input_file:
            print("this functionality is not been programmed yet, please use the "
                  "create_input_file(output_directory: str, pathlin) to create a scenario and load it")
            return

        if use_default_user_input_file:
            if (self.user_input_location_dir / self.user_input_location_filename).is_file():
                try:
                    self.df_scenario = read_user_input_template_excel_file(
                        self.user_input_location_dir,
                        user_input_template_filename=self.user_input_location_filename,
                    )
                except Exception as e:
                    print("The file could not be loaded because of the following error, please fix it and retry: ")
                    print(e)
            print("No default user input file has been create, use:\n"
                  "create_input_file(output_directory: str, pathlin)")
            return

        print("No user input as be given, no data has been loaded")
        return

    def create_new_location_dataset(self, overwrite_data_set=False):

        scn_df = self.df_scenario.copy()
        location_list = scn_df["location"].unique().tolist()

        for loc in location_list:
            if loc in self.modified_database.keys() and not overwrite_data_set:
                print(f"Skipping location {loc}, since there is already a dataset with this location.\n "
                      "To overwrite the dataset, set the argument 'overwrite_data_set' to true")

            modified_dataset = new_electricity_market(
                self.original_database,
                loc,
                scn_df[scn_df["location"] == loc].copy(),
                mapping_filepath=self.mapping_filepath
            )

            self.modified_database[loc] = modified_dataset.copy()

    def view_available_location(self):
        print("This object contains modified dataset for the following location:")
        for loc in self.modified_database.keys():
            print(f"...{loc}")

