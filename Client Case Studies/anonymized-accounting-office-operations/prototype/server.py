"""Serve the local accounting-office prototype on loopback only."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

class LocalOnlyServer(ThreadingHTTPServer):
    allow_reuse_address = True

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

if __name__ == "__main__":
    host, port = "127.0.0.1", 8767
    print(f"Local prototype: http://{host}:{port}")
    print("Files selected in the browser are not uploaded or persisted by this server.")
    try:
        LocalOnlyServer((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
