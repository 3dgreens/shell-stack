from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from shell_stack.hosts_table import HostsTable

# TODO: Stream handler will log to the gui - what is a legit log location?
from shell_stack.utils import get_logger

logger = get_logger(__name__)


class SSHConfigWatcher(App):
    CSS_PATH = "assets/shell_stack.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._ssh_config_path = Path.home() / ".ssh" / "config"

    def compose(self) -> ComposeResult:
        yield Header()
        yield HostsTable(self, self._ssh_config_path)
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        pass


if __name__ == "__main__":
    SSHConfigWatcher().run(inline=False)
