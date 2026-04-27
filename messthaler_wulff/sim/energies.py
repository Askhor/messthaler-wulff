import time

from messthaler_wulff import mylog


def find(states,
         timeout: float = 1,
         improve2reset: bool = True) -> list[int]:
    best = {}

    timeout_start = time.time()
    last_improvement = time.time()

    try:
        for state in (pbar := mylog.tqdm(states, "Evaluating states")):
            now = time.time()
            if improve2reset:
                pbar.set_postfix_str(f"last improved {now - last_improvement:.1f} sec ago")

            if state.size not in best or state.energy < best[state.size]:
                best[state.size] = state.energy
                last_improvement = now
                if improve2reset:
                    timeout_start = now

            if timeout is not None and now - timeout_start > timeout:
                break
    except KeyboardInterrupt:
        print("Optimisation was interrupted")

    return best
