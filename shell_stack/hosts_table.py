import shutil
import subprocess
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.timer import Timer
from textual.widgets import DataTable, Static

from shell_stack.components.host_probe import HostProbe
from shell_stack.ssh_config_parser import SshConfigParser
from shell_stack.utils import get_logger

logger = get_logger(__name__)


class HostsTable(Static, can_focus=True):
    BINDINGS: ClassVar = [
        ("s", "ssh()", "SSH"),
        ("c", "edit_config()", "Edit Config"),
    ]

    def __init__(self, app: App, ssh_config_path: Path, refresh_interval: int, host_probe: HostProbe) -> None:
        super().__init__()
        self._hosts_table: DataTable = DataTable(id="hosts-table", cursor_type="row")
        self._timer: Timer | None = None
        self._app = app
        self._ssh_config_path = ssh_config_path
        self._refresh_interval = refresh_interval
        self._host_probe = host_probe

    def compose(self) -> ComposeResult:
        yield Static(f"Hosts ({self._ssh_config_path})", id="hosts-title-bar")
        yield self._hosts_table

    def on_mount(self) -> None:
        self._hosts_table.add_columns("Host", "Hostname", "User", "Port", "Identity File", "Ping Status")
        self._timer = self.set_interval(self._refresh_interval, self._update)
        self._update()

    def action_ssh(self) -> None:
        selected_row_index = self._hosts_table.cursor_row
        selected_row = self._hosts_table.get_row_at(selected_row_index)
        host = selected_row[0]
        ssh_path = shutil.which("ssh")
        if not ssh_path:
            raise RuntimeError("ssh not found")  # noqa: TRY003

        with self._app.suspend():
            # TODO: Sanitize the host here
            subprocess.run([ssh_path, host])  # noqa: S603

    def action_edit_config(self) -> None:
        vim_path = shutil.which("vim")
        if not vim_path:
            raise RuntimeError("vim not found")  # noqa: TRY003

        with self._app.suspend():
            # TODO: Add more options than just vim
            # TODO: Sanitize the ssh config path here
            subprocess.run([vim_path, self._ssh_config_path])  # noqa: S603

    # TODO: Clean this up
    def _update(self) -> None:
        logger.info("Updating Hosts Table")
        hosts = SshConfigParser.parse_ssh_config(self._ssh_config_path)

        if hosts:
            # persist the selected row
            selected_cell_coordinate = self._hosts_table.cursor_coordinate
            if self._hosts_table.is_valid_coordinate(selected_cell_coordinate):
                selected_row_key, _ = self._hosts_table.coordinate_to_cell_key(selected_cell_coordinate)
            else:
                selected_row_key = None

            logger.info(f"Selected row key: {selected_row_key}")

            # remove all rows
            for row_key in list(self._hosts_table.rows.keys()):
                self._hosts_table.remove_row(row_key)

            for host_config in hosts:
                hostname = host_config.hostname
                # TODO: If I make the dataclass more strict then I can remove the None check
                ping_status = self._host_probe.ping(hostname) if hostname else None
                self._hosts_table.add_row(
                    host_config.host,
                    hostname or "N/A",
                    host_config.user or "N/A",
                    str(host_config.port) if host_config.port else "N/A",
                    # TODO: Check if the identity files exist
                    ", ".join(host_config.identity_file) if host_config.identity_file else "N/A",
                    f"Reachable ({ping_status} ms)" if ping_status else "Unreachable",
                    key=host_config.host,
                )

            # restore the selected row
            if selected_row_key:
                selected_row_index = self._hosts_table.get_row_index(selected_row_key)
                logger.info(f"Selected row index: {selected_row_index}")
                self._hosts_table.move_cursor(row=selected_row_index)
        else:
            self._hosts_table.clear()
            self._hosts_table.add_row("No hosts found", "", "", "", "", "")

        logger.info("Hosts Table updated")
