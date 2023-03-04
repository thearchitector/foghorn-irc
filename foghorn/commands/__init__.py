from ..enums import Command
from ..typing import typecaster
from .cap import CapCommand

# from .passwd import PassCommand
from .nick import NickCommand

COMMANDS = {
    Command.CAP: CapCommand(
        save_context=True,
        required_post_context=lambda p: p
        in (
            Command.CAP,
            # Command.PASS,
            Command.NICK,
        ),
    ),
    # Command.PASS: PassCommand(
    #     required_params=[str],
    #     save_context=True,
    #     required_pre_context=Command.CAP,
    #     required_post_context=Command.NICK,
    # ),
    Command.NICK: NickCommand(
        required_params=[typecaster(str, optional=True)],
        save_context=True,
        required_post_context=Command.USER,
    ),
    # Command.USER: UserCommand(required_pre_context=Command.NICK),
}

__all__ = ["COMMANDS"]
