import logging
import subprocess
from typing import Optional

from textual.logging import TextualHandler


def get_logger(name: Optional[str] = None, log_level: int = logging.DEBUG) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            # TODO: Maybe consider other handlers and make sure
            #       we can log to file
            TextualHandler()
        ],
    )
    return logging.getLogger(name)


logger = get_logger(__name__)


def ping_host(host: str) -> Optional[float]:
    """Ping a host to check if it is reachable and capture the latency."""

    def _parse_simple_time_line(line: str) -> Optional[float]:
        if "time=" in line:
            latency = line.split("time=")[1].split(" ")[0]
            return float(latency)
        return None

    def _parse_round_trip_line(line: str) -> Optional[float]:
        if "min/avg/max/stddev" in line:
            stats_part = line.split("=")[1].strip()
            avg_time = stats_part.split("/")[1]
            return float(avg_time)
        return None

    try:
        result = subprocess.run(
            args=["ping", "-c", "1", "-W", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                latency = _parse_simple_time_line(line)
                if latency is not None:
                    return latency
                latency = _parse_round_trip_line(line)
                if latency is not None:
                    return latency
                logger.warning(f"Unknown ping output line: {line}")
        else:
            logger.error(f"Ping command failed with return code {result.returncode}.")
            return None
    except Exception:
        logger.exception(f"Error pinging host {host}.")
        return None
