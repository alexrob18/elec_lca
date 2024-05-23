import bw2calc as bc
import bw2data as bd

def get_A_index(code_act, database):
    '''
    Parameters
    ----------
    code_act: (str) code of the activity
    database: wurst database

    Returns
    -------
    Index of the activity in the A matrix
    '''
    database_name = database[0]['database']
    id = bd.get_id((database_name, code_act))

    act = (database[0]['database'], database[0]['code'])
    lca = bc.LCA(demand={act: 1}) # lca for random dataset
    lca.lci()

    return lca.dicts.activity[id]


def get_coeff(code_act_1, code_act_2, database):
    '''
    Get the coefficient in the A matrix
    :param act_1: (str) code of activity 1
    :param act_2: (str) code of activity 2
    :param database: wurst database of the two activities
    :return: A matrix coefficient
    '''
    database_name = database[0]['database']
    id_1 = bd.get_id((database_name, code_act_1))
    id_2 = bd.get_id((database_name, code_act_2))

    act = (database[0]['database'], database[0]['code'])
    lca = bc.LCA(demand={act: 1})  # lca for random dataset
    lca.lci()
    A = lca.technosphere_matrix

    return A[lca.dicts.activity[id_1], lca.dicts.activity[id_2]]


def get_elec_impact(
        datapackage,
        array_to_modify,
        impact_method,
        activity='market for electricity, low voltage'):
    """
    Function that will calculate the the LCA score of oone scenario

    Parameters
    ----------
    activity: bw2_activity,  the electricty activity to be studied  
    datapackage :  datapackage to use for the base A matrix 
    array_to_modify:  array to be used by bw2calc per scenario / year while not changing base A matrix 
    impact_method : a bw2data.methods 

    Returns
    -------
    df_elec: a single lca score for the activity 
    
    """

    lca = bc.LCA(
        demand={activity: 1},
        data_objs=[datapackage, array_to_modify],
        method=impact_method,
        use_arrays=True,
    )
    lca.lci()
    lca.lcia()
    # prepare some df
    df_elec = lca.score
    return df_elec