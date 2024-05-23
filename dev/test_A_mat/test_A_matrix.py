import bw_processing as bwp
import matrix_utils as mu
import bw2calc as bc
import numpy as np
import pandas as pd

class get_A_matrix_elec_scn_array:
    """ once data transformation is done:
    1.A get a base A matrix: dp_A (won't change per user_scn, user_yr) 
    a.B get_indice_from_A: indice for the elec_act from the base A matrix
    
    2.A get_elec_array_indice: get the indice for diff. tech (depending on input:tech_list) that needs to be replaced  each user_scn, user_yr
    2.B. get_elec_mix_data: get the electricity mix data for each array (get_elec_array_indice) 
    3. elec_scn_arr: once 1 and 2 are prepared, get the final array, changing per user_scn, user_yr
    4. final lca calculation, get_elec_impact(), return lca_score per user_scn,user_yr
    """
    def __init__(
        self,
        act = None, #elec_act to calc, assert it's a bw2_act 
        user_scn = None, 
        user_yr = None, 
        tech_list = None,
        impact_method = None, 
    ):
        '''Initialise'''
        self.act = act 
        self.user_scn = user_scn
        self.user_yr = user_yr 
        self.tech_list = tech_list
        self.impact_method = impact_method
        self.dp_A = self.self.get_elec_A_mat_indice_for_Scn_x_Year_t()[0]
        self.get_indice_from_A = self.get_elec_A_mat_indice_for_Scn_x_Year_t()[1]
        self.get_elec_array_indice = self.get_elec_array_indice_for_Scn_x_Year_t()
        self.get_elec_mix_data = self.get_elec_array_value_for_Scn_x_Year_t()
        self.elec_scn_arr = self.get_final_elec_A_array_for_Scn_x_Year_t()

        
    def get_elec_A_mat_indice_for_Scn_x_Year_t(self):
        """ 
        to get the elec_act to get the A matrix per user_scn, user_yr
        output:
            get_indice_from_A: indice for the elec_act from the A matrix
        """ 
        elec_act = self.elec_act
        lca = bc.LCA(demand={elec_act: 1})
        lca.lci()
        dp_A = lca.technosphere_matrix
        # for BW25: lca.dicts.activity[bd.get_id((database_name, code_act))]
        get_indice_from_A = lca.dicts.activity[elec_act]  # for BW2
        return get_indice_from_A

    
    def convert_techx_to_bw2act (self, act_tech): 
        # need some mapping
        return techx_bw2act
    
    def get_coeff_for_tech_elec(self, act_tech, act_elec):
        '''
        Get the coefficient in the A matrix, for each tech -> elec 
        :param act_tech: need to read from self.tech_list and convert tech_x to bw2_act
        :param act_elec: self.act 
        :return: aa:  A matrix coefficient for act_tech & act_elec
        '''
        #act_tech = self.tech_list[0]
        elec_act = self.act
        lca = bc.LCA(demand = {elec_act:1})
        lca.lci()
        id1 = lca.activity_dict[act_tech] 
        id2 = lca.activity_dict[elec_act] 
        aa = lca.technosphere_matrix[
               lca.dicts.activity[id1], lca.dicts.activity[id2],
         ]
        return aa

    def get_elec_array_indice_for_Scn_x_Year_t(self ): 
        """ 
        input: elec_act: the bw2 activity per user_scn, user_yr
        output:
            get_elec_array_indice: scores tech indice for elec_mix for user_scn/user_yr: e.g., 
         """ 
        get_elec_array = [] 
        for tech_x in self.tech_list: 
            # need convert tech_x to bw2_act
            tech_x_bwact = self.convert_techx_to_bw2act(tech_x)
            aa = self.get_coeff_for_tech_elec(tech_x_bwact, self.act)
            get_elec_array.append(aa)
        get_elec_array_indice = np.array(get_elec_array, dtype=bwp.INDICES_DTYPE) 
        return (get_elec_array_indice)
    

    def get_elec_array_value_for_Scn_x_Year_t(self ): 
        """ 
        output: 
           get_elec_mix_data: array for elec_mix value 
           [[stores_coal_array],[stores_wind_array],[stores_gas_array]...]
         """ 
        get_elec_mix_data = []  
        return (get_elec_mix_data)
        
    
    def get_final_elec_A_array_for_Scn_x_Year_t(self): 
        """ 
        """ 
        get_elec_array_indice = self.get_elec_array_indice
        get_elec_mix_data = self.get_elec_mix_data

        """ to fit in get_elec_array_indice """
        elec_scn_arr = bwp.create_datapackage() 
        elec_scn_arr.add_persistent_array(
            matrix='technosphere_matrix',
            indices_array=np.array([
                    get_elec_array_indice, # elec_mix indice for scn / Year
                ], 
                dtype=bwp.INDICES_DTYPE
            ),
            # the array shape should be (N_of_elec_tech, )
            data_array=get_elec_mix_data.reshape((1, -1)), 
            flip_array=np.array([True]),
            name='scenario_' + str(user_scn) + 'year' + str(user_yr)
        )
        return elec_scn_arr
    

    def get_elec_impact(self): 
        """ 
        """  
        lca = bc.LCA(
            demand={self.act: 1},
            data_objs=[self.dp_A, self.elec_scn_arr],
            method = self.impact_method, 
            use_arrays=True,
        )
        lca.lci()
        lca.lcia()
        # prepare some df
        df_elec = lca.score
        return df_elec