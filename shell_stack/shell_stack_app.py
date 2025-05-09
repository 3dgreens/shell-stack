from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from shell_stack.components.host_probe import HostProbe
from shell_stack.hosts_table import HostsTable

# TODO: Stream handler will log to the gui - what is a legit log location?
from shell_stack.utils import get_logger

logger = get_logger(__name__)


class ShellStackApp(App):
    DEFAULT_SSH_CONFIG_PATH = Path.home() / ".ssh" / "config"
    DEFAULT_REFRESH_INTERVAL = 5
    CSS_PATH = "assets/shell_stack.tcss"
    BINDINGS: ClassVar = [
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self, host_probe: HostProbe, ssh_config_path: Path | None = None, refresh_interval: int | None = None
    ) -> None:
        super().__init__()
        self._ssh_config_path = ssh_config_path or self.DEFAULT_SSH_CONFIG_PATH
        self._refresh_interval = refresh_interval or self.DEFAULT_REFRESH_INTERVAL
        self._host_probe = host_probe

    def compose(self) -> ComposeResult:
        yield Header()
        yield HostsTable(self, self._ssh_config_path, self._refresh_interval, self._host_probe)
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        pass
