from pydantic import RootModel

from messthaler_wulff.parsing.common import NodeModel, list2vec, vec2list


class CrystalModel(RootModel):
    root: list[NodeModel]


def from_json(json: str) -> list:
    model = CrystalModel.model_validate_json(json)
    return list(map(list2vec, model.root))


def to_json(x: list) -> str:
    model = CrystalModel(list(map(vec2list, x)))
    return model.model_dump_json()