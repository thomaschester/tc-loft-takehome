from src.config import OutputMode
from src.light_control import LightController

from unittest.mock import patch, mock_open, MagicMock


def test_send_cmd_stdout(capsys) -> None:
    controller: LightController = LightController(
        satellites={"20344": "#3FA2C8", "22049": "#E74B1A"},
        output_mode=OutputMode.STDOUT,
        tcp_ip=None,
        tcp_port=None,
    )
    controller.send_cmd({"20344"})

    captured = capsys.readouterr()
    assert captured.out == '{"20344": "#3FA2C8"}\n'
    assert captured.err == ""


@patch("builtins.open")
def test_send_cmd_file(mock_file) -> None:
    mock_file.side_effect = mock_open()
    controller: LightController = LightController(
        satellites={"20344": "#3FA2C8", "22049": "#E74B1A"},
        output_mode=OutputMode.FILE,
        tcp_ip=None,
        tcp_port=None,
    )
    controller.send_cmd({"20344"})

    mock_file.assert_called_once_with("light_command.txt", "w", encoding="utf-8")
    mock_file().write.assert_called_once_with('{"20344": "#3FA2C8"}')


@patch("src.light_control.zmq.Context")
def test_send_cmd_tcp(mock_zmq_context) -> None:
    mock_socket: MagicMock = MagicMock()
    mock_zmq_context.return_value.socket.return_value = mock_socket

    controller: LightController = LightController(
        satellites={"20344": "#3FA2C8", "22049": "#E74B1A"},
        output_mode=OutputMode.TCP,
        tcp_ip="127.0.0.1",
        tcp_port="5005",
    )
    controller.send_cmd({"20344"})

    mock_socket.send_string.assert_called_once_with('{"20344": "#3FA2C8"}')


@patch("src.light_control.zmq.Context")
def test_send_cmd_tcp_bad_matching_ids_set(mock_zmq_context) -> None:
    mock_socket: MagicMock = MagicMock()
    mock_zmq_context.return_value.socket.return_value = mock_socket
    controller: LightController = LightController(
        satellites={"20344": "#3FA2C8", "22049": "#E74B1A"},
        output_mode=OutputMode.TCP,
        tcp_ip="127.0.0.1",
        tcp_port="5005",
    )
    controller.send_cmd({"1111"})
    mock_socket.send_string.assert_called_once_with("{}")
