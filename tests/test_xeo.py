from importlib.resources import files

import xeo


def test_public_package_metadata():
    assert xeo.__version__ == "2026.2.0"
    assert xeo.__all__ == ["catalogue", "instruments"]


def test_catalogue_is_available_from_xeo():
    assert xeo.catalogue.name == "Awesome Earth Observation Instruments"
    assert xeo.catalogue.instruments.MSI_S2A.data["id"] == "MSI_S2A"
    assert xeo.instruments.MSI_S2A.data["id"] == "MSI_S2A"


def test_catalogue_is_packaged_under_xeo():
    catalogue_path = files("xeo.data") / "catalogue.json"

    assert catalogue_path.is_file()
