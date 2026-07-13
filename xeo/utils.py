import json

from importlib.resources import files


def _load_JSON(file="catalogue.json"):
    """Loads the specified JSON file from the data folder.

    Parameters
    ----------
    file : str
        File name.

    Returns
    -------
    object
        JSON file.
    """
    data_file = files("xeo.data") / file
    with data_file.open("r", encoding="utf-8") as f:
        return json.load(f)
