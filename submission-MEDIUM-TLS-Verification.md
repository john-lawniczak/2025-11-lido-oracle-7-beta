## Titles
1. Credential exfiltration and alert tampering via HTTP in OpsGenie client
2. Missing HTTPS enforcement in OpsGenie client exposes API key and alerts

## Summary
The OpsGenie client in Accounting Oracle v7 accepts an arbitrary `api_url` and performs requests without enforcing HTTPS. When configured with an `http://` URL, it transmits the `Authorization: GenieKey …` secret and the alert payload in plaintext, enabling interception and tampering. No code-level control rejects non-HTTPS or pins certificates.

## Finding Description
The OpsGenie integration sends alerts using `requests.post` with headers containing the OpsGenie API key. The code does not validate the URL scheme and relies entirely on the provided `api_url`, which is sourced directly from the environment without defaults or scheme checks.

Key callsite using `requests.post` (no scheme enforcement; `verify` not specified):

```python
// 42:58:src/utils/api/opsgenie.py
        headers = {
            'Authorization': f'GenieKey {self.api_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                f'{self.api_url}/v2/alerts',
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.warning(
                {'msg': f'OpsGenie is not available: {e}.'}
            )
```

No URL scheme validation in the client constructor:

```python
// 19:27:src/utils/api/opsgenie.py
    def __init__(
        self,
        api_key: str,
        api_url: str,
        logger: logging.Logger,
    ) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.logger = logger
```

Environment variables feed the client directly, with no default `https://` or validation:

```python
// 93:96:src/variables.py
# - OpsGenie -
OPSGENIE_API_KEY: Final[str] = os.getenv('OPSGENIE_API_KEY', '')
OPSGENIE_API_URL: Final[str] = os.getenv('OPSGENIE_API_URL', '')
```

The pytest hook will send alerts using whatever URL is configured, including `http://`:

```python
// 163:169:src/modules/checks/suites/conftest.py
            opsgenie_api.send_opsgenie_alert({
                'message': f'Oracle check: {check_name}',
                'description': f'Reason: {reason}',
                'priority': opsgenie_api.AlertPriority.MINOR.value,
                'tags': ['oracle_checks', 'oracle'],
                'details': {'alertname': 'OracleDailyChecks'},
            })
```

Global overrides that disable TLS verification are absent in the repository: no `verify=False`, no `requests.Session().verify = False`, no `urllib3.disable_warnings(InsecureRequestWarning)`, and no `REQUESTS_CA_BUNDLE`/`SSL_CERT_FILE` usage. The defect is the lack of scheme enforcement, which allows a plaintext `http://` configuration to exfiltrate credentials and data without any in-code guardrail.

## Impact and Likelihood Explanation
Impact: When `OPSGENIE_API_URL` is set to an `http://` endpoint, the client sends the OpsGenie API key in the `Authorization` header and the alert JSON body in plaintext. A network attacker intercepts the key and reuses it to manage alerts, forging or suppressing notifications and degrading incident response integrity.

Likelihood: Default operational setups use `https://` endpoints, but a single environment misconfiguration routes traffic to `http://`. The code performs no scheme validation, so any misconfiguration immediately results in plaintext transmission and credential compromise.

## Recommendation
Enforce `https://` in the client and make TLS verification explicit. Reject non-HTTPS `api_url` at construction time and pass `verify=True` in the request call.

```diff
// 1:120:src/utils/api/opsgenie.py
--- a/src/utils/api/opsgenie.py
+++ b/src/utils/api/opsgenie.py
@@
 import requests
 import logging
 from enum import Enum
+from urllib.parse import urlparse
@@ class OpsGenieAPI:
     def __init__(
         self,
         api_key: str,
         api_url: str,
         logger: logging.Logger,
     ) -> None:
         self.api_key = api_key
         self.api_url = api_url
         self.logger = logger
+        if self.api_url:
+            parsed = urlparse(self.api_url)
+            if parsed.scheme != 'https':
+                raise ValueError('OPSGENIE_API_URL must use https://')
@@     def send_opsgenie_alert(
         try:
             response = requests.post(
                 f'{self.api_url}/v2/alerts',
                 json=payload,
                 headers=headers,
                 timeout=10,
+                verify=True,
             )
             response.raise_for_status()
```

## POC

General steps:
1) Start a minimal local HTTP capture server that logs the raw request line, headers, and JSON body.
2) Send a request shaped like the OpsGenie alert call to `http://127.0.0.1:8081/v2/alerts` with `Authorization: GenieKey …` and a JSON body.
3) Observe the plaintext Authorization header and payload in the capture output.

Files added:
- `poc/http_capture.py`: One-shot HTTP server that records the incoming request to stdout and a file.
- `poc/poc_opsgenie_http.py`: Minimal sender that posts the alert JSON with an Authorization header to the HTTP endpoint.

Commands to run:

```text
# 1) Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip requests

# 2) In Terminal 1: start the capture server (exits after one request)
python3 -u poc/http_capture.py --port 8081 --outfile captured-http.txt

# 3) In Terminal 2: send the plaintext HTTP request
python poc/poc_opsgenie_http.py

# 4) View the captured plaintext
cat captured-http.txt
```

PoC Code:

```python
// 1:75:poc/http_capture.py
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional


class OneShotHandler(BaseHTTPRequestHandler):
    outfile_path: Optional[str] = None

    def _write_log(self, content: str) -> None:
        # Write to stdout
        self.wfile.flush()
        print(content, flush=True)
        # Also persist to file if provided
        if self.outfile_path:
            with open(self.outfile_path, "a", encoding="utf-8") as f:
                f.write(content)
                if not content.endswith("\n"):
                    f.write("\n")

    def do_POST(self):  # noqa: N802 (BaseHTTPRequestHandler naming)
        # Read request body
        content_length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Log request line, headers, and body
        self._write_log(f"{self.command} {self.path} {self.request_version}")
        # Reconstruct minimal start-line compatible with PoC expectations
        host = self.headers.get("Host", "")
        self._write_log(f"Host: {host}")
        for key, value in self.headers.items():
            if key.lower() != "host":
                self._write_log(f"{key}: {value}")
        self._write_log("")
        try:
            body_text = body.decode("utf-8", errors="replace")
        except Exception:
            body_text = repr(body)
        self._write_log(body_text)

        # Respond OK
        self.send_response(200)
        response_body = b"OK"
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(response_body)
        self.wfile.flush()
        # Ensure the connection is not kept alive
        self.close_connection = True

        # Shutdown the server after handling this single request
        self.server.shutdown()  # type: ignore[attr-defined]


def main():
    parser = argparse.ArgumentParser(description="Minimal HTTP capture server (one-shot).")
    parser.add_argument("--port", type=int, default=8081, help="Port to listen on (default: 8081)")
    parser.add_argument("--outfile", type=str, default="", help="File to append captured request to")
    args = parser.parse_args()

    OneShotHandler.outfile_path = args.outfile or None

    httpd = HTTPServer(("127.0.0.1", args.port), OneShotHandler)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
```

```python
// 1:37:poc/poc_opsgenie_http.py
import logging
import requests


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    api_key = "TEST_API_KEY"
    api_url = "http://127.0.0.1:8081"  # plaintext endpoint for PoC
    headers = {
        "Authorization": f"GenieKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": "test",
        "description": "plaintext demo",
        "priority": "P4",
        "tags": ["oracle_checks", "oracle"],
    }
    response = requests.post(
        f"{api_url}/v2/alerts",
        json=payload,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()


if __name__ == "__main__":
    main()
```

PoC result output (captured plaintext):

```text
// 1:12:captured-http.txt
POST /v2/alerts HTTP/1.1
Host: 127.0.0.1:8081
User-Agent: python-requests/2.32.5
Accept-Encoding: gzip, deflate, zstd
Accept: */*
Connection: keep-alive
Authorization: GenieKey TEST_API_KEY
Content-Type: application/json
Content-Length: 107

{"message": "test", "description": "plaintext demo", "priority": "P4", "tags": ["oracle_checks", "oracle"]}
```

