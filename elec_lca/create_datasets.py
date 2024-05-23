import pandas as pd
import wurst
import bw2data
import uuid
from pathlib import Path
import pkg_resources


def mapping(tech, location, mapping_filepath=None):
    '''
    Performs mapping between energy technologies names and ecoinvent LCI datasets
    :param tech: (str) name of the energy technology
    :param location: (str) ecoinvent location code
    :param mapping_filepath: (str) path to mapping between energy technologies names and ecoinvent LCI datasets
    :return: Python dictionary of the technology LCI dataset containing the name, product and location as strings.
    '''

    if mapping_filepath is None:
        mapping_filepath = Path(pkg_resources.resource_stream(__name__, "__init__.py").name).parent.parent /\
                     "data/mappings/mapping_technologies_ecoinvent.csv"
    df_mapping = pd.read_csv(mapping_filepath)

    name = df_mapping[df_mapping['Technology name'] == tech].activity_name.iloc[0]
    product = df_mapping[df_mapping['Technology name'] == tech].product_name.iloc[0]

    tech_dict = {
        'name': name,
        'reference product': product,
        'location': location
    }

    return tech_dict


def searching_dataset(database, act_dict):
    '''
    Search and returns an activity within a wurst database.
    :param database: wurst database
    :param act_dict: dictionary of the activity, containing at least the name, product and location as strings.
    :return: wurst dataset
    '''
    act_filter = [
        wurst.searching.equals("name", act_dict['name']),
        wurst.searching.equals("reference product", act_dict['reference product']),
        wurst.searching.equals("location", act_dict['location'])
    ]

    ds = [a for a in wurst.searching.get_many(database, *act_filter)]

    if len(ds) == 1: # the searched dataset exists for our location
        ds = ds[0]

    else: # the searched dataset does not exist for our location
        act_filter = act_filter[:-1] # remove condition on location
        act_filter.append(wurst.either(*[wurst.searching.equals("location", loc) for loc in ["GLO", "RoW"]])) # putting RoW or GLO instead
        ds = [a for a in wurst.searching.get_many(database, *act_filter)][0] # search the GLO or RoW activity
        ds = wurst.transformations.copy_to_new_location(ds, act_dict['location']) # change the activity main location
        ds = wurst.transformations.relink_technosphere_exchanges(ds, database) # adapt the activity foreground
        database.append(ds) # add the new LCI dataset to the database

    return ds


def new_electricity_market(database, location, df_scenario, mapping_filepath=None):
    '''
    Creates a new database into which the electricity mix (high voltage) is replaced by the one specified by the user.
    :param database: wurst database
    :param location: (str) ecoinvent location code
    :param df_scenario: (pandas Dataframe) dataframe of an energy scenario, containing the shares (value column) for each energy technology (technology column)
    :param mapping_filepath: (str) path to mapping between energy technologies names and ecoinvent LCI datasets
    :return: (wurst dataset) the newly created electricity mix dataset
    '''
    name_database = database[0]['database']

    exchanges = [{
        'amount': 1.0,
        'type': 'production',
        'name': 'market for electricity, high voltage',
        'database': name_database,
        'product': 'electricity, high voltage',
        'unit': 'kilowatt hour',
        'location': location
    }] # list of exchanges of the electricity market

    tech_list = list(df_scenario.technology.unique()) # list of technologies involved in the scenario

    for tech in tech_list: # create the list of exchanges (i.e., shares of the electricity mix)
        ds = searching_dataset(database=database, act_dict=mapping(tech=tech, location=location,
                                                                   mapping_filepath=mapping_filepath))
        exc = {
            'amount': float(df_scenario[df_scenario.technology == tech].value.iloc[0]),
            'type': 'technosphere',
            'name': ds['name'],
            'database': name_database,
            'product': ds['reference product'],
            'unit': ds['unit'],
            'location': ds['location']
        }
        exchanges.append(exc)

    ds_mix = {
        'database': name_database,
        'code': uuid.uuid4().hex,
        'name': 'market for electricity, high voltage',
        'reference product': 'electricity, high voltage',
        'location': location,
        'unit': 'kilowatt hour',
        'classifications': [('ISIC rev.4 ecoinvent', '3510:Electric power generation, transmission and distribution'),
                            ('EcoSpold01Categories', 'hard coal/power plants'),
                            ('CPC', '17100: Electrical energy')],
        'categories': None,
        'comment': 'user-defined market electricity, high voltage',
        'parameters': {},
        'exchanges': exchanges
    }

    # Take the current database, and removes the market for electricity high voltage for the given location
    db = [a for a in database if (a["name"], a["reference product"], a["location"]) not in [
        ("market for electricity, high voltage", "electricity, high voltage", location)
    ]
          ]

    db.append(ds_mix) # add the new electricity market to the database

    if f'ecoinvent_updated_electricity_mix_{location}' in bw2data.databases:
        del bw2data.databases[f'ecoinvent_updated_electricity_mix_{location}']
    wurst.write_brightway2_database(db, f'ecoinvent_updated_electricity_mix_{location}') # write new database in brightway

    return ds_mix