from dataclasses import dataclass

from redis import Redis

from ..message import Message
from .base import BaseCommand


@dataclass(frozen=True)
class CapCommand(BaseCommand):
    def respond(
        self, message: Message, redis: Redis = None, prev_message: Message = None
    ) -> Message:
        pass
