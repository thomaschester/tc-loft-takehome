from .config import logger, OutputMode
import json
from typing import Dict, Set
import zmq


class LightController:
    def __init__(
        self,
        satellites: Dict[str, str],
        output_mode: OutputMode,
        tcp_ip: str | None,
        tcp_port: str | None,
    ) -> None:
        self._output_mode: OutputMode = OutputMode(output_mode)
        self._satellites: Dict[str, str] = satellites

        if self._output_mode == OutputMode.TCP:
            self._context: zmq.Context = zmq.Context()
            self._socket_address: str = f"tcp://{tcp_ip}:{tcp_port}"
            self._socket = self._context.socket(zmq.PUSH)
            self._socket.connect(self._socket_address)

    def send_cmd(self, matching_ids: Set[str]) -> None:
        cmd_dict = {}
        for sat_id in matching_ids:
            if self._satellites.get(sat_id):
                cmd_dict[sat_id] = self._satellites[sat_id]
        cmd_str: str = json.dumps(cmd_dict)

        match self._output_mode:
            case OutputMode.STDOUT:
                self._send_cmd_stdout(cmd_str)
            case OutputMode.FILE:
                self._send_cmd_file(cmd_str)
            case OutputMode.TCP:
                self._send_cmd_tcp(cmd_str)

    def _send_cmd_stdout(self, cmd: str) -> None:
        print(cmd)

    def _send_cmd_file(self, cmd: str) -> None:
        with open("light_command.txt", "w", encoding="utf-8") as file:
            file.write(cmd)

    def _send_cmd_tcp(self, cmd: str) -> None:
        try:
            self._socket.send_string(cmd)
        except zmq.error.ZMQError as e:
            logger.error("ZMQ Error: %s", str(e))
