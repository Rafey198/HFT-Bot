"""Lightweight structured logging helper."""
from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "aurumfx") -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(fmt)
        root = logging.getLogger("aurumfx")
        root.setLevel(logging.INFO)
        root.handlers.clear()
        root.addHandler(handler)
        _CONFIGURED = True
    return logging.getLogger(name if name.startswith("aurumfx") else f"aurumfx.{name}")
