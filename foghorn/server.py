import math
from typing import Callable, Dict, Optional

from gevent.queue import LifoQueue
from gevent.server import StreamServer
from redis import BlockingConnectionPool, Redis

from .commands import COMMANDS
from .commands.cap import ClientStatus
from .enums import ErrorCode
from .errors import ProtocolException
from .message import Message
from .parsing import MAX_MESSAGE_LENGTH, MAX_TAGS_LENGTH, MSG_DELIMITER
from .storage import CLIENT_STATUS_RKEY, client_rkey, get_statuses
from .typing import Address, Socket
from .utils import transform

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

        # create an unregistered client for the new address
        with Redis(connection_pool=self._redis_connection_pool) as redis:
            redis.hset(
                client_rkey(address),
                CLIENT_STATUS_RKEY,
                ClientStatus.UNREGISTERED.value,
            )

        while True:
            # read messages into the address's buffer until a delimiter is found
            while MSG_DELIMITER not in buffer:
                # closest power of 2
                try:
                    data = socket.recv(
                        math.ceil(
                            (MAX_MESSAGE_LENGTH + MAX_TAGS_LENGTH - 2).bit_length() / 8
                        )
                    )
                finally:
                    # if the socket is closed
                    if not data:
                        # delete all traces of the client
                        with Redis(
                            connection_pool=self._redis_connection_pool
                        ) as redis:
                            client_key = client_rkey(address)
                            redis.delete(client_key)

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
                resp = Message(verb=err.numeric, params=err.params + [err.msg])

            # send the response if exists, exhausting the entire bytestream
            if resp:
                socket.sendall(resp.to_line().encode("utf-8"))

    def _check_context(self, context, verb):
        # throw an unknown error (since no numeric is standardized) if the order of
        # the messages is unexpected
        if context and (
            (isinstance(context, Callable) and not context(verb)) or context != verb
        ):
            raise ProtocolException(ErrorCode.ERR_UNKNOWNERROR)

    def handle_message(
        self, socket: Socket, address: Address, line: str
    ) -> Optional[Message]:
        msg = Message.from_line(line)
        executor = COMMANDS[msg.verb]

        with Redis(connection_pool=self._redis_connection_pool) as redis:
            # ensure that the client is registered unless the command allows
            # them to be unregistered (for commands sent in order to register)
            client_key = client_rkey(address)
            if not executor.allow_unregistered and get_statuses(redis, client_key) != [
                ClientStatus.REGISTERED
            ]:
                raise ProtocolException(ErrorCode.ERR_NOTREGISTERED)

            # attempt to cast all the given parameters to their expected types
            casted_params = (
                transform(executor.required_params, msg.params)
                if executor.required_params
                else None
            )

            prev_msg = self._previous_messages.get(address)
            if prev_msg:
                del self._previous_messages[address]
                # check if the preceding command is what the current one expects
                self._check_context(executor.required_pre_context, prev_msg.verb)
                # check if the current command is required by the preceding one
                self._check_context(
                    COMMANDS[prev_msg.verb].required_post_context, msg.verb
                )

            # actually process the incoming message and generate a response
            response: Optional[Message] = executor.respond(
                client_key,
                msg,
                redis,
                prev_message=prev_msg,
                casted_params=casted_params,
            )

        # save the incoming context if requested
        if executor.save_context:
            self._previous_messages[address] = msg

        return response
