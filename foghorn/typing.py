from typing import Tuple

from gevent._socket3 import socket

Socket = socket
Address = Tuple[str, int]  # ip address, port
