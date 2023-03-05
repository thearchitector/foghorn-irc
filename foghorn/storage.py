from typing import List

from redis import Redis

from .typing import Address

CLIENT_STATUS_RKEY = "status"
CLIENT_CAPS_RKEY = "caps"
CLIENT_VERSION_RKEY = "version"
CLIENT_PASS_RKEY = "password"

CAP_DELIMITER = ";"
STATUS_DELIMITER = ";"


def client_rkey(addr: Address) -> str:
    """Returns the redis key for the given client address."""
    return f"client:{addr[0]}@{addr[1]}"


def get_statuses(redis: Redis, client_key: str) -> List[str]:
    """Returns the registration status of the given client."""
    return str(redis.hget(client_key, CLIENT_STATUS_RKEY) or "").split(CAP_DELIMITER)
