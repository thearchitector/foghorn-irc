from .typing import Address

CLIENT_STATUS_RKEY = "status"
CLIENT_CAPS_RKEY = "caps"
CLIENT_VERSION_RKEY = "version"
CLIENT_PASS_RKEY = "password"


def client_rkey(addr: Address) -> str:
    """Returns the redis key for the given client address."""
    return f"client:{addr[0]}@{addr[1]}"
