from ..enums import Command
from ..utils import typecaster
from .cap import CapCommand

COMMANDS = {
    Command.CAP: CapCommand(
        required_params={"subcommand": str, "version": typecaster(int)},
        needs_redis=False,
        save_context=True,
        required_post_context=lambda p: p in (Command.PASS, Command.NICK),
    )
}

__all__ = ["COMMANDS"]
