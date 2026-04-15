import sys
import time

import tqdm
from networkx import Graph

from messthaler_wulff.bravais import CommonBravais
from messthaler_wulff.sim import brute_force
from messthaler_wulff.sim.anneal import Anneal

STRATEGY_ANNEAL = lambda graph, upper_bound=None: Anneal(graph,
                                                         len(graph) if upper_bound is None else upper_bound).generate_states()

STRATEGY_BRUTE_FORCE = brute_force.generate_states


def compute(graph: Graph,
            strategy,
            timeout: float = 1,
            improve2reset: bool = True,
            *strategy_args,
            **strategy_kwargs) -> list[int]:
    best = [sys.maxsize] * (len(graph) + 1)

    timeout_start = time.time()
    last_improvement = time.time()

    try:
        for state in (pbar := tqdm.tqdm(strategy(graph, *strategy_args, **strategy_kwargs), "Evaluating states")):
            now = time.time()
            pbar.set_postfix_str(f"last improved {now - last_improvement:.1f} sec ago")

            if state.energy < best[state.size]:
                best[state.size] = state.energy
                last_improvement = now
                if improve2reset:
                    timeout_start = now

            if timeout is not None and now - timeout_start > timeout:
                break
    except KeyboardInterrupt:
        print("Optimisation was interrupted")

    return best


def main():
    graph = CommonBravais.fcc.value.graph(2)
    print(compute(graph, STRATEGY_ANNEAL)[:3])
    print(compute(graph, STRATEGY_BRUTE_FORCE)[:3])


if __name__ == "__main__":
    main()
