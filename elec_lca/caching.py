import pickle
from pathlib import Path

DIR_DATABASE_CACHE = Path.cwd() / "export" / "cache"

def cache_database(database):
    Path(DIR_DATABASE_CACHE).mkdir(parents=True, exist_ok=True)
    with open(DIR_DATABASE_CACHE / r"ecoinvent.pickle", "wb") as output_file:
        pickle.dump(database, output_file)


def load_db():
    with open(DIR_DATABASE_CACHE / r"ecoinvent.pickle", "rb") as input_file:
        db = pickle.load(input_file)

    for ds in db:
        if "categories" in ds:
            del ds["categories"]

    return db