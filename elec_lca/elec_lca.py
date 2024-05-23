import pandas
import pandas as pd

from elec_lca.reading import read_user_input_template_excel_file
from elec_lca.create_datasets import new_electricity_market
from elec_lca.create_user_input_file import create_user_input_file
from elec_lca.lca_results import get_elec_impact


class Elec_LCA:
    """

    """

    user_input_location_dir = None
    user_input_location_filename = None
    df_scenario = None
    original_database = None
    modified_database = {}
    array_to_modify = {}
    mapping_filepath = None
    df_results = None

    def __init__(self, original_database):
        self.original_database = original_database

    def load_custom_mapping_to_ei(self, mapping_filepath):

        self.mapping_filepath = mapping_filepath

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
                    return
                except Exception as e:
                    print("The file could not be loaded because of the following error, please fix it and retry: ")
                    print(e)
                    return
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

            df_of_modified_scenario = scn_df[scn_df["location"] == loc].copy()
            df_of_modified_scenario = df_of_modified_scenario.pivot_table(
                values="value", index=["scenario", "period"], columns="technology", aggfunc='sum'
            ).set_index(["scenario", "period"])

            self.modified_database[loc] = modified_dataset.copy()
            self.array_to_modify[loc] = df_of_modified_scenario

    def view_available_location(self):
        print("This object contains modified dataset for the following location:")
        for loc in self.modified_database.keys():
            print(f"...{loc}")

    def compute_lca_score_for_all_scenario(self, impact_method_list):
        """

        Parameters
        ----------
        impact_method_list :

        Returns
        -------

        """

        results_list = []

        for loc in self.modified_database.keys():
            for (scn, per) in self.array_to_modify[loc]:
                elec_scn_arr = None
                for impact_method in impact_method_list:
                    score = get_elec_impact(
                                self.modified_database[loc],
                                elec_scn_arr,
                                impact_method,
                                activity='market for electricity, low voltage'
                            )
                    res = pd.DataFrame(columns=["location", "period", "scenario"] + impact_method_list)
                    res["location"] = [loc]
                    res["period"] = per
                    res["scenario"] = scn
                    for method in impact_method_list:
                        res[method] = 0 if method != impact_method else score
                    results_list.append(res.copy())

        self.df_results = pd.concat(results_list, axis=0).set_index(["location", "period", "scenario"])

    def get_specific_results(self, scenario, period, location):
        if self.df_results is None:
            print("results has not been generated")
            return

        if (location, period, scenario) not in self.df_results.index.tolist():
            print("No input were provided for target scenario, period, location")
            return

        temp_res = self.df_results.copy()
        temp_res = temp_res[(temp_res["scenario"] == scenario)
                            & (temp_res["period"] == period)
                            % (temp_res["location"] == location)]

        results_dict = {}
        for col in self.df_results.copy():
            results_dict[col] = self.df_results.at[(location, period, scenario), col]

        print(results_dict)
        return results_dict

    def get_all_results(self):
        if self.df_results is None:
            print("results has not been generated")
            return

        return self.df_results

