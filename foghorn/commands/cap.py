from dataclasses import dataclass
from typing import Any, List, Optional

from redis import Redis

from ..enums import Capabilities, CapSubCommand, ClientStatus, Command, ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..parsing import ANY_CLIENT, PARAM_PREFIX, REMOVE_CAP_PREFIX
from ..storage import (
    CAP_DELIMITER,
    CLIENT_CAPS_RKEY,
    CLIENT_STATUS_RKEY,
    CLIENT_VERSION_RKEY,
    STATUS_DELIMITER,
    get_statuses,
)
from ..utils import transform
from .base import BaseCommand


@dataclass(frozen=True)
class CapCommand(BaseCommand):
    def respond(
        self,
        client_key: str,
        message: Message,
        redis: Redis,
        casted_params: List[Any] = None,
        prev_message: Message = None,
    ) -> Optional[Message]:
        if not message.params:
            raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

        # ensure valid command
        _command = message.params[0].upper()
        if _command not in CapSubCommand.__members__.keys():
            raise ProtocolException(
                ErrorCode.ERR_INVALIDCAPCMD,
                params=[ANY_CLIENT, _command],
            )
        else:
            command = CapSubCommand[_command]

        # if the subcommand expects parameters, transform them
        if command.value:
            casted_params = transform(command.value, message.params[1:])

        # initiate capability negotiation
        if command == CapSubCommand.LS or command == CapSubCommand.REQ:
            # set the client's status to ensure we process them correctly.
            # an incoming LS or REQ command does not always indicate
            # the beginning of a negotiation, as it may have happened already, so
            # we need to keep track of both the previous and new status
            # to ensure we set it back correctly when negotiation completes.
            statuses = get_statuses(redis, client_key)
            if statuses[0] != ClientStatus.NEGOTIATING:
                redis.hset(
                    client_key,
                    CLIENT_STATUS_RKEY,
                    ClientStatus.NEGOTIATING + STATUS_DELIMITER + statuses[0],
                )

            assert casted_params  # calm down mypy
            if command == CapSubCommand.LS:
                version = casted_params[0] or 300

                # set the client negotiation if one is not set, or if the client
                # has indicated a higher version that currently registered
                if (redis.hget(client_key, CLIENT_VERSION_RKEY) or -1) < version:
                    redis.hset(client_key, CLIENT_VERSION_RKEY, version)

                return Message(
                    verb=Command.CAP,
                    params=[
                        ANY_CLIENT,
                        CapSubCommand.LS.name,
                        *[cap.value for cap in Capabilities],
                    ],
                )
            elif command == CapSubCommand.REQ:
                # if the first parameter doesn't start with the prefix it isn't valid
                if casted_params[0][0] != PARAM_PREFIX:
                    raise ProtocolException(ErrorCode.ERR_NEEDMOREPARAMS)

                req_caps = set(casted_params[0][1:] + casted_params[1:])
                caps_to_add = {cap for cap in req_caps if cap[0] != REMOVE_CAP_PREFIX}
                caps_to_remove = req_caps - caps_to_add

                # if the client requests a capability we don't offer, including those
                # with values, reject the entire request. ensure to strip the removal
                # prefix from the caps to remove before checking the set inclusion
                if not (caps_to_add | ({cap[1:] for cap in caps_to_remove})).issubset(
                    {c.value for c in Capabilities}
                ):
                    return Message(
                        verb=Command.CAP,
                        params=[ANY_CLIENT, CapSubCommand.NAK.name, *req_caps],
                    )
                else:
                    # add or remove client capabilities, store them, and accept the
                    # request
                    current_caps = set(
                        (redis.hget(client_key, CLIENT_CAPS_RKEY) or "").split(
                            CAP_DELIMITER
                        )
                    )

                    # assume deletions take precedence over additions to ensure we
                    # don't add a capability when it should be removed. this is only
                    # a problem if a client asks to add and remove the same cap in
                    # the same message
                    current_caps.update(caps_to_add)
                    current_caps.difference_update(caps_to_remove)

                    redis.hset(
                        client_key, CLIENT_CAPS_RKEY, CAP_DELIMITER.join(current_caps)
                    )
                    return Message(
                        verb=Command.CAP,
                        params=[ANY_CLIENT, CapSubCommand.ACK.name, *current_caps],
                    )
        elif command == CapSubCommand.END:
            # if the client was negotiating, change their status back to what it was
            # before
            statuses = get_statuses(redis, client_key)
            if statuses[0] == ClientStatus.NEGOTIATING:
                redis.hset(client_key, CLIENT_STATUS_RKEY, statuses[1])

        return None
