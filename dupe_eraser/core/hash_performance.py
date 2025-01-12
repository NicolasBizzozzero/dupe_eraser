from typing import List


class HashPerformance:
    def __init__(self, name: str):
        """Initialize hash performance tracker.

        Args:
            name: Name of the hash algorithm
        """
        self.name = name
        self.times: List[float] = []
        self.sizes: List[int] = []

    @property
    def avg_speed_mbps(self) -> float:
        """Calculate average speed in MB/s."""
        if not self.times:
            return 0.0
        total_mb = sum(self.sizes) / (1024 * 1024)
        total_time = sum(self.times)
        return total_mb / total_time if total_time > 0 else 0.0

    @property
    def avg_time_ms(self) -> float:
        """Calculate average time in milliseconds."""
        return (sum(self.times) / len(self.times) * 1000) if self.times else 0.0
