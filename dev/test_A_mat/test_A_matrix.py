import bw_processing as bwp
import matrix_utils as mu
import bw2calc as bc
import numpy as np
import pandas as pd


class xxx : 

    # input needed: 


    # initilize : 
    
    self.dp_A = dp_A
    self.user_scn
    self.user_yr
    #self.
    self.get_elec_array_indice = self.get_elec_dataarray_for_Scn_x_Year_t()[0]
    self.get_elec_mix_data = self.get_elec_dataarray_for_Scn_x_Year_t()[1]
    self.elec_scn_arr = self.get_elec_A_vector_for_Scn_x_Year_t()
        

    
    def get_elec_dataarray_for_Scn_x_Year_t(): 
        """ 
        input: elec_act: the bw2 activity per user_scn, user_yr
        output:
            get_elec_mix_data: 
            the np.array for the elec_mix for user_scn/user_yr: e.g., 
            [[stores_coal_array],[stores_wind_array],[stores_gas_array]...]
         """ 

        #get_elec_array_indice = 
        #get_elec_mix_data = 
        
        return (get_elec_array_indice, get_elec_mix_data)
    
        
    def get_elec_mat_indice_for_Scn_x_Year_t(self):
        """ 
        to get the elec_act to get the A matrix per user_scn, user_yr
        output:
            get_indice_from_A: indice for the elec_act from the A matrix,
        """ 
        elec_act = f(self.user_scn, self.user_yr)
        
        lca = bc.LCA(demand = {elec_act:1})
        lca.lci()
        get_indice_from_A = lca.activity_dict[elec_act]
        return (get_indice_from_A)
    
    
    def get_elec_A_vector_for_Scn_x_Year_t(get_indice_from_A, get_elec_mix_data, user_scn, user_yr): 
        """ 
        get_indice_from_A: the col_indice from changed_A
        user_scn : the user-defined scenario for the new elec_mix
        user_yr: the year for the new elec_mix under user_scn 
        """ 
        elec_scn_arr = bwp.create_datapackage() 
        elec_scn_arr.add_persistent_array(
            matrix='technosphere_matrix',
            indices_array=np.array([
                    get_indice_from_A, # elec_mix indice for scn / Year
                ], 
                dtype=bwp.INDICES_DTYPE
            ),
            # the array shape should be (N_of_elec_tech, )
            data_array=get_elec_mix_data.reshape((1, -1)), 
            flip_array=np.array([True]),
            name='scenario_' + str(user_scn) + 'year' + str(user_yr)
        )
        return elec_scn_arr
    
    
    def get_elec_impact( self ): 
        """ 
        dp_A: the A_matrix (with old or new elec%) 
        elec_indice: the elec to be calculated 
        impact_method: the impact methods to run
        """ 
    
        elec_act 
        dp_A = self.dp_A
        elec_scn_arr = self.
        impact_method = self.impact_method 
        
        lca = bc.LCA(
            demand={elec_act: 1},
            data_objs=[dp_A, elec_scn_arr],
            method = impact_method, 
            use_arrays=True,
        )
        lca.lci()
        lca.lcia()
    
        # prepare some df
        df_elec = 
        return df_elec