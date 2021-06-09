"""
Expected bytes and strings as defined in the protocol specification.

https://modern.ircdocs.horse/index.html#messages
"""
MSG_DELIMITER = b"\r\n"
MAX_MESSAGE_LENGTH = 512  # in bytes
ATOM_DELIMITER = " "

MAX_TAGS_LENGTH = 4096  # in bytes
TAG_PREFIX = "@"
TAG_ESCAPE_MAPPING = {r"\s": " ", r"\\": "\\", r"\r": "\r", r"\n": "\n"}
TAG_ESCAPE_MAPPING_2 = {r"\:": ";", "\\": ""}
TAG_UNESCAPE_MAPPING = {
    v: k for k, v in dict(TAG_ESCAPE_MAPPING, **TAG_ESCAPE_MAPPING_2).items() if v
}

SOURCE_PREFIX = ":"
TRAILING_PARAM_PREFIX = ":"

WILDCARD_ESCAPE_MAPPING = {r"\*": r"[^\\]*", r"\?": r"[^\\]{1}"}
