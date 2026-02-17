import logging
import re

log = logging.getLogger("messthaler_wulff")

int_re = re.compile(r"[+-]?\d+")
atom_re = re.compile(fr"\((\s*{int_re.pattern}\s*(?:,\s*{int_re.pattern}\s*)*),?\s*\)")
crystal_re = re.compile(r"\s*\[\s*"
                        r"(?:"
                        rf"{atom_re.pattern}"
                        rf"(?:\s*,\s*{atom_re.pattern}\s*)*"
                        r")?"
                        r"\s*]\s*")

def parse_atom(string: str) -> tuple:
    return tuple(map(int, int_re.findall(string)))


def parse_crystal(string: str) -> list[tuple]:
    if not crystal_re.fullmatch(string):
        log.error(f"String does not match crystal format: {string}")
        exit(0)

    return list(map(parse_atom, atom_re.findall(string)))
