"""Performance metrics and monitoring for CompText MCP Server"""

import time
from typing import Dict
from functools import wraps
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collector for tracking API performance"""

    def __init__(self):
        self.request_count: Dict[str, int] = defaultdict(int)
        self.error_count: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, list] = defaultdict(list)
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.start_time: datetime = datetime.now()

    def record_request(self, endpoint: str, response_time: float, error: bool = False):
        """Record a request with its metrics"""
        self.request_count[endpoint] += 1
        self.response_times[endpoint].append(response_time)

        if error:
            self.error_count[endpoint] += 1

    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1

    def get_stats(self) -> Dict:
        """Get current statistics"""
        stats = {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_requests": sum(self.request_count.values()),
            "total_errors": sum(self.error_count.values()),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "endpoints": {},
        }

        for endpoint, count in self.request_count.items():
            times = self.response_times[endpoint]
            stats["endpoints"][endpoint] = {
                "count": count,
                "errors": self.error_count.get(endpoint, 0),
                "avg_response_time": sum(times) / len(times) if times else 0,
                "min_response_time": min(times) if times else 0,
                "max_response_time": max(times) if times else 0,
            }

        return stats

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100

    def reset(self):
        """Reset all metrics"""
        self.request_count.clear()
        self.error_count.clear()
        self.response_times.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = datetime.now()


# Global metrics collector
metrics = MetricsCollector()


def track_performance(endpoint_name: str):
    """
    Decorator to track function performance.

    Args:
        endpoint_name: Name of the endpoint/function being tracked
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            error = False

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                elapsed = time.time() - start_time
                metrics.record_request(endpoint_name, elapsed, error)

                if error:
                    logger.warning(f"{endpoint_name} failed in {elapsed:.3f}s")
                else:
                    logger.debug(f"{endpoint_name} completed in {elapsed:.3f}s")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            error = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                elapsed = time.time() - start_time
                metrics.record_request(endpoint_name, elapsed, error)

                if error:
                    logger.warning(f"{endpoint_name} failed in {elapsed:.3f}s")
                else:
                    logger.debug(f"{endpoint_name} completed in {elapsed:.3f}s")

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def get_metrics() -> Dict:
    """Get current metrics"""
    return metrics.get_stats()


def reset_metrics():
    """Reset all metrics"""
    metrics.reset()
