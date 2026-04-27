from argparse import ArgumentParser
from pathlib import Path

from pydantic import RootModel

from messthaler_wulff.parsing.common import NodeModel, list2vec, vec2list


class CrystalModel(RootModel):
    root: list[NodeModel]


def from_json(json: str) -> list:
    model = CrystalModel.model_validate_json(json)

    values = list(map(list2vec, model.root))
    assert len(values) == len(set(values))  # TODO
    return values


def to_json(x: list) -> str:
    model = CrystalModel(list(map(vec2list, x)))
    return model.model_dump_json()


def add_arguments(parser: ArgumentParser):
    parser.add_argument("crystal", type=Path)


def from_args(args):
    path = args.crystal

    if path == Path("-"):
        string = input("Enter crystal json here: ")
    else:
        assert path.exists()  # TODO
        string = path.read_text()

    return from_json(string)