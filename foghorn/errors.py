from dataclasses import dataclass

from .numerics import ErrorCode


@dataclass(frozen=True)
class ProtocolException(Exception):
    """Base class for all protocol exceptions."""

    error_code: ErrorCode

    def value(self):
        return self.error_code.value
