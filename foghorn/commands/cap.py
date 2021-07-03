from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import Any, List, Optional

from redis import Redis

from ..enums import ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..typing import Address
from .base import BaseCommand
from .utils import client_rkey


@dataclass(frozen=True)
class CapCommand(BaseCommand):
    def respond(
        self,
        address: Address,
        message: Message,
        redis: Redis,
        prev_message: Message = None,
    ) -> Optional[Message]:
        if not message.params:
            raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

        # ensure valid command
        command = params[0]
        if command not in Command.__members__.keys():
            raise ProtocolException(ErrorCode.ERR_INVALIDCAPCMD)
        else:
            command = Command[command]

        # initiate capability negotiation
        if command == Command.LS or command == Command.REQ:
            client_key = client_rkey(address)
            if redis.hget(client_key, "status") == ClientStatus.UNREGISTERED.value:
                redis.hset(client_key, "status", ClientStatus.NEGOTIATING.value)

            if command == Command.LS:
                version = casted_params[1] or 300

                # set the client negotiation
                if (redis.hget(client_key, "version") or -1) < version:
                    redis.hset(client_key, "version", version)

            if command == Command.REQ:
                

        return None
