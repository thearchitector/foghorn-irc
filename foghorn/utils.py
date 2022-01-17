"""
Different miscellaneous utility functions for parsing, ingestion, and egestion of
message packets sent to and from foghorn.
"""
from typing import Callable, List

from .enums import ErrorCode
from .errors import ProtocolException


def transform(transformers: List[Callable], args: List[str]):
    """
    Casts each argument in the list according to the behavior of the provided
    transformer. The number of transformers may mismatch the number of arguments
    only if the last transformer casts many.
    """
    transformed = []
    aiter = iter(args)
    for transformer in transformers:
        try:
            transformed.extend(transformer(args, aiter))
        except (TypeError, ValueError, StopIteration):
            # something went wrong during transformation, so the param was
            # super invalid or missing when expected
            raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

    # if there are remaining parameters, the incoming message must be
    # malformed for this server and is not processible, as the parameters
    # are unexpected
    try:
        next(aiter)
        raise ProtocolException(ErrorCode.ERR_UNKNOWNERROR, msg="Too many parameters.")
    except StopIteration:
        pass

    return transformed
