from typing import Optional

from typer import Typer

app = Typer()


@app.command()
def start(
    hostname: Optional[str] = None,
    config: Optional[str] = ".foghornirc",
):
    """
    Launches a Foghorn IRCv3 server running with the explicitly provided configuration,
    or by loading the configuration file if one is provided.

    All servers run on TCP using port 6697 as per the specification. All connections
    are encrypted with automatically generated TLS certificates from Let's Encrypt.
    """
    from foghorn.server import IRCServer

    server = IRCServer("127.0.0.1", 1000)
    server.serve_forever()


if __name__ == "__main__":
    app()
