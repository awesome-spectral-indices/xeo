"""Download and cache spectral response function CSV files."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pandas as pd
from platformdirs import user_cache_path


_CACHE_ENVIRONMENT_VARIABLE = "XEO_CACHE_DIR"
_DOWNLOAD_TIMEOUT_SECONDS = 30


def _safe_path_component(value: str, label: str) -> str:
    """Return a trusted single path component."""

    if not value or value in {".", ".."} or Path(value).name != value:
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def _cache_root() -> Path:
    """Return the configurable per-user cache root."""

    configured = os.environ.get(_CACHE_ENVIRONMENT_VARIABLE)
    if configured:
        return Path(configured).expanduser()
    return user_cache_path("xeo")


def _srf_cache_path(
    catalogue_version: str,
    instrument_id: str,
    filename: str,
) -> Path:
    """Return the cache path for one instrument SRF."""

    version = _safe_path_component(catalogue_version, "catalogue version")
    instrument = _safe_path_component(instrument_id, "instrument id")
    safe_filename = _safe_path_component(filename, "SRF filename")
    return _cache_root() / "srf" / version / instrument / safe_filename


def _read_srf(
    path: Path,
    expected_bands: list[str] | None,
) -> pd.DataFrame:
    """Read and validate an SRF CSV."""

    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"SRF CSV is empty: {path}")
    if "wavelength" not in frame.columns:
        raise ValueError(f"SRF CSV has no wavelength column: {path}")

    if expected_bands is not None:
        response_columns = [
            column for column in frame.columns if column != "wavelength"
        ]
        if response_columns != expected_bands:
            raise ValueError(
                "SRF columns do not match the instrument bands. "
                f"Expected {expected_bands}, found {response_columns}."
            )
    return frame


def _download_srf(
    url: str,
    destination: Path,
    expected_bands: list[str] | None,
) -> pd.DataFrame:
    """Download, validate, and atomically cache an SRF CSV."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        request = Request(url, headers={"User-Agent": "xeo"})
        with urlopen(request, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as response:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{destination.name}.",
                suffix=".part",
                dir=destination.parent,
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                shutil.copyfileobj(response, temporary)

        frame = _read_srf(temporary_path, expected_bands)
        os.replace(temporary_path, destination)
        temporary_path = None
        return frame
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_srf(
    *,
    url: str,
    filename: str,
    catalogue_version: str,
    instrument_id: str,
    expected_bands: list[str] | None,
    refresh: bool = False,
) -> pd.DataFrame:
    """Return an SRF from the cache, downloading it when necessary."""

    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError(f"invalid SRF URL for {instrument_id}: {url!r}")

    cache_path = _srf_cache_path(
        catalogue_version,
        instrument_id,
        filename,
    )
    if cache_path.is_file() and not refresh:
        try:
            return _read_srf(cache_path, expected_bands)
        except (OSError, UnicodeError, ValueError):
            cache_path.unlink(missing_ok=True)

    try:
        return _download_srf(url, cache_path, expected_bands)
    except Exception as error:
        raise RuntimeError(
            f"Unable to download the SRF for {instrument_id} from {url}. "
            f"Check the network connection or set {_CACHE_ENVIRONMENT_VARIABLE} "
            "to a writable cache directory."
        ) from error
