from gevent.server import StreamServer
from collections import defaultdict

from typing import DefaultDict
from .typing import Socket, Address

from .parsing import MSG_DELIMITER, MAX_MESSAGE_LENGTH, MAX_TAGS_LENGTH

from .message import Message

IRC_PORT = 6697


class IRCServer(StreamServer):
    def __init__(self, hostname: str, max_clients: int):
        self.buffer_map: DefaultDict[Address, bytes] = defaultdict(bytes)

        super().__init__((hostname, IRC_PORT), spawn=max_clients)

    def handle(self, socket: Socket, address: Address) -> None:  # pylint: disable=E0202
        buffer = self.buffer_map[address]

        while True:
            # read messages into the address's buffer until a delimiter is found
            while MSG_DELIMITER not in buffer:
                data = socket.recv(MAX_MESSAGE_LENGTH + MAX_TAGS_LENGTH)

                # if the socket is closed
                if not data:
                    return

                buffer += data

            # messages may be incomplete, so ensure to save the remainder of the
            # buffer for the next parsing cycle
            line, _, self.buffer_map[address] = buffer.partition(MSG_DELIMITER)

            try:
                # redundant, but nice to be explicit about whats happening here
                self.handle_message(line.decode("utf-8", "strict"))
            except UnicodeDecodeError:
                # as per spec impl recommendation, silently ignore any invalid messages.
                # this will include any messages that are encoded validly but not UTF-8
                pass

    def handle_message(self, line: str):
        msg = Message.from_line(line)
        pass
