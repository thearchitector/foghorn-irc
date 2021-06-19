"""
Different miscellaneous utility functions for parsing, ingestion, and egestion of
message packets sent to and from foghorn.
"""
from typing import Callable, Type


def typecaster(t: Type) -> Callable:
    return lambda v: t(v) if v is not None else None
