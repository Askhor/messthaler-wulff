from pathlib import Path

from messthaler_wulff import fcc_transform
from messthaler_wulff._additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation
from messthaler_wulff.mode_explore import run_mode

TEST_ENERGIES: list[int] = [0, 12, 22, 30, 36, 44, 50, 54, 60, 66, 70, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112,
                            116, 120, 124, 126, 130, 134, 138, 142, 144, 148, 150, 154, 158, 160, 164, 166, 168,
                            168, 172, 176, 180, 184, 188, 192, 194, 198, 198, 202, 206, 210, 212, 216, 218, 222,
                            224, 224, 228, 230, 234, 238, 242, 244, 246, 246, 250, 250, 252, 256, 260, 264, 268,
                            268, 270, 270, 274, 276, 280, 282, 286, 286, 288, 288, 292, 296, 300, 302, 306, 306,
                            308, 308, 312]


def test_forwards_mode_results(capsys):
    omni_simulation = OmniSimulation(SimpleNeighborhood(fcc_transform()), None, tuple([0] * 4))
    with capsys.disabled():
        explorer = ExplorativeSimulation(omni_simulation, 20, verbosity=0,
                                         require_energy=4, ti=True, bidi=False, collect_crystals=False)

    for i, (expected, value) in enumerate(zip(TEST_ENERGIES, explorer.energies)):
        assert value == expected


def test_mode():
    run_mode(20, fcc_transform(), 3, None, False, (), 4)


def test_mode_dump():
    run_mode(20, fcc_transform(), 3, "-", False, (), 4)

def test_mode_dump_folder(tmp_path: Path):
    run_mode(20, fcc_transform(), 3, tmp_path, False, (), 4)