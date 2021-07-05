"""
Different miscellaneous utility functions for parsing, ingestion, and egestion of
message packets sent to and from foghorn.
"""
from typing import Any, Callable, Iterator, List, Type, Union

from .enums import ErrorCode
from .errors import ProtocolException
from .typing import Address


def typecaster(t: Type, many=False) -> Callable:
    """
    Returns a function to cast the next arg in an iterator to the provided type. If
    many=False (default), parameters that don't exist are treated as optional. If
    many=True, the returned Callable will accept and cast all items in the iterator.
    In both cases, arguments are exhausted as they are casted.
    """

    def _cast(params: List[str], args: Iterator) -> Any:
        if many:
            # cast all remaining parameters to the given type
            return [t(next(args)) for _ in params]
        else:
            # attempt to case the current parameter to the given type,
            # returning None if non-existent
            try:
                return [t(next(args))]
            except StopIteration:
                return None

    return _cast


def transform(transformers: List[Union[Type, Callable]], args: List[str]):
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
    if next(aiter):
        raise ProtocolException(ErrorCode.ERR_UNKNOWNERROR)

    return transformed
