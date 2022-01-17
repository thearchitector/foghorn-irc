import secrets
from dataclasses import dataclass
from typing import Any, List, Optional

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from redis import Redis

from ..enums import ClientStatus, ErrorCode
from ..errors import ProtocolException
from ..message import Message
from ..storage import CLIENT_STATUS_RKEY, client_rkey
from ..typing import Address
from .base import BaseCommand

KDF = Scrypt(salt=secrets.token_bytes(), length=32, n=2 ** 14, r=8, p=1)


@dataclass(frozen=True)
class PassCommand(BaseCommand):
    def respond(
        self,
        address: Address,
        message: Message,
        redis: Redis,
        casted_params: List[Any] = None,
        prev_message: Message = None,
    ) -> Optional[Message]:
        assert casted_params
        client_key = client_rkey(address)
        status = redis.hget(client_key, CLIENT_STATUS_RKEY)

        if status == ClientStatus.NEGOTIATING:
            encrypted_passwd = KDF.derive(casted_params[0])
        elif status == ClientStatus.REGISTERED:
            raise ProtocolException(
                ErrorCode.ERR_ALREADYREGISTERED,
                msg="You cannot set your password after registration.",
            )

        return None
