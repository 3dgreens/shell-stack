from shell_stack.components.ping_wrapper import PingWrapper
from shell_stack.utils import get_logger

logger = get_logger(__name__)


class HostProbe:
    def __init__(self, ping_wrapper: PingWrapper) -> None:
        self.ping_wrapper = ping_wrapper

    def ping(self, host: str) -> float | None:
        ping_result_lines = PingWrapper.safe_ping(host)
        for line in ping_result_lines:
            latency = self._parse_simple_time_line(line)
            if latency is not None:
                return latency

            latency = self._parse_round_trip_line(line)
            if latency is not None:
                return latency

        logger.error(f"Unknown ping output lines: {ping_result_lines}")
        return None

    def _parse_simple_time_line(self, line: str) -> float | None:
        if "time=" in line:
            latency = line.split("time=")[1].split(" ")[0]
            return float(latency)
        return None

    def _parse_round_trip_line(self, line: str) -> float | None:
        # TODO: Sanitize this
        if "min/avg/max/stddev" in line:
            stats_part = line.split("=")[1].strip()
            avg_time = stats_part.split("/")[1]
            return float(avg_time)
        return None
