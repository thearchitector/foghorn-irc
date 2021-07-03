"""
Different miscellaneous utility functions for parsing, ingestion, and egestion of
message packets sent to and from foghorn.
"""
from typing import Callable, Type

from .typing import Address


def typecaster(t: Type) -> Callable:
    """Returns a function to optionally cast a given arg to the provided type."""
    return lambda v: t(v) if v is not None else None


def client_rkey(addr: Address) -> str:
    """Returns the redis key for the given client address."""
    return f"client:{addr[0]}@{addr[1]}"
