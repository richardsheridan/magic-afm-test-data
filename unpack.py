"""Unpack the files listed in SHA256SUMS.txt and check each against its row.

Usage (Python 3, standard library only):

    python unpack.py DEST [RELPATH...]      write DEST/RELPATH for every row, or those named
    python unpack.py --check [RELPATH...]   check the rows, write nothing

A file already in DEST with the listed sha256 is left alone. Exits 1 if any stored
size or sha256 does not match.
"""

import argparse
import hashlib
import lzma
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "SHA256SUMS.txt"


def rows():
    for line in MANIFEST.read_text().splitlines():
        if line and not line.startswith("#"):
            sha, raw, stored, _chain, relpath = line.split(maxsplit=4)
            yield sha, int(raw), int(stored), relpath


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="check only, no DEST")
    parser.add_argument("paths", nargs="*", help="DEST, then the rows to unpack")
    args = parser.parse_args()
    if args.check:
        dest, relpaths = None, args.paths
    elif args.paths:
        dest, relpaths = Path(args.paths[0]), args.paths[1:]
    else:
        parser.error("give DEST, or --check")

    wanted = set(relpaths)
    failed = 0
    for sha, raw, stored, relpath in rows():
        if wanted and relpath not in wanted:
            continue
        wanted.discard(relpath)
        packed = HERE / (relpath + ".xz")
        target = None if dest is None else dest / relpath
        if target is not None and target.exists() and sha256(target) == sha:
            print(f"present  {relpath}")
            continue
        if packed.stat().st_size != stored:
            print(f"BAD SIZE {relpath}.xz: {packed.stat().st_size}, listed {stored}")
            failed += 1
            continue
        data = lzma.decompress(packed.read_bytes())
        if len(data) != raw or hashlib.sha256(data).hexdigest() != sha:
            print(f"BAD DATA {relpath}")
            failed += 1
            continue
        if target is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        print(f"ok       {relpath}")
    for relpath in sorted(wanted):
        print(f"NOT LISTED {relpath}")
        failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
