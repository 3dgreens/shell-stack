from unittest.mock import MagicMock, patch

import pytest

from shell_stack.components.host_probe import HostProbe
from shell_stack.components.ping_wrapper import PingWrapper


@pytest.fixture
def host_probe() -> HostProbe:
    ping_wrapper = MagicMock(spec=PingWrapper)
    return HostProbe(ping_wrapper)


@patch.object(PingWrapper, "safe_ping")
def test_ping_simple_time_format(mock_safe_ping, host_probe):
    mock_safe_ping.return_value = ["64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=10.6 ms"]

    result = host_probe.ping("8.8.8.8")

    mock_safe_ping.assert_called_once_with("8.8.8.8")
    assert result == 10.6


@patch.object(PingWrapper, "safe_ping")
def test_ping_round_trip_format(mock_safe_ping, host_probe):
    mock_safe_ping.return_value = [
        "1 packets transmitted, 1 received, 0% packet loss, time 0ms",
        "rtt min/avg/max/stddev = 15.123/20.456/25.789/5.678 ms",
    ]

    result = host_probe.ping("8.8.8.8")

    mock_safe_ping.assert_called_once_with("8.8.8.8")
    assert result == 20.456


@patch.object(PingWrapper, "safe_ping")
def test_ping_both_formats_returns_first_match(mock_safe_ping, host_probe):
    mock_safe_ping.return_value = [
        "64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=10.6 ms",
        "rtt min/avg/max/stddev = 15.123/20.456/25.789/5.678 ms",
    ]

    result = host_probe.ping("8.8.8.8")

    mock_safe_ping.assert_called_once_with("8.8.8.8")
    assert result == 10.6


@patch.object(PingWrapper, "safe_ping")
def test_ping_unknown_format(mock_safe_ping, host_probe):
    mock_safe_ping.return_value = ["Some unexpected output format"]

    result = host_probe.ping("8.8.8.8")

    mock_safe_ping.assert_called_once_with("8.8.8.8")
    assert result is None


@patch.object(PingWrapper, "safe_ping")
def test_ping_empty_result(mock_safe_ping, host_probe):
    mock_safe_ping.return_value = []

    result = host_probe.ping("8.8.8.8")

    mock_safe_ping.assert_called_once_with("8.8.8.8")
    assert result is None


def test_parse_simple_time_line(host_probe):
    line = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=10.6 ms"
    result = host_probe._parse_simple_time_line(line)
    assert result == 10.6

    line = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=116"
    result = host_probe._parse_simple_time_line(line)
    assert result is None


def test_parse_round_trip_line(host_probe):
    line = "rtt min/avg/max/stddev = 15.123/20.456/25.789/5.678 ms"
    result = host_probe._parse_round_trip_line(line)
    assert result == 20.456

    line = "Some other line"
    result = host_probe._parse_round_trip_line(line)
    assert result is None
