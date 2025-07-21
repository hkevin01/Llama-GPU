"""
Benchmarking and Regression Testing Utility
Provides functions to benchmark model performance and log results.
"""

import time
import logging
logging.basicConfig(filename='logs/benchmark_utils.log', level=logging.INFO)

def benchmark_model(model, input_data, runs=10):
    times = []
    for _ in range(runs):
        start = time.time()
        model(input_data)
        end = time.time()
        times.append(end - start)
    avg_time = sum(times) / len(times)
    logging.info('Benchmark: %d runs, avg %.4fs', runs, avg_time)
    return avg_time, times
