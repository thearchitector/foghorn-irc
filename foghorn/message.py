from dataclasses import dataclass
from typing import Optional, Dict, List, Match
import re

from .standards import (
    ATOM_DELIMITER,
    TAG_PREFIX,
    TAG_ESCAPE_MAPPING,
    TAG_ESCAPE_MAPPING_2,
    SOURCE_PREFIX,
    TRAILING_PARAM_PREFIX,
    TAG_UNESCAPE_MAPPING,
)


@dataclass(frozen=True)
class Message:
    params: List[str]
    verb: str
    source: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    @staticmethod
    def _tags_from_line(line: str):
        """
        Parses the tag section of a UTF-8 encoded ABNF string line to a
        appropriately mapped dictionary. Tags that are empty are parsed as
        missing.
        https://ircv3.net/specs/extensions/message-tags.html
        """

        def unescape(matchobj: Match) -> str:
            """
            Unescapes non-parsing special character encodings from the entire line
            at once to reduce the number of regex calls.
            """
            match = matchobj.group(0)
            return TAG_ESCAPE_MAPPING.get(
                match, re.sub(r"\\([^:])", lambda m: m.group(1), matchobj.group(0))
            )

        line = re.sub(r"\\.?", unescape, line)
        # extract all tag assignments and as a list of tuples of matching groups,
        # and combine them together into a dictionary. as per spec, the last value
        # of a tag is acknowledged
        tags = dict(re.findall(r"([^=;]+)=?([^;]*)(?:;|$)", line))

        def unescape2(matchobj: Match) -> str:
            r"""
            Unescapes the special parsing character encodings (trailing '\' and '\:')
            from each raw value. This must be done lastly on each tag as the raw
            values for both characters have special meanings for initial decoding.
            """
            return TAG_ESCAPE_MAPPING_2[matchobj.group(0)]

        return {t: re.sub(r"\\:|\\$", unescape2, tags[t]) for t in tags}

    @classmethod
    def from_line(cls, line: str):
        # atoms = re.split(r" {1}", line)
        atoms = line.split(ATOM_DELIMITER)

        # tags are optional. if the first atom begins with '@', extract them
        tags = None
        if atoms[0].startswith(TAG_PREFIX):
            tags, atoms = cls._tags_from_line(atoms[0][1:]), atoms[1:]

        # source is optional. if the first (or second, depending on the inclusion
        # of tags) begins with ':', extract it
        source = None
        if atoms[0].startswith(SOURCE_PREFIX):
            source, atoms = atoms[0][1:], atoms[1:]

        # the verb and params must the remaining atoms. the last parameter may contain
        # spaces, so be sure to concatenate its atoms if indicated (prefixed by a ':').
        verb, params = atoms[0], []
        for i, p in enumerate(atoms[1:]):
            if p.startswith(TRAILING_PARAM_PREFIX):
                params.append(ATOM_DELIMITER.join(atoms[1:][i:])[1:])
                break
            elif p.strip():
                params.append(p)

        return Message(tags=tags, source=source, verb=verb, params=params)

    def _tags_to_line(self):
        """
        Encodes this message's tags into a UTF-8 encoded ABNF string, escaping
        all characters with special meanings. Tags that were parsed as empty
        during ingestion are normalized to missing values.
        https://ircv3.net/specs/extensions/message-tags.html
        """

        def escape(matchgroup: Match) -> str:
            """
            Escapes all characters by the reverse of the special character
            mapping used during parsing. By the nature of the initial decoding,
            this process is lossless in terms of meaning, but may not yield the
            exact original line (for example, invalid backslashes are not added).
            """
            match = matchgroup.group(0)
            return TAG_UNESCAPE_MAPPING.get(match, match)

        pattern = r"(?:.|\n|\r){1}"
        assignments = [
            k + (f"={re.sub(pattern, escape, self.tags[k])}" if self.tags[k] else "")
            for k in self.tags
        ]

        return f"@{';'.join(assignments)}"

    def to_line(self) -> str:
        atoms = []

        # start with tags if present
        if self.tags:
            atoms.append(self._tags_to_line())

        # append source with correct prefix if present
        if self.source:
            atoms.append(f"{SOURCE_PREFIX}{self.source}")

        atoms.append(self.verb)

        # if params are present, append them while ensuring to append the
        # trailing parameter character when necessary for proper encoding
        if self.params:
            atoms.extend(self.params[:-1])
            atoms.append(
                (
                    TRAILING_PARAM_PREFIX
                    if not self.params[-1]
                    or self.params[-1][0] == TRAILING_PARAM_PREFIX
                    or " " in self.params[-1]
                    else ""
                )
                + self.params[-1]
            )

        return ATOM_DELIMITER.join(atoms)
