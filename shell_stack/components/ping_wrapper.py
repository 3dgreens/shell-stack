import subprocess

from shell_stack.utils import get_logger

logger = get_logger(__name__)


class PingWrapper:
    @classmethod
    def safe_ping(cls, host: str) -> list[str]:
        try:
            return cls.ping(host)
        except Exception:
            logger.exception(f"Error pinging host {host}.")
            return []

    @staticmethod
    def ping(host: str) -> list[str]:
        result = subprocess.run(
            args=["ping", "-c", "1", "-W", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.splitlines()
        else:
            logger.error(f"Ping command failed with return code {result.returncode}.")
            return []
