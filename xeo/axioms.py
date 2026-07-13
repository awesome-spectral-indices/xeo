from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from box import Box
from rich.console import Console, RenderResult
from rich.table import Table

from .utils import _load_JSON

if TYPE_CHECKING:
    import pandas as pd


class Catalogue(object):
    """Awesome Earth Observation Instruments catalogue.

    Parameters
    ----------
    catalogue : dict
        Raw catalogue data.
    instruments : Instruments, optional
        Instrument objects created from the raw catalogue.

    Examples
    --------
    >>> import xeo
    >>> xeo.catalogue
    Awesome Earth Observation Instruments (v0.1.0)
    >>> len(xeo.catalogue.instruments)
    28
    """

    def __init__(
        self,
        catalogue: dict[str, Any],
        instruments: Instruments | None = None,
    ):
        self.data = catalogue
        """Raw, JSON-serializable catalogue data."""

        self.name = catalogue["name"]
        """Name of the catalogue."""

        self.version = catalogue["version"]
        """Version of the catalogue."""

        self.link = catalogue["link"]
        """URL of the catalogue."""

        self.href = catalogue["link"]
        """URL of the catalogue. Equivalent to :attr:`link`."""

        if instruments is None:
            instruments = Instruments(
                {
                    key: Instrument(value)
                    for key, value in catalogue["instruments"].items()
                },
                frozen_box=True,
            )
        self.instruments = instruments
        """Instruments available in the catalogue."""

    def __repr__(self) -> str:
        """Return a concise machine-readable representation."""

        return f"{self.name} (v{self.version})"

    def __str__(self) -> str:
        """Return a concise human-readable representation."""

        return f"{self.name} (v{self.version})"

    def to_dict(self) -> dict[str, Any]:
        """Return an independent dictionary containing the raw catalogue."""

        return deepcopy(self.data)


class Instruments(Box):
    """Collection of instruments in the catalogue.

    Instruments support both mapping and attribute access.

    Examples
    --------
    >>> import xeo
    >>> xeo.instruments.MSI_S2A
    Instrument(MSI_S2A: MultiSpectral Instrument)
    >>> xeo.instruments["MSI_S2A"] is xeo.instruments.MSI_S2A
    True
    """

    def __repr__(self) -> str:
        """Return the collection name and its instrument identifiers."""

        return f"Instruments({list(self.keys())})"

    def __str__(self) -> str:
        """Return the available instrument identifiers."""

        return f"{list(self.keys())}"

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

        for instrument in self.values():
            status_color = status_colors.get(instrument.status, "white")
            styled_status = (
                f"[{status_color}]{instrument.status}[/{status_color}]"
            )

            type_color = type_colors.get(instrument.type, "white")
            styled_type = f"[{type_color}]{instrument.type}[/{type_color}]"

            platform_color = platform_colors.get(instrument.platform_type, "white")
            styled_platform = (
                f"[{platform_color}]{instrument.platform_type}[/{platform_color}]"
            )

            table.add_row(
                instrument.id,
                instrument.acronym,
                instrument.name,
                ", ".join(instrument.platform),
                styled_platform,
                styled_type,
                styled_status,
            )

        yield table


class Instrument(object):
    """Earth observation instrument from the catalogue.

    Core metadata is available directly as attributes. The complete source record
    remains available through :attr:`data`.

    Examples
    --------
    >>> import xeo
    >>> xeo.instruments.MSI_S2A
    Instrument(MSI_S2A: MultiSpectral Instrument)
    >>> xeo.instruments.MSI_S2A.operator
    ['ESA', 'Copernicus']
    >>> xeo.instruments.MSI_S2A.bands().shape
    (13, 6)
    """

    def __init__(self, instrument: dict[str, Any]):
        self._data = instrument

    @property
    def data(self) -> dict[str, Any]:
        """Complete instrument record from the catalogue."""

        return self._data

    @property
    def id(self) -> str:
        """Instrument identifier."""

        return self._data["id"]

    @property
    def name(self) -> str:
        """Full instrument name."""

        return self._data["name"]

    @property
    def acronym(self) -> str:
        """Instrument acronym."""

        return self._data["acronym"]

    @property
    def type(self) -> str:
        """Instrument sensing modality."""

        return self._data["type"]

    @property
    def platform_type(self) -> str:
        """Class of platform carrying the instrument."""

        return self._data["platform_type"]

    @property
    def platform(self) -> list[str]:
        """Platforms carrying the instrument."""

        return self._data["platform"]

    @property
    def operator(self) -> list[str]:
        """Organizations operating the instrument."""

        return self._data["operator"]

    @property
    def start_date(self) -> str:
        """Start of instrument operation."""

        return self._data["start_date"]

    @property
    def end_date(self) -> str | None:
        """End of instrument operation, when available."""

        return self._data.get("end_date")

    @property
    def status(self) -> str:
        """Instrument lifecycle status."""

        return self._data["status"]

    @property
    def availability(self) -> str:
        """Instrument data accessibility level."""

        return self._data["availability"]

    @property
    def references(self) -> list[str]:
        """Reference URLs for the instrument."""

        return self._data["references"]

    @property
    def data_links(self) -> list[str]:
        """URLs where instrument data products can be accessed."""

        return self._data.get("data_links", [])

    @property
    def notes(self) -> str | None:
        """Additional notes, when available."""

        return self._data.get("notes")

    @property
    def extensions(self) -> dict[str, Any]:
        """Domain-specific instrument metadata extensions."""

        return self._data.get("extensions", {})

    @property
    def extension_names(self) -> list[str]:
        """Names of the extensions available for this instrument."""

        return list(self.extensions)

    @property
    def family(self) -> list[str]:
        """Identifiers of instruments in the same family."""

        return self._data.get("family", [])

    @property
    def platform_companions(self) -> list[str]:
        """Identifiers of other instruments on the same platform."""

        return self._data.get("platform_companions", [])

    @property
    def has_bands(self) -> bool:
        """Whether materialized spectral band definitions are available."""

        bands = self.extensions.get("spectral", {}).get("bands")
        return isinstance(bands, dict) and bool(bands)

    @property
    def has_srf(self) -> bool:
        """Whether a spectral response function is available."""

        srf = self.extensions.get("spectral", {}).get(
            "spectral_response_function"
        )
        return isinstance(srf, dict) and bool(srf)

    def bands(self) -> pd.DataFrame | None:
        """Return spectral bands as a DataFrame, when available.

        The DataFrame is indexed by band identifier. ``None`` is returned when
        the instrument has no materialized spectral band definitions.
        """

        bands = self.extensions.get("spectral", {}).get("bands")
        if not isinstance(bands, dict) or not bands:
            return None

        import pandas as pd

        frame = pd.DataFrame.from_dict(bands, orient="index")
        frame.index.name = "band"
        return frame

    def srf(self) -> pd.DataFrame | None:
        """Return the spectral response function as a DataFrame, when available.

        ``None`` is returned when the instrument has no spectral response
        function in the catalogue.
        """

        srf = self.extensions.get("spectral", {}).get(
            "spectral_response_function"
        )
        if not isinstance(srf, dict) or not srf:
            return None

        import pandas as pd

        return pd.DataFrame.from_dict(srf, orient="columns")

    def __repr__(self) -> str:
        """Return the instrument identifier and name."""

        return f"Instrument({self.id}: {self.name})"

    def __str__(self) -> str:
        """Return a concise human-readable representation."""

        return f"{self.id}: {self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Return an independent dictionary containing the instrument record."""

        return deepcopy(self._data)


def _create_catalogue() -> tuple[Catalogue, Instruments]:
    """Create the catalogue and its shared instrument collection."""

    catalogue_data = _load_JSON()
    instrument_objects = {
        key: Instrument(value)
        for key, value in catalogue_data["instruments"].items()
    }
    instrument_collection = Instruments(instrument_objects, frozen_box=True)

    return (
        Catalogue(catalogue_data, instruments=instrument_collection),
        instrument_collection,
    )


catalogue, instruments = _create_catalogue()
