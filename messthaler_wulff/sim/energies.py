import sys
import time
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count

from networkx import Graph

from messthaler_wulff import mylog
from messthaler_wulff.sim import brute_force
from messthaler_wulff.sim.anneal import Anneal


def STRATEGY_ANNEAL(graph: Graph, upper_bound: int = None):
    anneal = Anneal(graph, len(graph) if upper_bound is None else upper_bound)
    return anneal.generate_states()


def STRATEGY_BRUTE_FORCE(*args, **kwargs):
    return brute_force.generate_states(*args, **kwargs)


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
        for state in (pbar := mylog.tqdm(strategy(graph, *strategy_args, **strategy_kwargs), "Evaluating states")):
            now = time.time()
            if improve2reset:
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


@dataclass
class RemoteComputation:
    graph: Graph
    timeout: float
    upper_bound: int

    def __call__(self, *args, **kwargs):
        mylog.log_level = mylog.WARNING
        return compute(self.graph, STRATEGY_ANNEAL, self.timeout, False, self.upper_bound)


def compute_parallel(graph: Graph,
                     timeout: float = 1,
                     *strategy_args,
                     **strategy_kwargs) -> list[int]:
    computation = RemoteComputation(graph, timeout, *strategy_args, **strategy_kwargs)
    best = [sys.maxsize] * (len(graph) + 1)

    with Pool() as p:
        for res in p.map(computation, range(cpu_count())):
            assert len(res) == len(best)
            for i in range(len(best)):
                if res[i] < best[i]:
                    best[i] = res[i]

    return best
