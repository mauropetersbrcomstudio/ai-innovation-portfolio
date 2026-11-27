"""Serve the Logistics Demo locally; no external integrations or network calls are used."""
from __future__ import annotations
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class LocalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

def main() -> None:
    parser = argparse.ArgumentParser(description="Logistics Operations Workspace — local MVP")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), LocalHandler)
    print(f"Logistics Demo disponível em http://127.0.0.1:{args.port}")
    print("Acesso restrito a este computador. Pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
