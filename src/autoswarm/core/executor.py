from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class ParallelExecutor:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute_parallel(
        self,
        func: Callable,
        items: List[Any],
        *args,
        **kwargs
    ) -> List[Any]:
        futures = []
        results = []

        for item in items:
            future = self.executor.submit(func, item, *args, **kwargs)
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Parallel execution error: {e}")
                results.append(None)

        return results

    def shutdown(self, wait: bool = True):
        self.executor.shutdown(wait=wait)
