import logging

import numpy as np

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation

log = logging.getLogger("messthaler_wulff")


def run_mode():
    omni_simulation = OmniSimulation(SimpleNeighborhood(np.identity(2)), None, (0, 0, 0))
    explorative_simulation = ExplorativeSimulation(omni_simulation)

    log.debug("Now exploring")

    for state in explorative_simulation.n_crystals(2):
        state.visualise_slice()

    log.debug("Finished exploring")
