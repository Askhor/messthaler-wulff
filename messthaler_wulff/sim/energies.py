import time

from messthaler_wulff import mylog


def find(states,
         timeout: float = 1,
         improve2reset: bool = True) -> list[int]:
    """
        Evaluate a series of states to find the best energy for each unique size.

        Args:
            states: An iterable of simulation states to evaluate.
            timeout (float, optional): The maximum time to evaluate states in seconds. Default is 1 second.
            improve2reset (bool, optional): If True, display the time since the last improvement and reset the timeout on
                                            any improvement. Default is True.

        Returns:
            list[int]: A list of best energies corresponding to the sizes of states evaluated.
        """
    best = {}

    timeout_start = time.time()
    last_improvement = time.time()

    try:
        for state in (pbar := mylog.tqdm(states, "Evaluating states")):
            now = time.time()
            # Update progress bar with time since last improvement if applicable
            if improve2reset:
                pbar.set_postfix_str(f"last improved {now - last_improvement:.1f} sec ago")

            # Update the best energy for the current state size if it's an improvement
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
