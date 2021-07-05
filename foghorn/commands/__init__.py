from ..enums import Command
from .cap import CapCommand

COMMANDS = {
    Command.CAP: CapCommand(
        save_context=True,
        required_post_context=lambda p: p in (Command.CAP, Command.PASS, Command.NICK),
    )
}

__all__ = ["COMMANDS"]
