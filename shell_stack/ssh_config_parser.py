from dataclasses import dataclass
from pathlib import Path
from typing import cast

import paramiko

from shell_stack.utils import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class SshHostConfig:
    host: str
    # TODO: See if these should really be optional
    hostname: str | None = None
    user: str | None = None
    port: int | None = None
    identity_file: list[str] | None = None


EXCLUDED_ALIASES: list[str] = ["*"]


class SshConfigParser:
    @staticmethod
    def parse_ssh_config(ssh_config_path: Path) -> list[SshHostConfig]:
        """Parse SSH config and return a list of SshHostConfig objects."""

        if not ssh_config_path.exists():
            logger.error(f"Config file not found at '{ssh_config_path}'")
            return []

        logger.info(f"Opening config file at '{ssh_config_path}'")
        with ssh_config_path.open() as f:
            ssh_config = paramiko.SSHConfig()
            ssh_config.parse(f)

        configs = []
        for alias in ssh_config.get_hostnames():
            if alias in EXCLUDED_ALIASES:
                continue

            entry = ssh_config.lookup(alias)
            parsed_config = SshHostConfig(
                host=alias,
                hostname=entry.get("hostname"),
                user=entry.get("user"),
                port=int(entry["port"]) if "port" in entry else None,
                identity_file=cast(list[str] | None, entry.get("identityfile")),
            )
            logger.debug(f"Parsed config: {parsed_config}")
            configs.append(parsed_config)
        logger.info(f"Loaded {len(configs)} configs.")
        return configs
