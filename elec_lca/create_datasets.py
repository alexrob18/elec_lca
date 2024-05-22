import wurst

def mapping(df_mapping, tech, location):

    name = df_mapping[df_mapping['Technology name'] == tech].activity_name
    product = df_mapping[df_mapping['Technology name'] == tech].product_name

    tech_dict = {
        'name': name,
        'reference product': product,
        'location': location
    }

    return tech_dict


def searching_dataset(database, act_dict):

    act_filter = [
        wurst.searching.contains("name", act_dict['name']),
        wurst.searching.contains("reference product", act_dict['product']),
        wurst.searching.contains("location", act_dict['location'])
    ]

    ds = wurst.searching.get_many(database, *act_filter)

    if len(ds) == 1: # the searched dataset exists for our location
        pass

    else: # the searched dataset does not exist for our location
        act_filter = act_filter[:-1] # remove condition on location
        act_filter.append(wurst.searching.contains("location", loc) for loc in ["GLO", "RoW"]) # putting RoW or GLO instead
        ds = wurst.searching.get_many(database, *act_filter)[0] # search the GLO or RoW activity
        ds = wurst.transformations.copy_to_new_location(ds, act_dict['location']) # change the activity main location
        ds = wurst.transformations.relink_technosphere_exchanges(ds, database) # adapt the activity foreground
        database.extend(ds) # add the new LCI dataset to the database

    return ds


def new_electricity_market(database, location, df_scenario, df_mapping):

    exchanges = [] # list of exchanges of the electricity market
    tech_list = list(df_scenario.Technology.unique()) # list of technologies involved in the scenario

    for tech in tech_list: # create the list of exchanges (i.e., shares of the electricity mix)
        ds = searching_dataset(database=database, act_dict=mapping(df_mapping=df_mapping, tech=tech, location=location))
        exc = {
            'amount': float(df_scenario[df_scenario.Technology == tech].Value),
            'type': 'technosphere',
            'name': ds['name'],
            'database': database,
            'product': ds['reference product'],
            'unit': ds['unit'],
            'location': ds['location']
        }
        exchanges.append(exc)

    ds = {
        'database': database,
        #'code':,
        'name': 'market for electricity, high voltage',
        'reference product': 'electricity, high voltage',
        'location': location,
        'unit': 'kilowatt hour',
        'classifications': [],
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

    db.append(ds) # add the new electricity market to the database

    wurst.brightway.write_database.write_brightway2_database(db, f'ecoinvent_updated_electricity_mix_{location}') # write new database in brightway

    return ds