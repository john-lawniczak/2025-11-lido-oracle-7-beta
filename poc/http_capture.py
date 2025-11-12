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


