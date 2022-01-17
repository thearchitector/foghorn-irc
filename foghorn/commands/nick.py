from dataclasses import dataclass
from typing import Any, List, Optional

from redis import Redis

from ..enums import ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..parsing import INVALID_CHARACTER_PATTERN
from ..storage import CLIENT_STATUS_RKEY, client_rkey
from ..typing import Address
from .base import BaseCommand


@dataclass(frozen=True)
class NickCommand(BaseCommand):
    def respond(
        self,
        address: Address,
        message: Message,
        redis: Redis,
        casted_params: List[Any] = None,
        prev_message: Message = None,
    ) -> Optional[Message]:
        assert casted_params

        nickname = casted_params[0]
        if not nickname:
            # no nickname supplied
            raise ProtocolException(ErrorCode.ERR_NONICKNAMEGIVEN)
        elif INVALID_CHARACTER_PATTERN.search(nickname):
            # an invalid nickname was supplied (contains special characters except '-')
            raise ProtocolException(ErrorCode.ERR_ERRONEUSNICKNAME)

        client_key = client_rkey(address)
        status = redis.hget(client_key, CLIENT_STATUS_RKEY)

        return None
