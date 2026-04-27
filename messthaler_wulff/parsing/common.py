from typing import Union

from messthaler_wulff.math.vector import vec

VectorModel = list[int]
NodeModel = Union[str, int, VectorModel]

def list2vec(x) -> vec:
    if isinstance(x, list) and all(isinstance(i, int) for i in x):
        return vec(x)
    else:
        return x

def vec2list(x):
    if isinstance(x, vec):
        return list(x)
    else:
        return x
