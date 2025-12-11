import numpy as np

from .utils import *


def pos(*c):
    return np.array(c)


@constant
def fcc_wulff_data():
    return np.transpose(np.array([(1, -1, 2),
                                  (2, -2, 2),
                                  (0, -2, 2),
                                  (1, -3, 2),
                                  (1, 0, 1),
                                  (2, 0, 0),
                                  (0, 0, 0),
                                  (1, 0, -1),
                                  (1, -4, 1),
                                  (2, -4, 0),
                                  (0, -4, 0),
                                  (1, -4, -1),
                                  (1, -1, -2),
                                  (2, -2, -2),
                                  (0, -2, -2),
                                  (1, -3, -2),
                                  (-1, -2, 1),
                                  (-1, -1, 0),
                                  (-1, -3, 0),
                                  (-1, -2, -1),
                                  (3, -2, 1),
                                  (3, -1, 0),
                                  (3, -3, 0),
                                  (3, -2, -1)]))


@constant
def fcc_wulff2_data():
    return np.transpose(np.array([(2, 0, 4),
                                  (-2, 0, 4),
                                  (0, 2, 4),
                                  (0, -2, 4),
                                  (2, 0, -4),
                                  (-2, 0, -4),
                                  (0, 2, -4),
                                  (0, -2, -4),
                                  (2, 4, 0),
                                  (-2, 4, 0),
                                  (0, 4, 2),
                                  (0, 4, -2),
                                  (2, -4, 0),
                                  (-2, -4, 0),
                                  (0, -4, 2),
                                  (0, -4, -2),
                                  (4, 2, 0),
                                  (4, 0, 2),
                                  (4, -2, 0),
                                  (4, 0, -2),
                                  (-4, 2, 0),
                                  (-4, -2, 0),
                                  (-4, 0, -2),
                                  (-4, 0, 2)]))


@constant
def fcc_transform():
    is2 = 1 / math.sqrt(2)

    b1 = is2 * pos(1, 1, 0)
    b2 = is2 * pos(1, 0, 1)
    b3 = is2 * pos(0, 1, 1)

    return np.array([b1, b2, b3])


@constant
def fcc_wulff_lattice_coords():
    undo_encoding = np.linalg.inv(np.multiply(math.sqrt(2), fcc_transform()))
    flipper = np.array(
        [[1, 0, 0],
         [0, -1, 0],
         [0, 0, 1]])

    return [np.dot(undo_encoding, np.dot(flipper, p)) for p in np.transpose(fcc_wulff_data())]


@constant
def fcc_wulff_obj():
    flipper = np.array(
        [[1, 0, 0],
         [0, -1, 0],
         [0, 0, 1]])

    return (ObjectCollection.from_points(*fcc_wulff_data())
            * flipper
            # + pos(-1, -2, 0))
            * ((1 / math.sqrt(2)) * np.identity(3)))


@constant
def fcc_wulff2_obj():
    return (ObjectCollection.from_points(*fcc_wulff2_data())
            * ((1 / math.sqrt(2)) * np.identity(3)))


@constant
def hcp_transform():
    e1 = pos(1, 0, 0)
    e2 = 0.5 * pos(1, math.sqrt(3), 0)
    e3 = 2 / 3 * math.sqrt(6) * pos(0, 0, 1)

    return np.transpose(np.array([e1, e2, e3]))


@constant
def hcp_vector():
    return np.dot(hcp_transform(), pos(1 / 3, 1 / 3, 1 / 2))
