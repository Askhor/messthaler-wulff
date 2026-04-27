import logging
import re

from messthaler_wulff.math.bravais import CommonBravais

log = logging.getLogger("messthaler_wulff")

int_re = re.compile(r"[+-]?\d+(?:\.0)?")
atom_re = re.compile(fr"\((\s*{int_re.pattern}\s*(?:,\s*{int_re.pattern}\s*)*),?\s*\)")
crystal_re = re.compile(r"\s*\[\s*"
                        r"(?:"
                        rf"{atom_re.pattern}"
                        rf"(?:\s*,\s*{atom_re.pattern}\s*)*"
                        r")?"
                        r"\s*]\s*")

allowed_characters = frozenset("0123456789.,()[]+- ")


def parse_atom(string: str) -> tuple:
    ints = map(lambda x: x.split(".")[0], int_re.findall(string))
    return tuple(map(int, ints))


def parse_crystal(string: str) -> list[tuple]:

    if not crystal_re.fullmatch(string):
        log.error(f"String does not match crystal format: {string}")
        characters = frozenset(string)
        if not characters < allowed_characters:
            log.error(f"You used the following illegal characters: {characters - allowed_characters}")
        string = string.strip()
        if string[0] != "[" or string[-1] != "]":
            log.error(f"String does not begin or end with '[' and ']'")
        exit(0)

    return list(map(parse_atom, atom_re.findall(string)))

def parse_graph(string: str) -> tuple:
    string = string.strip().lower()

    for bravais in CommonBravais:
        if bravais.lower() == string:
            return 
