# foghorn-irc

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fatrox%2Fsync-dotenv%2Fbadge&style=popout-square)](https://actions-badge.atrox.dev/atrox/sync-dotenv/goto)

A fully-compliant IRCv3 (<https://ircv3.net/>) server written referencing Modern IRC (<https://modern.ircdocs.horse/index.html>).

## What features does foghorn-irc support?

While forhorn is fully compliant with the IRCv3 specification, it does not support all of its extended features and defined capabilities. At the moment, support includes:

- Capability negotation.
- `CAP LS` version <= 300, which excludes support for `cap-notify`, `multiline replies`, and `capability values`. The full table of unsupported features for versions > 300 can be viewed on the official spec (<https://ircv3.net/specs/extensions/capability-negotiation.html#cap-ls-version-features>).
- The `message-tags` capability, though there is a plan to extend support for other useful capabilities in the future (like `chat-history`, `away-notify` automatic connection upgrades via `sts` and Let's Encrypt).

## CI/CD

CI/CD is managed using Github Actions, where the CI workflow manages codebase linting and automated testing. To avoid having to commit and push workflow changes in order to test the workflows, developers are encouraged to test locally using [act](https://github.com/nektos/act#installation). Note, however, that act currently only supports Linux-based runners. While useful for initial testing, workflow moficiations must be tested on a separate branch to ensure they work correctly for all supported operating systems and Python versions.
