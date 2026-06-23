from __future__ import annotations

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the image-process backend server.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8001")))
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload.")
    args = parser.parse_args()

    uvicorn.run(
        "image_process_backend.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
