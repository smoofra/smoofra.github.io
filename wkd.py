#!/usr/bin/env python3
"""Mirror WKD keys from the advanced-mode server into direct-mode files.

Run by Quarto as a pre-render step.  Writes .well-known/openpgpkey/ so that
https://elder-gods.org/.well-known/openpgpkey/hu/<hash> serves the same keys as
https://openpgpkey.elder-gods.org/.well-known/openpgpkey/elder-gods.org/hu/<hash>.
"""

import hashlib
import shutil
import urllib.request
from pathlib import Path

DOMAIN = "elder-gods.org"
ADVANCED = f"https://openpgpkey.{DOMAIN}/.well-known/openpgpkey/{DOMAIN}"

# Local parts of the addresses to publish.  Direct mode has no catch-all, so
# every address needs to be listed here.
LOCAL_PARTS = ["larry", "cthulhu", "demogorgon", "root"]

ZBASE32 = "ybndrfg8ejkmcpqxot1uwisza345h769"


def zbase32(data):
    n = int.from_bytes(data, "big")
    bits = len(data) * 8
    pad = -bits % 5
    n <<= pad
    bits += pad
    return "".join(ZBASE32[(n >> (bits - 5 * (i + 1))) & 31] for i in range(bits // 5))


def wkd_hash(local):
    return zbase32(hashlib.sha1(local.lower().encode()).digest())


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def main():
    out = Path(".well-known/openpgpkey")
    files = {"policy": fetch(f"{ADVANCED}/policy")}
    for local in LOCAL_PARTS:
        h = wkd_hash(local)
        files[f"hu/{h}"] = fetch(f"{ADVANCED}/hu/{h}?l={local}")

    # Fetch everything before touching the output, so a network failure leaves
    # the existing files alone.
    if out.exists():
        shutil.rmtree(out)
    for name, data in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"wkd: wrote {path}")


if __name__ == "__main__":
    main()
