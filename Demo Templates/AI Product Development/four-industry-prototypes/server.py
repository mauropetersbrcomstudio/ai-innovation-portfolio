"""Serve the four local prototypes over loopback with Python's standard library."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).resolve().parent), **kwargs)


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8768), Handler) as server:
        print("Open http://127.0.0.1:8768/", flush=True)
        server.serve_forever()
