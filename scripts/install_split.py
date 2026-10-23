#!/usr/bin/env python3
"""Install locked project-local tooling and the checksum-pinned WASM core."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = "7.4.3"
CORE_VERSION = "7.6.8"
CORE_NAME = "libffi-wasm32-wasip1.wasm"
CORE_SHA256 = "05a88dcb9a0b0d1e14daf0f429d9af6e2ac8d94d9e574523a76d3e9f440dccc9"
CORE_URLS = (
    f"https://github.com/KonghaYao/cn-font-split/releases/download/{CORE_VERSION}/{CORE_NAME}",
    "https://api.github.com/repos/KonghaYao/cn-font-split/releases/assets/315110498",
)


def valid_core(data: bytes) -> bool:
    return hashlib.sha256(data).hexdigest() == CORE_SHA256


def install() -> None:
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
    if not npm or not shutil.which("node"):
        raise RuntimeError("Node.js and npm must be available on PATH")
    local = ROOT / "_tools"
    dist = local / "node_modules/cn-font-split/dist"
    core = dist / CORE_NAME
    # Keep a verified existing core across npm ci, which replaces node_modules.
    data = core.read_bytes() if core.is_file() else b""
    if not valid_core(data):
        data = b""
    local.mkdir(exist_ok=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copy2(ROOT / "tools" / name, local / name)
    subprocess.run([npm, "ci", "--prefix", str(local), "--ignore-scripts",
                    "--cache", str(ROOT / "_npm-cache"), "--no-audit", "--no-fund"], check=True)
    package = json.loads((dist.parent / "package.json").read_text("utf-8"))
    if package["version"] != PACKAGE_VERSION:
        raise RuntimeError("Unexpected cn-font-split package version")
    if not data:
        errors = []
        for url in CORE_URLS:
            try:
                request = urllib.request.Request(url, headers={
                    "User-Agent": "Pico-build",
                    "Accept": "application/octet-stream",
                })
                with urllib.request.urlopen(request, timeout=30) as response:
                    candidate = response.read()
                if not valid_core(candidate):
                    raise ValueError("WASM core SHA-256 does not match the pinned release")
                data = candidate
                break
            except Exception as error:
                errors.append(str(error))
        if not data:
            raise RuntimeError("Could not install WASM core: " + "; ".join(errors))
    core.write_bytes(data)
    print(f"Installed cn-font-split {PACKAGE_VERSION}, WASM core {CORE_VERSION} (SHA-256 verified).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", action="store_true", help="Split all built fonts after installation")
    args = parser.parse_args()
    install()
    if args.split:
        subprocess.run([sys.executable, str(ROOT / "split.py")], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        sys.exit(1)
