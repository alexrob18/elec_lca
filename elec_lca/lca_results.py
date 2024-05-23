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


def get_elec_A_mat_indice_for_Scn_x_Year_t(bc, elec_act):
    """
    to get the elec_act to get the A matrix per user_scn, user_yr

    Parameters
    ----------
    elec_act :

    Returns
    -------

    """
    """ 
    to get the elec_act to get the A matrix per user_scn, user_yr
    output:
        get_indice_from_A: indice for the elec_act from the A matrix
    """
    lca = bc.LCA(demand={elec_act: 1})
    lca.lci()
    dp_A = lca.technosphere_matrix
    # for BW25: lca.dicts.activity[bd.get_id((database_name, code_act))]
    get_indice_from_A = lca.dicts.activity[elec_act]  # for BW2
    return dp_A, get_indice_from_A


def get_elec_impact(
        datapackage,
        elec_scn_arr,
        impact_method,
        activity='market for electricity, low voltage'):
    """
    Function that will calculate the the LCA score of oone scenario

    Parameters
    ----------
    activity :
    datapackage :
    elec_scn_arr :
    impact_method :

    Returns
    -------

    """


    lca = bc.LCA(
        demand={activity: 1},
        data_objs=[datapackage, elec_scn_arr],
        method=impact_method,
        use_arrays=True,
    )
    lca.lci()
    lca.lcia()
    # prepare some df
    df_elec = lca.score
    return df_elec