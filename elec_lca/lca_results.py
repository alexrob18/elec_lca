import bw2calc as bc
import bw2data as bd

def technosphere_matrix(database):
    '''
    Generates the A matrix of a given database
    :param database: wurst database
    :return: technosphere matrix object
    '''
    act = (database[0]['database'], database[0]['code'])
    lca = bc.LCA(demand={act: 1}) # lca for random dataset
    lca.lci()

    return lca.technosphere_matrix


def get_coeff(code_act_1, code_act_2, database):
    '''
    Get the coefficient
    :param act_1: (str) code of activity 1
    :param act_2: (str) code of activity 2
    :param database: wurst database of the two activities
    :return:
    '''
    database_name = database[0]['database']
    id_1 = bd.get_id((database_name, code_act_1))
    id_2 = bd.get_id((database_name, code_act_2))
    A = technosphere_matrix(database)

    return A[id_1, id_2]