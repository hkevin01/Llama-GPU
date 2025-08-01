"""
batching.py - Request queuing and dynamic batching utilities for LLaMA GPU API server.
"""

import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class BatchWorker(threading.Thread):
    def __init__(self, 
                 request_queue: queue.Queue, 
                 batch_process_fn: Callable[[List[Any]], List[Any]],
                 batch_size: int = 8, 
                 batch_timeout: float = 0.1,
                 name: Optional[str] = None):
        super().__init__(daemon=True, name=name)
        self.request_queue = request_queue
        self.batch_process_fn = batch_process_fn
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.running = True

    def run(self):
        while self.running:
            batch = []
            start_time = time.time()
            while len(batch) < self.batch_size:
                try:
                    item = self.request_queue.get(timeout=self.batch_timeout)
                    batch.append(item)
                except queue.Empty:
                    break
                if time.time() - start_time > self.batch_timeout:
                    break
            if batch:
                self.batch_process_fn(batch)

    def stop(self):
        self.running = False


def start_batch_workers(
    num_workers: int,
    request_queue: queue.Queue,
    batch_process_fn: Callable[[List[Any]], List[Any]],
    batch_size: int = 8,
    batch_timeout: float = 0.1,
    name_prefix: str = "BatchWorker"
) -> List[BatchWorker]:
    workers = []
    for i in range(num_workers):
        worker = BatchWorker(
            request_queue=request_queue,
            batch_process_fn=batch_process_fn,
            batch_size=batch_size,
            batch_timeout=batch_timeout,
            name=f"{name_prefix}-{i+1}"
        )
        worker.start()
        workers.append(worker)
    return workers 