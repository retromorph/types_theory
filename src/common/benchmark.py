import time
import tracemalloc
import cProfile
import pstats
import io
import sys


def benchmark(
    func,
    *args,
    measure_time=False,
    measure_tracemalloc=False,
    measure_profile=False,
    measure_allocs=False,
    n_iter=1,
    **kwargs
):
    result = None
    stats = {}

    # --- Allocations before ---
    if measure_allocs:
        allocs_before = sys.getallocatedblocks()
    else:
        allocs_before = None

    # --- tracemalloc ---
    if measure_tracemalloc:
        tracemalloc.start()

    # --- profiler ---
    if measure_profile:
        profiler = cProfile.Profile()
        profiler.enable()
    else:
        profiler = None

    # --- time ---
    if measure_time:
        start_time = time.perf_counter()
    else:
        start_time = None

    # --- Execute function ---
    for _ in range(n_iter):
        result = func(*args, **kwargs)

    # --- time end ---
    if measure_time:
        stats["time_sec"] = (time.perf_counter() - start_time) / n_iter

    # --- profiler end ---
    if measure_profile:
        profiler.disable()
        s = io.StringIO()
        pstats.Stats(profiler, stream=s).sort_stats("tottime").print_stats(40)
        stats["profile"] = s.getvalue()

    # --- tracemalloc end ---
    if measure_tracemalloc:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        stats["tracemalloc_current_bytes"] = current
        stats["tracemalloc_peak_bytes"] = peak

    # --- allocations end ---
    if measure_allocs:
        allocs_after = sys.getallocatedblocks()
        stats["allocs_delta"] = allocs_after - allocs_before

    stats["result"] = result
    return stats
