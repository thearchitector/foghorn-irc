from typing import Any, Callable, Iterator, List, Tuple, Type

from gevent._socket3 import socket

Socket = socket
Address = Tuple[str, int]  # ip address, port


def typecaster(t: Type, many=False, optional=False) -> Callable:
    """
    Returns a function to cast the next arg in an iterator to the provided type. If
    optional=True, individual parameters that don't exist are treated as optional. If
    many=True, the returned Callable will accept and cast all items in the iterator.
    In both cases, arguments are exhausted as they are casted.
    """
    if many and optional:
        raise TypeError(
            "'many' and 'optional' are mutually exclusive options, and cannot both be set to `True`."
        )

    def _cast(params: List[str], args: Iterator) -> Any:
        if many:
            # cast all remaining parameters to the given type
            return [t(next(args)) for _ in params]
        else:
            # attempt to case the current parameter to the given type,
            # returning None if non-existent
            try:
                return t(next(args))
            except StopIteration:
                if not optional:
                    raise

                return None

    return _cast
