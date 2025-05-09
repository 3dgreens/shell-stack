import subprocess
from unittest.mock import MagicMock, patch

from shell_stack.components.ping_wrapper import PingWrapper


@patch("subprocess.run")
def test_ping_success(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = (
        "64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=10.6 ms\n"
        "1 packets transmitted, 1 received, 0% packet loss, time 0ms\n"
        "rtt min/avg/max/mdev = 10.607/10.607/10.607/0.000 ms"
    )
    mock_run.return_value = mock_process

    result = PingWrapper.ping("8.8.8.8")

    mock_run.assert_called_once_with(
        args=["ping", "-c", "1", "-W", "1", "8.8.8.8"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    assert result == mock_process.stdout.splitlines()


@patch("subprocess.run")
def test_ping_failure(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stdout = "ping: unknown host example.invalid"
    mock_run.return_value = mock_process

    result = PingWrapper.ping("example.invalid")

    mock_run.assert_called_once_with(
        args=["ping", "-c", "1", "-W", "1", "example.invalid"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    assert result == []


@patch.object(PingWrapper, "ping")
def test_safe_ping_success(mock_ping):
    expected_result = ["64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=10.6 ms"]
    mock_ping.return_value = expected_result

    result = PingWrapper.safe_ping("8.8.8.8")

    mock_ping.assert_called_once_with("8.8.8.8")
    assert result == expected_result


@patch.object(PingWrapper, "ping")
def test_safe_ping_exception(mock_ping):
    mock_ping.side_effect = Exception("Test exception")

    result = PingWrapper.safe_ping("8.8.8.8")

    mock_ping.assert_called_once_with("8.8.8.8")
    assert result == []


@patch("subprocess.run")
def test_ping_timeout(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stdout = "1 packets transmitted, 0 received, 100% packet loss, time 0ms"
    mock_run.return_value = mock_process

    result = PingWrapper.ping("192.168.1.254")

    mock_run.assert_called_once()
    assert result == []


@patch("subprocess.run")
def test_ping_network_unreachable(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 2
    mock_process.stdout = "ping: connect: Network is unreachable"
    mock_run.return_value = mock_process

    result = PingWrapper.ping("10.0.0.1")

    mock_run.assert_called_once()
    assert result == []
