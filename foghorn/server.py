from itertools import zip_longest
from typing import Callable, Dict

from gevent.queue import LifoQueue
from gevent.server import StreamServer
from redis import BlockingConnectionPool, Redis

from .commands import COMMANDS
from .enums import ErrorCode
from .errors import ProtocolException
from .message import Message
from .parsing import MAX_MESSAGE_LENGTH, MAX_TAGS_LENGTH, MSG_DELIMITER
from .typing import Address, Socket

IRC_PORT = 6697


class IRCServer(StreamServer):
    def __init__(self, hostname: str, max_clients: int = 100, redis_timeout: int = 20):
        self._connection_buffer_map: Dict[Address, bytes] = {}
        self._previous_messages: Dict[Address, Message] = {}
        self._redis_connection_pool = BlockingConnectionPool(
            queue_class=LifoQueue, max_connections=max_clients, timeout=redis_timeout
        )

        super().__init__((hostname, IRC_PORT), spawn=max_clients)

    def handle(self, socket: Socket, address: Address) -> None:  # pylint: disable=E0202
        buffer = self._connection_buffer_map.get(address, b"")

        while True:
            # read messages into the address's buffer until a delimiter is found
            while MSG_DELIMITER not in buffer:
                # closest power of 2
                data = socket.recv(
                    (MAX_MESSAGE_LENGTH + MAX_TAGS_LENGTH - 2).bit_length()
                )

                # if the socket is closed
                if not data:
                    return

                # TODO: read atom sizes for compliance while reading buffer instead
                # of decoding and re-encoding utf-8

                buffer += data

            # messages may be incomplete, so ensure to save the remainder of the
            # buffer for the next parsing cycle
            line, _, self._connection_buffer_map[address] = buffer.partition(
                MSG_DELIMITER
            )

            try:
                # redundant, but nice to be explicit about whats happening here
                resp = self.handle_message(
                    socket, address, line.decode("utf-8", "strict")
                )
            except UnicodeDecodeError:
                # as per spec impl recommendation, silently ignore any invalid messages.
                # this will include any messages that are encoded validly but not UTF-8
                continue
            except ProtocolException as err:
                # if a protocol exception happened, send back the error numeric
                # resp = err.response
                pass

            socket.sendall(resp.to_line().encode("utf-8"))

    def handle_message(self, socket: Socket, address: Address, line: str) -> Message:
        msg = Message.from_line(line)
        executor = COMMANDS[msg.verb]

        # attempt to cast all the given parameters to their expected types. most params
        # will remain strings and checked downstream, but this will raise any missing
        # or
        casted_params = []
        if executor.required_params:
            for transformer, given in zip_longest(
                executor.required_params.values(), msg.params
            ):
                # if the transfomer is None, we got more parameters than
                # we expected
                if not transformer:
                    raise ProtocolException(ErrorCode.ERR_UNKNOWNERROR)

                try:
                    # all types except int and float will cast None to some value,
                    # which is not the behavior we want
                    if transformer != int and transformer != float and given is None:
                        raise TypeError

                    casted_params.append(transformer(given))
                except (TypeError, ValueError):
                    # something went wrong during transformation, so the param was
                    # super invalid or missing when expected
                    raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

        def _check_context(context, verb):
            # throw an unknown error (since no numeric is standardized) if the order of
            # the messages is unexpected
            if context and (
                (isinstance(context, Callable) and not context(verb)) or context != verb
            ):
                raise ProtocolException(ErrorCode.ERR_UNKNOWNERROR)

        prev_msg = self._previous_messages.get(address)
        if prev_msg:
            del self._previous_messages[address]
            # check if the preceding command is what the current one expects
            _check_context(executor.required_pre_context, prev_msg.verb)
            # check if the current command is required by the preceding one
            _check_context(COMMANDS[prev_msg.verb].required_post_context, msg.verb)

        # if the executor creates a Redis session (the default unless specified)
        redis = None
        if executor.needs_redis:
            redis = Redis(connection_pool=self._redis_connection_pool)

        # actually process the incoming message and generate a response
        response = executor.respond(
            msg,
            redis=redis,
            prev_message=prev_msg,
        )

        # save the incoming context if requested
        if executor.save_context:
            self._previous_messages[address] = msg

        # send the response, exhausting the entire bytestream
        return response
