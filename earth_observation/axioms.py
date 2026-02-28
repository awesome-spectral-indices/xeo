from box import Box
from rich.table import Table
from rich.console import Console, RenderResult

from .utils import _load_JSON


class Catalogue(object):
    """Catalogue object.

    This object allows interaction with the
    Awesome Earth Observation Instruments (AEOI) catalogue.

    See Also
    --------
    Instruments : Instruments object.
    Instrument : Instrument object.

    Examples
    --------
    >>> import earth_observation as eo
    >>> eo.catalogue
    Result here
    """

    def __init__(self, catalogue: dict):

        self.data = catalogue
        """Dictionary containing the catalogue."""

        self.name = catalogue["name"]
        """Name of the catalogue."""

        self.version = catalogue["version"]
        """Version of the catalogue."""

        self.link = catalogue["link"]
        """URL of the catalogue."""

        self.href = catalogue["link"]
        """URL of the catalogue."""

        self.instruments = Instruments(catalogue["instruments"], frozen_box=True)
        """URL of the catalogue."""

    def __repr__(self):
        """Machine readable output of the Catalogue object."""

        return f"{self.name} (v{self.version})"

    def __str__(self):
        """Human readable output of the Catalogue object."""

        return f"{self.name} (v{self.version})"


class Instruments(Box):
    """Instruments object.

    This object allows interaction with the complete list of Instruments in the
    Awesome Earth Observation Instruments (AEOI) catalogue.

    See Also
    --------
    Instrument : Instrument object.
    Catalogue : Catalogue object.

    Examples
    --------
    >>> import earth_observation as eo
    >>> eo.catalogue.instruments
    Result here
    """

    def __rich_console__(self, console: Console, options) -> RenderResult:

        table = Table(title="Awesome Earth Observation Instruments")

        table.add_column("Id", style="cyan", no_wrap=True)
        table.add_column("Acronym")
        table.add_column("Name")
        table.add_column("Platform")
        table.add_column("Platform Type")
        table.add_column("Type")
        table.add_column("Status")

        status_colors = {
            "operational": "green",
            "retired": "red",
            "planned": "blue",
            "experimental": "yellow",
        }

        type_colors = {
            "hyperspectral": "chartreuse2",
            "multispectral": "orange1",
            "radar": "white",
            "lidar": "deep_sky_blue4",
            "rgb": "dark_green",
            "other": "orchid1",
        }

        platform_colors = {
            "satellite": "deep_sky_blue3",
            "airborne": "deep_sky_blue3",
            "uav": "deep_sky_blue2",
            "terrestrial": "deep_sky_blue1",
        }

        for key, value in self.items():
            data = value.data

            status_color = status_colors.get(data["status"], "white")
            styled_status = f"[{status_color}]{data['status']}[/{status_color}]"

            type_color = type_colors.get(data['type'], "white")
            styled_type = f"[{type_color}]{data['type']}[/{type_color}]"

            platform_color = platform_colors.get(data['platform_type'], "white")
            styled_platform = f"[{platform_color}]{data['platform_type']}[/{platform_color}]"

            table.add_row(
                data["id"],
                data["acronym"],
                data["name"],
                ", ".join(data["platform"]),
                styled_platform,
                styled_type,        
                styled_status,
            )

        yield table


class Instrument(object):
    """Instrument object.

    This object allows interaction with specific Instruments in the
    Awesome Earth Observation Instruments (AEOI) catalogue.
    Attributes of the Instrument can be accessed.

    See Also
    --------
    Catalogue : Catalogue object.

    Examples
    --------
    >>> import earth_observation as eo
    >>> eo.catalogue.instruments.MSI_S2A
    Result
    >>> eo.catalogue.instruments.MSI_S2A.operator
    Result
    """

    def __init__(self, instrument: dict):

        self.data = instrument
        """Dictionary containing the attributes of the Instrument."""

    def __repr__(self):
        """Machine readable output of the Instrument."""

        return repr(self.data)

    def __str__(self):
        """Human readable output of the Instrument."""

        return repr(self.data)


def _create_catalogue():
    """Creates the catalogue object locally available."""

    catalogue = _load_JSON()
    # instruments_class = {}
    for key, value in catalogue["instruments"].items():
        catalogue["instruments"][key] = Instrument(value)

    return Catalogue(catalogue)

catalogue = _create_catalogue()

def _create_instruments():
    """Creates the instruments object locally available."""

    catalogue = _load_JSON()
    # instruments_class = {}
    for key, value in catalogue["instruments"].items():
        catalogue["instruments"][key] = Instrument(value)

    return Instruments(catalogue["instruments"], frozen_box=True)

instruments = _create_instruments()