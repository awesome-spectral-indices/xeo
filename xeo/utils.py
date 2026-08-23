import json
import os
import tempfile

from importlib.resources import files
from pathlib import Path


CATALOGUE_URL = (
    "https://github.com/awesome-spectral-indices/"
    "awesome-earth-observation-instruments/raw/refs/heads/main/"
    "catalogue/catalogue.json"
)


def _validate_catalogue_json(contents: bytes) -> dict:
    """Decode catalogue bytes and validate the required top-level structure."""

    try:
        catalogue = json.loads(contents.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("the downloaded catalogue is not valid UTF-8 JSON") from error

    required_types = {
        "name": str,
        "version": str,
        "link": str,
        "instruments": dict,
    }
    if not isinstance(catalogue, dict):
        raise ValueError("the downloaded catalogue must be a JSON object")

    for property_name, expected_type in required_types.items():
        if not isinstance(catalogue.get(property_name), expected_type):
            raise ValueError(
                f"the downloaded catalogue has an invalid {property_name!r} property"
            )

    for instrument_id, instrument in catalogue["instruments"].items():
        if (
            not isinstance(instrument_id, str)
            or not isinstance(instrument, dict)
            or instrument.get("id") != instrument_id
        ):
            raise ValueError(
                f"the downloaded catalogue has an invalid instrument {instrument_id!r}"
            )
    return catalogue


def _catalogue_path(file="catalogue.json") -> Path:
    """Return the filesystem path of a bundled catalogue file."""

    return Path(files("xeo.data") / file)


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
    data_file = _catalogue_path(file)
    with data_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def _replace_JSON(contents: bytes, file="catalogue.json") -> None:
    """Atomically replace a bundled catalogue file with validated bytes."""

    destination = _catalogue_path(file)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(contents)
            temporary.flush()
            os.fsync(temporary.fileno())

        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
