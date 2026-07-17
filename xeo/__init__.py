"""xeo - Earth observation instruments in Python."""

__version__ = "0.2.1"
__author__ = "David Montero Loaiza <dml.mont@gmail.com>"
__all__ = [
    "Catalogue",
    "Instrument",
    "Instruments",
    "catalogue",
    "instruments",
    "plot_bands",
    "plot_srf",
]

from .xeo import (
    Catalogue,
    Instrument,
    Instruments,
    catalogue,
    instruments,
    plot_bands,
    plot_srf,
)
