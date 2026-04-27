from messthaler_wulff.math.bravais import CommonBravais
from messthaler_wulff.sim import energies as nrg
from messthaler_wulff.sim.anneal import Anneal

TEST_ENERGIES_FORWARDS: list[int] = [0, 12, 22, 30, 36, 44, 50, 54, 60, 66, 70, 76, 80, 84, 88, 92, 96, 100, 104, 108,
                                     112, 116, 120, 124, 126, 130, 134, 138, 142, 144, 148, 150, 154, 158, 160, 164,
                                     166, 168, 168, 172, 176, 180, 184, 188, 192, 194, 198, 198, 202, 206, 210, 212,
                                     216, 218, 222, 224, 224, 228, 230, 234, 238, 242, 244, 246, 246, 250, 250, 252,
                                     256, 260, 264, 268, 268, 270, 270, 274, 276, 280, 282, 286, 286, 288, 288, 292,
                                     296, 300, 302, 306, 306, 308, 308, 312]

TEST_ENERGIES_BIDI: list[int] = [0, 12, 22, 30, 36, 44, 48, 54, 60, 66, 70, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112,
                                 116, 120,
                                 124, 126, 130, 134, 138, 142, 144, 148, 150, 154, 158, 160, 164, 166, 168, 168, 172,
                                 176, ]

TEST_ENERGIES_BEST = list(TEST_ENERGIES_FORWARDS)

for i in range(len(TEST_ENERGIES_BIDI)):
    if TEST_ENERGIES_BIDI[i] < TEST_ENERGIES_BEST[i]:
        TEST_ENERGIES_BEST[i] = TEST_ENERGIES_BIDI[i]


def test_energies():
    upper_bound = len(TEST_ENERGIES_BEST)

    graph = CommonBravais.fcc.value.graph(7)
    anneal = Anneal(graph, upper_bound)

    found = nrg.find(anneal.generate_states())

    for i in range(len(TEST_ENERGIES_BEST)):
        assert i in found
        if i <= 10:
            assert found[i] ==  TEST_ENERGIES_BEST[i]
        else:
            assert TEST_ENERGIES_BEST[i] - 10 <= found[i] <= TEST_ENERGIES_BEST[i]
