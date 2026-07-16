from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import TYPE_CHECKING, Any

from box import Box

from .utils import _load_JSON

if TYPE_CHECKING:
    import pandas as pd


class Catalogue(object):
    """Awesome Earth Observation Instruments catalogue. 🐈

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

    def search(self, **kwargs: Any) -> Instruments:
        """Search instruments using core metadata and spectral availability.

        Search values are matched exactly, except that ``start_date`` also
        accepts inclusive intervals formatted as
        ``YYYY-MM-DD/YYYY-MM-DD``. Different properties are combined with AND.
        A list supplied for one property uses OR, and list-valued instrument
        properties such as ``operator`` and ``platform`` match when any
        requested value is present.

        Parameters
        ----------
        **kwargs
            Required instrument properties to match. ``has_srf`` and
            ``has_bands`` are also accepted as boolean filters.

        Returns
        -------
        Instruments
            A frozen collection containing the matching instruments in
            catalogue order.

        Examples
        --------
        >>> import xeo
        >>> result = xeo.catalogue.search(operator=["ESA", "NASA"])
        >>> "MSI_S2A" in result and "OLI_L8" in result
        True
        >>> all(item.has_srf for item in xeo.catalogue.search(has_srf=True).values())
        True
        >>> list(xeo.catalogue.search(start_date="2000-01-01/2003-01-01"))
        ['MODIS_AQUA']
        """

        searchable_properties = (
            "id",
            "name",
            "acronym",
            "type",
            "platform_type",
            "platform",
            "operator",
            "start_date",
            "status",
            "availability",
            "references",
            "has_srf",
            "has_bands",
        )
        invalid_properties = set(kwargs).difference(searchable_properties)
        if invalid_properties:
            invalid = ", ".join(sorted(invalid_properties))
            allowed = ", ".join(searchable_properties)
            raise ValueError(
                f"unknown search properties: {invalid}. Allowed properties: {allowed}"
            )

        for property_name in ("has_srf", "has_bands"):
            if property_name in kwargs and not isinstance(kwargs[property_name], bool):
                raise TypeError(f"{property_name} must be a boolean")

        def parse_start_date_interval(value: Any) -> Any:
            if not isinstance(value, str) or "/" not in value:
                return value
            if value.count("/") != 1:
                raise ValueError(
                    "start_date intervals must use YYYY-MM-DD/YYYY-MM-DD"
                )

            start_text, end_text = value.split("/")
            try:
                start = date.fromisoformat(start_text)
                end = date.fromisoformat(end_text)
            except ValueError as error:
                raise ValueError(
                    "start_date intervals must use YYYY-MM-DD/YYYY-MM-DD"
                ) from error

            if start.isoformat() != start_text or end.isoformat() != end_text:
                raise ValueError(
                    "start_date intervals must use YYYY-MM-DD/YYYY-MM-DD"
                )
            if start > end:
                raise ValueError(
                    "start_date interval beginning must not be after its end"
                )
            return start, end

        requested_values = {
            property_name: query if isinstance(query, list) else [query]
            for property_name, query in kwargs.items()
        }
        if "start_date" in requested_values:
            requested_values["start_date"] = [
                parse_start_date_interval(value)
                for value in requested_values["start_date"]
            ]

        def matches(
            instrument: Instrument,
            property_name: str,
            requested: list[Any],
        ) -> bool:
            instrument_value = getattr(instrument, property_name)

            if property_name == "start_date":
                instrument_date = date.fromisoformat(instrument_value)
                for value in requested:
                    if isinstance(value, tuple):
                        start, end = value
                        if start <= instrument_date <= end:
                            return True
                    elif instrument_value == value:
                        return True
                return False

            if isinstance(instrument_value, list):
                return any(value in instrument_value for value in requested)
            return instrument_value in requested

        results = {
            instrument_id: instrument
            for instrument_id, instrument in self.instruments.items()
            if all(
                matches(instrument, property_name, requested)
                for property_name, requested in requested_values.items()
            )
        }
        return Instruments(results, frozen_box=True)

    def to_dict(self) -> dict[str, Any]:
        """Return an independent dictionary containing the raw catalogue."""

        return deepcopy(self.data)


class Instruments(Box):
    """Collection of instruments in the catalogue.

    Instruments support both mapping and attribute access. 😺

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
        """Identifiers of instruments in the same family. 🐈‍⬛"""

        return self._data.get("family", [])

    @property
    def platform_companions(self) -> list[str]:
        """Identifiers of other instruments on the same platform."""

        return self._data.get("platform_companions", [])

    def get_data_access(
        self,
        provider: str = "ee",
        processing_level: str = "primary",
    ) -> dict[str, str | None] | None:
        """Return metadata for an available data access point.

        Parameters
        ----------
        provider : str, default="ee"
            Data provider. One of ``ee``, ``planetary_computer``, ``cdse``, or
            ``eopf``.
        processing_level : str, default="primary"
            Processing level. One of ``primary``, ``boa``, ``toa``, or ``raw``.

        Returns
        -------
        dict or None
            A dictionary containing ``stac_endpoint``, ``collection``, and
            ``docs``. Missing values, such as the Earth Engine STAC endpoint,
            are represented by ``None``. ``None`` is returned when the provider
            or processing level is valid but unavailable for this instrument.

        Examples
        --------
        >>> import xeo
        >>> xeo.instruments.MSI_S2A.get_data_access()["collection"]
        'COPERNICUS/S2_SR_HARMONIZED'
        >>> xeo.instruments.MSI_S2A.get_data_access("cdse", "toa")["collection"]
        'sentinel-2-l1c'
        >>> xeo.instruments.MSI_S2A.get_data_access(processing_level="raw") is None
        True
        """

        providers = {
            "ee": "ee",
            "planetary_computer": "planetary_computer",
            "cdse": "cdse",
            "eopf": "eopf",
        }
        processing_levels = ("primary", "boa", "toa", "raw")

        if provider not in providers:
            choices = ", ".join(providers)
            raise ValueError(
                f"provider must be one of: {choices}; received {provider!r}"
            )
        if processing_level not in processing_levels:
            choices = ", ".join(processing_levels)
            raise ValueError(
                "processing_level must be one of: "
                f"{choices}; received {processing_level!r}"
            )

        data_access = self.extensions.get("data_access", {})
        provider_metadata = data_access.get(providers[provider])
        if not isinstance(provider_metadata, dict):
            return None

        access_metadata = provider_metadata.get(processing_level)
        if not isinstance(access_metadata, dict):
            return None

        return {
            "stac_endpoint": provider_metadata.get("stac_endpoint"),
            "collection": access_metadata.get("collection"),
            "docs": access_metadata.get("docs"),
        }

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
        """Return the spectral response function as a DataFrame, when available. 🐱

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
