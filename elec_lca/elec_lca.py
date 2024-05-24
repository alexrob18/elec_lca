import pandas as pd
import numpy as np
import bw_processing as bwp
import matrix_utils as mu
import bw2calc as bc
import bw2data
import json

from reading import read_user_input_template_excel_file
from create_datasets import new_electricity_market
from create_user_input_file import create_user_input_file
from lcia import get_lcia_method_names


class Elec_LCA:
    """
    Main class to prepare final lca results once the database is prepared (by create_datasets.py) 
    Computes LCA by calling lca_results.py, where a base A_matrix and a changing array_to_modify per scenario per year is used in matrix calculation. This enables a faster computation of LCA per scenario/year. 
    
    Parameters
    ----------
    user_input_location_dir: absolute filepath in users' local drives that stores user-input excel file 
    user_input_location_filename: the file name for user-input excel 
    df_scenario: user supplied scenarios
    original_database: the original background database supplied by user
    modified_database: dict of modified database for the new electricity market
    array_to_modify: dict of array to be used by bw2calc per scenario / year 
    mapping_filepath: file path for technology mapping: map user-defined technology to background dataset  
    df_results: the final lca results returned per scenario / year 
    
    """

    user_input_location_dir = None
    user_input_location_filename = None
    mapping_filepath = None

    methode_family = None # type of methods
    method_list = None # exact list of methods

    original_database = None
    modified_datapack = {}
    tech_map = {}
    tech_dict = {}
    bio_dict = {}
    df_scenario = None

    index_array_to_modify = {}
    data_array_to_modify = {}

    results_fiure = None

    list_of_df_scenario = {}
    scenario_mapping = None # tuple (scenario, period)
    df_results = None
    status = None

    def __init__(self, original_database, methode_family):
        self.original_database = original_database
        self.methode_family = methode_family

    def prepare_method_list(self, methode_family):
        self.method_list = get_lcia_method_names()
    
    def load_custom_mapping_to_ei(self, mapping_filepath):
        """     locate the technology mapping file , doesn't return anything  """
        self.mapping_filepath = mapping_filepath

    def create_input_file(self, output_directory):
        """
        create an input_file,
        prepare: user_input_location_dir and user_input_location_filename

        Parameters
        ----------
        output_directory: the user's output directory in the local drive
        """
        
        filepath = create_user_input_file(
            output_directory,
            warn_if_dir_created=True,
            force_overwrite=False
            )
        self.user_input_location_dir = filepath.parent
        self.user_input_location_filename = filepath.name

    def load_user_input_file(self, use_default_user_input_file=True, custom_csv_filepath=None):
        """ 
        load users input excel to prepare the input data
        
        Parameters
        ----------
        use_default_user_input_file: default is true, use user's input file
        custom_csv_filepath: 

        Prepares:
        ----------
        self.df_scenario: the scenarios pulled from user input excel 
        
        """

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

    # make calculation
    def create_new_location_dataset(self, overwrite_data_set=False):
        """ 
        to create a new dataset according to user's input location, through create_datasets.py module / new_electricity_market
        
        Parameters
        ----------
        overwrite_data_set: default False, if there is already the dataset for user-specified location from original database

        Prepares:
        ----------
        self.modified_database: the dict of modified database, key is the location, value is the modified database
        self.array_to_modify: the dict of array to be used by bw2calc per scenario / year  
        """

        scn_df = self.df_scenario.copy()
        location_list = scn_df["location"].unique().tolist()

        for loc in location_list:
            if loc in self.modified_datapack.keys() and not overwrite_data_set:
                print(f"Skipping location {loc}, since there is already a dataset with this location.\n "
                      "To overwrite the dataset, set the argument 'overwrite_data_set' to true")

            self.prepare_method_list(self.methode_family)

            modified_dataset, tech_dict, bio_dict, tech_map = new_electricity_market(
                self.original_database,
                loc,
                scn_df[scn_df["location"] == loc].copy(),
                methods=self.method_list,
                mapping_filepath=self.mapping_filepath
            )
            self.modified_datapack[loc] = modified_dataset.copy()
            self.tech_dict[loc] = tech_dict.copy()
            self.tech_map[loc] = tech_map.copy()
            self.bio_dict[loc] = bio_dict.copy()

            df_of_modified_scenario = scn_df[scn_df["location"] == loc].copy()
            df_of_modified_scenario = df_of_modified_scenario.pivot_table(
                values="value", index=["scenario", "period"], columns="technology", aggfunc='sum'
            )

            self.scenario_mapping = {idx: name for idx, name in enumerate(df_of_modified_scenario.index.to_list())}
            self.list_of_df_scenario[loc] = df_of_modified_scenario

            self.index_array_to_modify[loc] = np.array(
                [(tech_dict[tech_map[tech]["name"], tech_map[tech]["reference product"], tech_map[tech]["location"]],
                  tech_dict[("market for electricity, high voltage", "electricity, high voltage", loc)])
                 for tech in tech_map.keys()],
                dtype=bwp.INDICES_DTYPE)

            self.data_array_to_modify[loc] = np.transpose(df_of_modified_scenario.to_numpy())

    def view_available_location(self):
        """ to print out the modified locations """
        print("This object contains modified dataset for the following location:")
        for loc in self.modified_datapack.keys():
            print(f"...{loc}")

    def compute_lca_score_for_all_scenario(self):
        """
        compute the final lca score for all scenarios and years, combined into one final dataframe

        Parameters
        ----------
        impact_method_list: a list of bw2data.methods 
        example: ('TRACI v2.1 no LT', 'climate change no LT', 'global warming potential (GWP100) no LT')

        Prepares
        -------
        df_results: the lca results run though matrix calcuation from lca_results.py , get_elec_impact
        """

        results_list = []
        permutation_to_do = (len(self.method_list) * len(self.modified_datapack.keys()) * len(self.scenario_mapping))
        i = 0
        for idx, impact_method in enumerate(self.method_list):
            for loc in self.modified_datapack.keys():

                current_datapack = self.modified_datapack[loc][idx]

                dp_scenarios = bwp.create_datapackage(sequential=True)
                dp_scenarios.add_persistent_array(
                        matrix='technosphere_matrix',
                        indices_array=self.index_array_to_modify[loc],
                        data_array=self.data_array_to_modify[loc],
                        # flip_array=np.array([False for _ in range(len(self.index_array_to_modify[loc]))]),
                        name='scenario'
                    )

                lca = bc.LCA(
                    demand={self.tech_dict[loc][("market for electricity, low voltage", "electricity, low voltage",
                                                 loc)]: 1},
                    data_objs=[current_datapack, dp_scenarios],
                    use_arrays=True,
                )
                lca.lci()
                lca.lcia()

                lca.keep_first_iteration()
                scenario_mapping = self.scenario_mapping

                for _, (scn, per) in scenario_mapping.items():
                    i += 1
                    self.status = f"lca {i} out of {permutation_to_do}"
                    print(self.status)
                    next(lca)
                    res = pd.DataFrame(columns=["location", "period", "scenario", "impact_method", "value"])
                    res["location"] = [loc]
                    res["scenario"] = scn
                    res["period"] = per
                    res["impact_method"] = impact_method
                    res["value"] = lca.score

                    results_list.append(res.copy())

        self.df_results = pd.concat(results_list, axis=0).set_index(["location", "period", "scenario", "impact_method"])

    # get results
    # def get_specific_results(self, scenario, period, location, impact_method):
    #     """
    #     get lca result for specific scenario and year(s) from the final df_results prepared in compute_lca_score_for_all_scenario()
    #
    #     Parameters
    #     ----------
    #     scenario: specific scenario to get from the final df_results
    #     period:   specific period to get from the final df_results
    #     location: specific location to get from the final df_results
    #     impact_method : specific impact method to get from the final df_results
    #
    #     Returns
    #     -------
    #     results_dict: dict storing lca dataframe for selected scenario, period, location
    #     """
    #
    #     if self.df_results is None:
    #         print("results has not been generated")
    #         return
    #
    #     if (location, period, scenario,  impact_method) not in self.df_results.index.tolist():
    #         print("No input were provided for target scenario, period, location")
    #         return
    #
    #     temp_res = self.df_results.copy()
    #
    #     return temp_res.at[(location, scenario, period, impact_method), "value"]

    def get_all_results(self):
        """ get all the combined scenarios, years, locations results dataframe """
        if self.df_results is None:
            print("results has not been generated")
            return

        return self.df_results

    # format
    def create_plot_for_1_loc(self, loc, scenario):
        df = self.get_all_results().copy().reset_index()
        df = df[df["location"] == loc]
        df = df[df["scenario"] == scenario]
        df_min = df[df["period"] == df["period"].min()].rename(columns={"value": "min_val"}).drop(columns="period")

        df = pd.merge(df, df_min, on=['location', "scenario", "impact_method"], how="left")
        df["value"] = df["value"] / df["min_val"]
        df = df.drop(columns="min_val")

        df = df.pivot(index="period", columns=("scenario", "location", "impact_method"), values="value")
        fig = df.plot(figsize=(12, 8))
        fig.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        self.results_fiure = fig

