from dataclasses import dataclass
from typing import Any, List, Optional

from redis import Redis

from ..enums import ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..parsing import INVALID_CHARACTER_PATTERN
from .base import BaseCommand


@dataclass(frozen=True)
class NickCommand(BaseCommand):
    def respond(
        self,
        client_key: str,
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

        return None
