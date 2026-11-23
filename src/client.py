"""Client for interacting with the HTTP API."""

import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8080/rest/api/v1.0"
TIMEOUT_SECONDS = 2

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class ApiClient:
    """API client for compression tasks."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        """Initialize client with base URL."""
        self.base_url = base_url

    def _request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> tuple[int, dict | list]:
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en",
        }
        payload = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(
            url, data=payload, headers=headers, method=method
        )
        try:
            with _OPENER.open(req, timeout=TIMEOUT_SECONDS) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as e:
            return e.code, {}

    def session_submit(self, uid: int, data: dict) -> tuple[int, dict]:
        """Submit a session."""
        return self._request("PUT", f"session/submit/{uid}", data)

    def session_pop(self, uid: int) -> tuple[int, dict]:
        """Pop a session."""
        return self._request("DELETE", f"session/pop/{uid}")

    def session_search(self) -> tuple[int, list]:
        """Search sessions."""
        return self._request("GET", "session/search")

    def session_adjust(self, data: dict) -> tuple[int, dict]:
        """Adjust session."""
        return self._request("POST", "session/adjust", data)

    def instruction_submit(self, uid: int, data: dict) -> tuple[int, dict]:
        """Submit an instruction."""
        return self._request("PUT", f"instruction/submit/{uid}", data)

    def instruction_pop(self, uid: int) -> tuple[int, dict]:
        """Pop an instruction."""
        return self._request("DELETE", f"instruction/pop/{uid}")

    def instruction_search(self, session_id: int) -> tuple[int, list]:
        """Search instructions by session."""
        return self._request("GET", f"instruction/search/{session_id}")

    def instruction_adjust(self, data: dict) -> tuple[int, dict]:
        """Adjust an instruction."""
        return self._request("POST", "instruction/adjust", data)

    def response_search(self, instruction_id: int) -> tuple[int, list]:
        """Search responses by instruction."""
        return self._request("GET", f"response/search/{instruction_id}")

    def report_search(self) -> tuple[int, list]:
        """Get report."""
        return self._request("GET", "report/search")
