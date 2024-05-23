import pandas as pd
import numpy as np
import bw_processing as bwp
import matrix_utils as mu
import bw2calc as bc
import bw2data
import json

from elec_lca.reading import read_user_input_template_excel_file
from elec_lca.create_datasets import new_electricity_market
from elec_lca.create_user_input_file import create_user_input_file
from elec_lca.lca_results import get_elec_impact, get_elec_A_mat_indice_for_Scn_x_Year_t


class Elec_LCA:
    """

    """

    user_input_location_dir = None
    user_input_location_filename = None
    df_scenario = None
    original_database = None
    modified_database = {}
    tech_dict = {}
    bio_dict = {}
    index_array_to_modify = None
    data_array_to_modify = {}
    mapping_filepath = None
    df_results = None
    scenario_mapping = None # tuple (scenario, period)
    method_list = None
    methode_family = None

    def __init__(self, original_database, methode_family):
        self.original_database = original_database
        self.methode_family = methode_family

    def prepare_method_list(self, methode_family):
        flows = []
        methods = []
        for m in list(bw2data.methods):
            if m[0] == methode_family:
                d = {"name": list(m), "exchanges": []}
                method = bw2data.Method(m)
                cfs = method.load()
                for idx, val in cfs:
                    act = bw2data.get_activity(idx)
                    d["exchanges"].append({
                        "name": act["name"],
                        "categories": list(act["categories"]),
                        "amount": val
                    })
                flows.append(d)
                methods.append(m)
        with open('../elec_lca/data/lcia_data.json', 'w') as f:
            json.dump(flows, f)
        self.method_list = [" - ".join(i) for i in methods]

    # load Data
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

    # make calculation
    def create_new_location_dataset(self, overwrite_data_set=False):

        scn_df = self.df_scenario.copy()
        location_list = scn_df["location"].unique().tolist()

        for loc in location_list:
            if loc in self.modified_database.keys() and not overwrite_data_set:
                print(f"Skipping location {loc}, since there is already a dataset with this location.\n "
                      "To overwrite the dataset, set the argument 'overwrite_data_set' to true")

            self.prepare_method_list(self.methode_family)

            modified_dataset, tech_dict, bio_dict = new_electricity_market(
                self.original_database,
                loc,
                scn_df[scn_df["location"] == loc].copy(),
                methods=self.method_list,
                mapping_filepath=self.mapping_filepath
            )

            self.modified_database[loc] = modified_dataset.copy()
            self.tech_dict[loc] = tech_dict.copy()
            self.bio_dict[loc] = bio_dict.copy()

            df_of_modified_scenario = scn_df[scn_df["location"] == loc].copy()
            df_of_modified_scenario = df_of_modified_scenario.pivot_table(
                values="value", index=["scenario", "period"], columns="technology", aggfunc='sum'
            ).set_index(["scenario", "period"])

            self.scenario_mapping = {idx: name for idx, name in enumerate(df_of_modified_scenario.index.to_list)}
            self.data_array_to_modify[loc] = df_of_modified_scenario.to_numpy()

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

        for impact_method in self.method_list:
            for loc in self.modified_database.keys():

                dp_scenarios = bwp.create_datapackage(combinatorial=True)
                dp_scenarios.add_persistent_array(
                        matrix='technosphere_matrix',
                        indices_array=self.index_array_to_modify,
                        data_array=np.array(self.data_array_to_modify[loc]),  # reduce cf consumption
                        flip_array=np.array([False]),
                        name='cf scenario'
                    )

                lca = bc.LCA(
                    demand={'market for electricity, low voltage': 1},
                    data_objs=[self.modified_database[loc][impact_method], dp_scenarios],
                    use_arrays=True,
                )
                lca.lci()
                lca.lcia()

                scenario_mapping = self.scenario_mapping

                # save first results
                resource_group = next(grp for grp in lca.technosphere_mm.groups).indexer.indexer
                (scn, per) = scenario_mapping[resource_group.index]
                res = pd.DataFrame(columns=["location", "period", "scenario"] + impact_method_list)
                res["location"] = [loc]
                res["period"] = per
                res["scenario"] = scn
                for method in impact_method_list:
                    res[method] = 0 if method != impact_method else lca.score
                results_list.append(res.copy())

                for scenario_result in lca:
                    (scn, per) = scenario_mapping[resource_group.index]
                    res = pd.DataFrame(columns=["location", "period", "scenario"] + impact_method_list)
                    res["location"] = [loc]
                    res["period"] = per
                    res["scenario"] = scn
                    for method in impact_method_list:
                        res[method] = 0 if method != impact_method else lca.score

                    results_list.append(res.copy())

        self.df_results = pd.concat(results_list, axis=0).set_index(["location", "period", "scenario"])

    # get results
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

