from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Type, Union

from redis import Redis

from ..enums import Command
from ..message import Message


# mypy: ignore_errors
@dataclass(frozen=True)
class BaseCommand(ABC):
    needs_redis: bool = True
    # all required parameters and their expected typings
    required_params: Optional[Dict[str, Union[Type, Callable[Type]]]] = None
    # the expected preceding and proceeding commands
    save_context: bool = False
    required_pre_context: Optional[Union[Command, Callable[[Command], Command]]] = None
    required_post_context: Optional[Union[Command, Callable[[Command], bool]]] = None

    @abstractmethod
    def respond(
        self, message: Message, redis: Redis = None, prev_message: Message = None
    ) -> Message:
        """
        Responds to the provided message, optionally storing correlated information
        in the given Redis session. Each Redis session is isolated within the specific
        response context, which runs under a unique greenlet for every incoming packet.
        """
        raise NotImplementedError()
