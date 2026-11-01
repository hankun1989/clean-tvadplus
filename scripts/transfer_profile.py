#!/usr/bin/env python3
"""Transfer one configuration through ADB reverse and loopback only."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shlex
import subprocess
import threading
import time
from urllib.parse import urlencode, urlsplit

PACKAGE = "com.github.metacubex.clash.meta"


def adb(serial, *args):
    return subprocess.run(["adb", "-s", serial, *args], check=True,
                          capture_output=True, text=True, errors="replace", timeout=30)


def make_handler(payload):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path != "/profile.yaml":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/yaml; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            print("Transferred; verify Save and activation on the TV.", flush=True)

        def log_message(self, format, *args):
            pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="Exact authorized adb device")
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--name", default="TV-ad-filter")
    parser.add_argument("--refresh-only", action="store_true", help="Serve at an existing profile URL; refresh that profile in the TV UI")
    parser.add_argument("--device-port", type=int, default=18765)
    parser.add_argument("--seconds", type=int, default=180)
    args = parser.parse_args()
    if not 1024 <= args.device_port <= 65535 or not 1 <= args.seconds <= 900:
        parser.error("Port must be 1024..65535; duration must be 1..900 seconds")
    payload = args.profile.read_bytes()
    if not payload or len(payload) > 1024 * 1024:
        parser.error("Profile must be nonempty and at most 1 MiB")
    if adb(args.serial, "get-state").stdout.strip() != "device":
        parser.error("Selected device is not connected and authorized")
    if not adb(args.serial, "shell", "pm", "path", PACKAGE).stdout.strip().startswith("package:"):
        parser.error("Install and verify the official CMFA APK first")
    remote = f"tcp:{args.device_port}"
    for row in adb(args.serial, "reverse", "--list").stdout.splitlines():
        if remote in row.split():
            parser.error("Port already forwarded; choose a different --device-port")
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(payload))
    mapped = False
    thread = None
    try:
        adb(args.serial, "reverse", remote, f"tcp:{server.server_address[1]}")
        mapped = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "clashmeta://install-config?" + urlencode({
            "url": f"http://127.0.0.1:{args.device_port}/profile.yaml", "name": args.name})
        command = ("am start -a android.intent.action.VIEW -d "
                   + shlex.quote(url) + " -p " + PACKAGE)
        if not args.refresh_only:
            adb(args.serial, "shell", command)
        else:
            print("Refresh the existing profile at this device port in the TV UI.", flush=True)
        print(f"Loopback-only transfer ready for {args.seconds}s. Ctrl+C closes early.", flush=True)
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            time.sleep(min(1, max(0, deadline - time.monotonic())))
    except KeyboardInterrupt:
        pass
    finally:
        if thread:
            server.shutdown()
            thread.join(timeout=3)
        server.server_close()
        if mapped:
            try:
                adb(args.serial, "reverse", "--remove", remote)
            except (subprocess.SubprocessError, OSError) as error:
                print(f"Mapping cleanup needs reconnection: {type(error).__name__}")
                print(f"Reconnect then run: adb -s <same-device> reverse --remove {remote}")
        print("Transfer closed. Importing alone does not prove filtering works.")


if __name__ == "__main__":
    main()
