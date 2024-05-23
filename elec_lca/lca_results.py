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