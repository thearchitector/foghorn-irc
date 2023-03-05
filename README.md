# foghorn-irc

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/thearchitector/foghorn-irc/ci.yaml?label=tests&style=flat-square)

A fully-compliant IRCv3 (<https://ircv3.net/>) server written referencing Modern IRC (<https://modern.ircdocs.horse/index.html>).

## What features does foghorn-irc support?

While foghorn is fully compliant with the IRCv3 specification, it does not support all of its extended features and defined capabilities. At the moment, support includes:

- Capability negotiation version <= 300, which excludes support for:
    - `cap-notify`
    - `multiline replies`
    - `capability values`

    The full table of unsupported features for versions > 300 can be viewed on the official spec (<https://ircv3.net/specs/extensions/capability-negotiation.html#cap-ls-version-features>).

- The `message-tags` capability

There is a plan to extend support for other useful capabilities (like `chat-history`, `away-notify` automatic connection upgrades via `sts` and Let's Encrypt), but that will happen sometime in the future.
