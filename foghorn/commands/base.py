from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Union

from redis import Redis

from ..enums import Command
from ..message import Message
from ..typing import Address


@dataclass(frozen=True)  # type: ignore[misc]
class BaseCommand(ABC):
    # all required parameters and their expected typings
    required_params: Optional[List[Callable]] = None
    save_context: bool = False
    # the expected preceding and proceeding commands
    required_pre_context: Optional[Union[Command, Callable[[Command], Command]]] = None
    required_post_context: Optional[Union[Command, Callable[[Command], bool]]] = None

    @abstractmethod
    def respond(
        self,
        address: Address,
        message: Message,
        redis: Redis,
        casted_params: List[Any] = None,
        prev_message: Message = None,
    ) -> Optional[Message]:
        """
        Optionally responds to the provided message, optionally storing correlated
        information in the given Redis session. Each Redis session is isolated within
        the specific response context, which runs under a unique greenlet for every
        incoming packet.
        """
        raise NotImplementedError()
