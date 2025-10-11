#!/usr/bin/env python3
"""Simple uploader script for testing the file-service.

Usage:
  python scripts/upload_example.py --file path/to/file --chat-id curso123

It POSTs multipart/form-data to /upload and prints the server response.
"""
import argparse
import sys
from pathlib import Path
import json
import httpx


def main():
    p = argparse.ArgumentParser(description="Upload a file to the file-service for testing")
    p.add_argument("--file", "-f", required=True, help="Path to file to upload")
    p.add_argument("--chat-id", "-c", required=True, help="Chat ID to associate the file with")
    p.add_argument("--message-id", "-m", default=None, help="Optional message ID")
    p.add_argument("--thread-id", "-t", default=None, help="Optional thread ID")
    p.add_argument("--url", "-u", default="http://127.0.0.1:8000/upload", help="Upload URL (default: http://127.0.0.1:8000/upload)")
    args = p.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(2)

    data = {"chat_id": args.chat_id}
    if args.message_id:
        data["message_id"] = args.message_id
    if args.thread_id:
        data["thread_id"] = args.thread_id

    try:
        with file_path.open("rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            print(f"Uploading {file_path} to {args.url} ...")
            resp = httpx.post(args.url, data=data, files=files, timeout=30.0)

        print(f"Response: {resp.status_code}")
        try:
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            print(resp.text)

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
