"""Run the API locally: uv run python -m provenance.api [--port 8000] [--reload]

Interactive docs: http://127.0.0.1:8000/docs
"""

import argparse
import sys

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="provenance.api")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    uvicorn.run(
        "provenance.api.main:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        # psycopg's async mode can't run on Windows' default Proactor event loop.
        loop="asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto",
    )


if __name__ == "__main__":
    main()
