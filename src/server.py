"""HTTP server with API for compression tasks."""

import json
import os
import subprocess
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from src import constants as const
from src import storage
from src.db import init_db

TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"
PREFIX = ["rest", "api", "v1.0"]
RESOURCE_SESSION = "session"
RESOURCE_INSTRUCTION = "instruction"
RESOURCE_RESPONSE = "response"
RESOURCE_REPORT = "report"


def check_headers(headers: dict) -> tuple[int, str]:
    """Validate required headers."""
    method = headers.get("_method", const.METHOD_GET)
    if method in (const.METHOD_POST, const.METHOD_PUT, const.METHOD_PATCH):
        if headers.get(const.HEADER_CONTENT_TYPE) != const.VALUE_JSON:
            return (
                const.HTTP_UNSUPPORTED_MEDIA_TYPE,
                "Unsupported Media Type",
            )
    if headers.get(const.HEADER_ACCEPT) != const.VALUE_JSON:
        return const.HTTP_NOT_ACCEPTABLE, "Not Acceptable"
    if headers.get(const.HEADER_ACCEPT_LANGUAGE) != const.VALUE_LANGUAGE_EN:
        return const.HTTP_NOT_ACCEPTABLE, "Not Acceptable"
    return const.HTTP_OK, ""


class RequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests."""

    protocol_version = "HTTP/1.1"

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def _send_json(self, code: int, data: dict | list) -> None:
        response = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", const.VALUE_JSON)
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _handle_error(self, code: int, message: str) -> None:
        self._send_json(code, {"error": message})

    def _check_headers(self) -> bool:
        self.headers["_method"] = self.command
        code, msg = check_headers(dict(self.headers))
        if code != const.HTTP_OK:
            self._handle_error(code, msg)
            return False
        return True

    def _parse_path(self) -> tuple[list[str], dict[str, str]]:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = {}
        if parsed.query:
            for pair in parsed.query.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    query[k] = v
        return parts, query

    def _safe_int(self, value: str) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _process_request(self) -> None:
        if not self._check_headers():
            return

        parts, query = self._parse_path()
        body = self._read_body()

        if len(parts) < const.PREFIX_LEN or parts[:3] != PREFIX:
            self._handle_error(const.HTTP_NOT_FOUND, "Not Found")
            return

        try:
            self._route_request(parts, body, query)
        except Exception as err:
            traceback.print_exc()
            self._handle_error(
                const.HTTP_INTERNAL_SERVER_ERROR, str(err)
            )

    def _route_request(
        self, parts: list[str], body: dict, query: dict
    ) -> None:
        resource = parts[3]
        action = (
            parts[const.ACTION_INDEX]
            if len(parts) > const.ACTION_INDEX
            else ""
        )
        arg = (
            parts[const.ARG_INDEX]
            if len(parts) > const.ARG_INDEX
            else ""
        )

        if resource == RESOURCE_SESSION:
            self._handle_session(action, arg, body, query)
        elif resource == RESOURCE_INSTRUCTION:
            self._handle_instruction(action, arg, body, query)
        elif resource == RESOURCE_RESPONSE:
            self._handle_response(action, arg, query)
        elif resource == RESOURCE_REPORT:
            self._send_json(const.HTTP_OK, storage.get_report())
        else:
            self._handle_error(const.HTTP_NOT_FOUND, "Not Found")

    def _handle_session(
        self, action: str, arg: str, body: dict, query: dict
    ) -> None:
        if action == "submit" and self.command == const.METHOD_PUT:
            self._session_submit(arg, body)
        elif action == "pop" and self.command == const.METHOD_DELETE:
            self._session_pop(arg)
        elif action == "search" and self.command == const.METHOD_GET:
            self._send_json(const.HTTP_OK, storage.get_sessions())
        elif action == "adjust" and self.command == const.METHOD_POST:
            self._session_adjust(body)
        else:
            self._handle_error(
                const.HTTP_METHOD_NOT_ALLOWED, "Method Not Allowed"
            )

    def _session_submit(self, arg: str, body: dict) -> None:
        uid = self._safe_int(arg)
        data = storage.add_session(uid, body)
        self._send_json(const.HTTP_OK, data)

    def _session_pop(self, arg: str) -> None:
        success = storage.pop_session(self._safe_int(arg))
        self._send_json(const.HTTP_OK, {"success": success})

    def _session_adjust(self, body: dict) -> None:
        uid = self._safe_int(str(body.get("uid", 0)))
        data = storage.update_session(uid, body)
        self._send_json(const.HTTP_OK, data or {})

    def _handle_instruction(
        self, action: str, arg: str, body: dict, query: dict
    ) -> None:
        if action == "submit" and self.command == const.METHOD_PUT:
            self._instruction_submit(arg, body)
        elif action == "pop" and self.command == const.METHOD_DELETE:
            self._instruction_pop(arg)
        elif action == "search" and self.command == const.METHOD_GET:
            self._instruction_search(arg)
        elif action == "adjust" and self.command == const.METHOD_POST:
            self._instruction_adjust(body)
        else:
            self._handle_error(
                const.HTTP_METHOD_NOT_ALLOWED, "Method Not Allowed"
            )

    def _instruction_submit(self, arg: str, body: dict) -> None:
        uid = self._safe_int(arg)
        data = storage.add_instruction(uid, body)
        if not TEST_MODE:
            self._run_cli(data)
        self._send_json(const.HTTP_OK, data)

    def _instruction_pop(self, arg: str) -> None:
        success = storage.pop_instruction(self._safe_int(arg))
        self._send_json(const.HTTP_OK, {"success": success})

    def _instruction_search(self, arg: str) -> None:
        session_id = self._safe_int(arg)
        instructions = storage.get_instructions(session_id)
        self._send_json(const.HTTP_OK, instructions)

    def _instruction_adjust(self, body: dict) -> None:
        uid = self._safe_int(str(body.get("uid", 0)))
        data = storage.update_instruction(uid, body)
        self._send_json(const.HTTP_OK, data or {})

    def _handle_response(self, action: str, arg: str, query: dict) -> None:
        if action == "search" and self.command == const.METHOD_GET:
            instruction_id = self._safe_int(arg)
            responses = storage.get_responses(instruction_id)
            self._send_json(const.HTTP_OK, responses)
        else:
            self._handle_error(
                const.HTTP_METHOD_NOT_ALLOWED, "Method Not Allowed"
            )

    def _run_cli(self, instruction: dict) -> None:
        """Run CLI compression via subprocess."""
        payload = instruction.get("payload", "")
        uid = instruction.get("uid", 0)
        output = f"examples/output_{uid}.gz"
        try:
            subprocess.run(
                [sys.executable, "-m", "src.cli", payload, output],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        self._process_request()

    def do_POST(self) -> None:
        """Handle POST requests."""
        self._process_request()

    def do_PUT(self) -> None:
        """Handle PUT requests."""
        self._process_request()

    def do_DELETE(self) -> None:
        """Handle DELETE requests."""
        self._process_request()


def run_server(port: int = const.DEFAULT_PORT) -> None:
    """Start the HTTP server."""
    init_db()
    server = HTTPServer(("", port), RequestHandler)
    print(f"Server running on port {port}...")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
