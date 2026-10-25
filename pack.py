"""Pack corpus files into this repository, one .xz each, and list them in SHA256SUMS.txt.

This repository is magic-afm's tests/magic-afm-test-data submodule. Run from
magic-afm's root:

    pixi run -e test python tests/magic-afm-test-data/pack.py SOURCE RELPATH...

Each SOURCE/RELPATH is written here as RELPATH.xz, and its manifest row is added
or replaced. The filter chain is chosen per file: a delta of the file's sample
width when a magic_afm reader accepts the file, otherwise whichever candidate
compresses a sample of the file best. Compression is single-threaded, so packing
the same file twice gives the same bytes.
"""

import argparse
import hashlib
import lzma
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# the magic-afm checkout this repository is the tests/magic-afm-test-data submodule of
sys.path.insert(0, str(HERE.parents[1]))

from magic_afm.data_readers import SUFFIX_FVFILE_MAP, FileFormatError  # noqa: E402

MANIFEST = HERE / "SHA256SUMS.txt"
MANIFEST_HEADER = (
    "# sha256 of the ORIGINAL file, original bytes, stored bytes, chain, path;\n"
    "# each file is stored as path.xz, LF line endings, rows sorted by path\n"
)

# Delta distances to try; None is lzma2 alone.
CANDIDATES = (None, 1, 2, 4, 8)
FINAL_PRESET = 9 | lzma.PRESET_EXTREME
SAMPLE_PRESET = 6
WHOLE_FILE_LIMIT = 3 << 20
CHUNK = 1 << 20


def lzma2_options(dist):
    if dist is None:
        return {}
    bits = dist.bit_length() - 1
    return {"lc": 0, "lp": bits, "pb": bits}


def filters(dist, preset):
    lzma2 = {"id": lzma.FILTER_LZMA2, "preset": preset, **lzma2_options(dist)}
    if dist is None:
        return [lzma2]
    return [{"id": lzma.FILTER_DELTA, "dist": dist}, lzma2]


def chain_name(dist):
    """The chain in xz's own option syntax, enough to reproduce the bytes."""
    overrides = [f"{k}={v}" for k, v in lzma2_options(dist).items()]
    options = ",".join(["preset=9e", *overrides])
    if dist is None:
        return f"lzma2:{options}"
    return f"delta:dist={dist}+lzma2:{options}"


def header_distance(path):
    """The sample width a magic_afm reader reports, or None if it has no answer."""
    entry = SUFFIX_FVFILE_MAP.get(path.suffix.lower())
    if entry is None:
        return None
    fvfile_cls, opener = entry
    data = opener(path)
    try:
        width = fvfile_cls.sample_width(data)
    except FileFormatError:
        return None
    finally:
        data.close()
    return width if width in CANDIDATES else None


def sampled_distance(data):
    """The candidate that best compresses the file, or three 1 MiB chunks of it."""
    if len(data) <= WHOLE_FILE_LIMIT:
        samples = [data]
    else:
        middle = (len(data) - CHUNK) // 2
        samples = [data[:CHUNK], data[middle : middle + CHUNK], data[-CHUNK:]]

    def packed_size(dist):
        f = filters(dist, SAMPLE_PRESET)
        return sum(len(lzma.compress(s, filters=f)) for s in samples)

    return min(CANDIDATES, key=packed_size)


def pack(source, relpath):
    path = source / relpath
    data = path.read_bytes()
    dist = header_distance(path)
    how = "header"
    if dist is None:
        dist = sampled_distance(data)
        how = "sampled"
    packed = lzma.compress(
        data,
        format=lzma.FORMAT_XZ,
        check=lzma.CHECK_CRC64,
        filters=filters(dist, FINAL_PRESET),
    )
    out = HERE / (relpath + ".xz")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(packed)
    sha = hashlib.sha256(data).hexdigest()
    print(f"{relpath}: {how} {chain_name(dist)}, {len(data)} -> {len(packed)}")
    return sha, len(data), len(packed), chain_name(dist), relpath


def read_manifest():
    rows = {}
    if MANIFEST.exists():
        for line in MANIFEST.read_text().splitlines():
            if line and not line.startswith("#"):
                sha, raw, stored, chain, relpath = line.split(maxsplit=4)
                rows[relpath] = (sha, int(raw), int(stored), chain, relpath)
    return rows


def write_manifest(rows):
    lines = ["  ".join(map(str, rows[k])) + "\n" for k in sorted(rows)]
    with MANIFEST.open("w", newline="\n") as f:
        f.write(MANIFEST_HEADER + "".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="root the relpaths are under")
    parser.add_argument("relpaths", nargs="+", help="paths as they will be listed")
    args = parser.parse_args()
    rows = read_manifest()
    for relpath in args.relpaths:
        rows[relpath] = pack(args.source, Path(relpath).as_posix())
    write_manifest(rows)


if __name__ == "__main__":
    main()
