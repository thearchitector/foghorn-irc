from dataclasses import dataclass

from .enums import ErrorCode


@dataclass(frozen=True)
class ProtocolException(Exception):
    """Base class for all protocol exceptions."""

    error_code: ErrorCode

    @property
    def value(self):
        return self.error_code.value
