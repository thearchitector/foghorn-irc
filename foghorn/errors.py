from typing import List, Optional

from .enums import ErrorCode


class ProtocolException(Exception):
    """Base class for all protocol exceptions."""

    def __init__(
        self, error_code: ErrorCode, params: Optional[List[str]] = None, msg: str = None
    ):
        self.error_code = error_code
        self.numeric = self.error_code.numeric
        self.params = params or []
        self.msg = msg or self.error_code.msg

        if not msg:
            raise TypeError(
                "The given error has no default message, so one must be provided."
            )
