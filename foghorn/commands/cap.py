from dataclasses import dataclass
from typing import Any, List, Optional

from redis import Redis

from ..enums import Capabilities, CapSubCommand, ClientStatus, Command, ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..parsing import ANY_CLIENT
from ..storage import (
    CLIENT_CAPS_RKEY,
    CLIENT_STATUS_RKEY,
    CLIENT_VERSION_RKEY,
    client_rkey,
)
from ..typing import Address
from ..utils import transform
from .base import BaseCommand


@dataclass(frozen=True)
class CapCommand(BaseCommand):
    def respond(
        self,
        address: Address,
        message: Message,
        redis: Redis,
        casted_params: List[Any] = None,
        prev_message: Message = None,
    ) -> Optional[Message]:
        if not message.params:
            raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

        # ensure valid command
        if message.params[0] not in CapSubCommand.__members__.keys():
            raise ProtocolException(ErrorCode.ERR_INVALIDCAPCMD)
        else:
            command = CapSubCommand[message.params[0].upper()]

        # if the subcommand expects parameters, transform them
        if command.value:
            casted_params = transform(command.value, message.params[1:])

        # initiate capability negotiation
        if command == CapSubCommand.LS or command == CapSubCommand.REQ:
            # if the client is unregistered, set their status to ensure we process
            # them correctly. an incoming LS or REQ command does not always indicate
            # the beginning of a negotation, as it may have happened already.
            client_key = client_rkey(address)
            if (
                redis.hget(client_key, CLIENT_STATUS_RKEY)
                == ClientStatus.UNREGISTERED.value
            ):
                redis.hset(
                    client_key, CLIENT_STATUS_RKEY, ClientStatus.NEGOTIATING.value
                )

            assert casted_params  # calm down mypy
            if command == CapSubCommand.LS:
                version = casted_params[0] or 300

                # set the client negotiation if one is not set, or if the client
                # has indicated a higher version that currently registered
                if (redis.hget(client_key, CLIENT_VERSION_RKEY) or -1) < version:
                    redis.hset(client_key, CLIENT_VERSION_RKEY, version)
            elif command == CapSubCommand.REQ:
                req_caps = casted_params[1:]

                # if the client requests a capability we don't offer, including those
                # with values, reject the entire request
                if not {*req_caps}.issubset({c.value for c in Capabilities}):
                    return Message(
                        verb=Command.CAP,
                        params=[ANY_CLIENT, CapSubCommand.NAK.name, *req_caps],
                    )
                else:
                    # store client capabilities and accept the request
                    redis.hset(client_key, CLIENT_CAPS_RKEY, ";".join(req_caps))
                    return Message(
                        verb=Command.CAP,
                        params=[ANY_CLIENT, CapSubCommand.ACK.name, *req_caps],
                    )

        return None
