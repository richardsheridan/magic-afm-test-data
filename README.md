# magic-afm test data

Real AFM files that the slow tests of
[magic-afm](https://github.com/richardsheridan/magic-afm) read: one file for each reader
path, grid shape, curve length, trace case and format pair, plus a few vendor exports
that serve as independent references. Released under CC0 1.0 (`LICENSE`).

This repository is magic-afm's `tests/magic-afm-test-data` submodule, and every command
below runs from magic-afm's root. To get it there, clone magic-afm with
`--recurse-submodules`, or run `git submodule update --init` in a checkout.

## Layout

Each file is stored as `<path>.xz`, where `<path>` is the name magic-afm's tests pass
to their `real_data_file` fixture. `SHA256SUMS.txt` has one row per file: the sha256 of
the original file, its size, the stored size, the filter chain in `xz`'s own option
syntax, and the path. The chain is enough to rebuild the stored bytes, for example:

```bash
xz -T1 --format=xz --check=crc64 --delta=dist=4 --lzma2=preset=9e,lc=0,lp=2,pb=2 -c FILE
```

## Unpacking

magic-afm's tests read the `.xz` files in place and unpack them into a cache. To get
the original files, for example into magic-afm's git-ignored `example.data/test_cases/`
(`unpack.py` needs only the standard library):

```bash
pixi run -e test python tests/magic-afm-test-data/unpack.py example.data/test_cases
pixi run -e test python tests/magic-afm-test-data/unpack.py --check
```

The first writes every file and checks it against its row; the second checks every
row and writes nothing.

## Files

133.2 MB stored, 455.7 MB unpacked. Sizes in MB.

| Path | What it covers | Original | Stored |
|---|---|---|---|
| `PDMS_SAA/ffm/both0001.ARDF` | Asylum fast force map with trace and retrace volumes and 10 images | 50.0 | 15.0 |
| `PDMS_SAA/ffm/both0001.h5` | Asylum's `.h5` conversion of `both0001`, the ARDF/ARH5 pair | 49.3 | 14.0 |
| `PDMS_SAA/ffm/rtrace0001.ARDF` | Retrace only | 25.0 | 7.8 |
| `PDMS_SAA/ffm/rtrace0001.h5` | Its `.h5` conversion, the retrace-only pair | 24.7 | 7.3 |
| `PDMS_SAA/ffm/onekhz0001.ARDF` | Trace only | 25.0 | 7.8 |
| `PDMS_SAA/ffm/hard0001.ARDF` | Stopped scan, rows 0 to 18 acquired, scanning up | 14.9 | 4.6 |
| `PDMS_SAA/ffm/hard0003.ARDF` | Stopped scan, rows 13 to 31 acquired, scanning down | 14.9 | 4.6 |
| `PDMS_SAA/ffm/mellow0003.ARDF` | Stopped scan, rows 15 to 31 acquired, scanning down; (0, 0) never acquired | 13.4 | 4.2 |
| `PDMS_SAA/ffm/hundhz0001.ARDF` | Curve length: 2500 points at 2 µs steps | 61.9 | 16.4 |
| `PDMS_SAA/ffm/twoxln0001.ARDF` | Non-square grid: 64 lines of 32 points | 49.9 | 15.3 |
| `PDMS_SAA/ffm/twoxpt0001.ARDF` | Non-square grid: 32 lines of 64 points | 49.9 | 15.2 |
| `PDMS_SAA/ffm/hyte2x0001.ARDF` | Scan aspect: 500 x 1000 nm | 25.0 | 7.6 |
| `PDMS_SAA/ffm/wide2x0001.ARDF` | Scan aspect: 1000 x 500 nm | 25.0 | 7.7 |
| `AC160s00.ARDF` | Asylum slow force map, 5 x 6, extends of 339 to 535 points, an Away segment | 0.6 | 0.2 |
| `AC160s00.h5` | Its `.h5` conversion, the slow-map pair | 0.7 | 0.2 |
| `PS_PCL_SAA/QNM/onekhz.000.pfc` | Nanoscope PeakForce QNM capture, 32 x 32, 128 points per curve | 0.6 | 0.2 |
| `PS_PCL_SAA/QNM/onekhz.001.pfc` | A second QNM capture, the source of the two `onekhz.001` exports | 0.6 | 0.2 |
| `PS_PCL_SAA/QNM/maxscanrate.000.pfc` | The skipped-point mode (`Bytes/pixel: 0`), which readers refuse | 0.2 | 0.1 |
| `onekhz.001.pfc-record261-retract-ascii.txt` | Nanoscope Analysis ASCII export of record 261's retract (reader (8, 5)), the reference for `.pfc` deflection | 0.004 | 0.001 |
| `onekhz.001.pfc-8B8F_ForceCurveIndex_296.spm` | Nanoscope Analysis export of record 296, the .5 rounding case of the marker fill | 0.08 | 0.007 |
| `A1_OCSOH-PMMA21k_300421.0_300425.spm` | Nanoscope force volume, 32 x 32, 512 + 512 points; pixel (12, 3) has a sentinel z | 16.9 | 2.0 |
| `A1_OCSOH-PMMA21k_300421.0_300425.spm-6616_ForceCurveIndex_100.spm` | Nanoscope Analysis export of an ordinary `A1` pixel, reader (3, 4) | 0.1 | 0.01 |
| `A1_OCSOH-PMMA21k_300421.0_300425.spm-6616_ForceCurveIndex_387.spm` | Nanoscope Analysis export of the sentinel pixel, reader (12, 3) | 0.1 | 0.01 |
| `DOE4_20nN_80nm.0_00012.spm` | Nanoscope force volume, 8 x 8, whose scan list states a stale grid | 1.1 | 0.2 |
| `20251216_141819_PVDF2_Film_U_00002.nid` | Nanosurf spectroscopy map, 10 x 10, extends of 967 to 1024 points | 6.0 | 2.6 |
| `PVDF2_Film_U_00002/CSV/PVDF2_Film_U_00002_R10_C01.csv` | Nanosurf's export of the `.nid` curve at reader (0, 0) | 0.05 | 0.006 |
| `PVDF2_Film_U_00002/CSV/PVDF2_Film_U_00002_R01_C10.csv` | The opposite corner, reader (9, 9) | 0.05 | 0.009 |
| `PVDF2_Film_U_00002/CSV/PVDF2_Film_U_00002_R10_C02.csv` | The shortest extend, reader (0, 1), 967 points | 0.05 | 0.009 |

Pixel positions are (row, column) as magic-afm's readers index them. Nanosurf's `R`
and `C` map to reader `(rows - R, C - 1)`.

## Adding a file

`pack.py` uses magic-afm's readers from the checkout it sits in:

```bash
pixi run -e test python tests/magic-afm-test-data/pack.py SOURCE RELPATH...
```

It writes `RELPATH.xz` for each `SOURCE/RELPATH` and adds or replaces its row in
`SHA256SUMS.txt`. The chain is chosen per file:

- When a magic-afm reader accepts the file, a delta of the sample width it reports. The
  lzma2 settings `lc=0` and `lp = pb = log2(width)` go with it.
- Otherwise, the candidate (no delta, or a delta of 1, 2, 4 or 8) that best compresses
  the file at preset 6. A file of up to 3 MiB is tried whole; a larger one is tried as
  three 1 MiB chunks, from its start, middle and end.

The stored file is then written at preset 9e. Compression runs on one thread, so packing
a file twice gives the same bytes.

Then commit and push here, and commit the submodule's new commit in magic-afm, which
pins this repository by commit. Tags mark versions for people. Every version of every
file stays in the history and counts against the size budget, so add files rather than
replace them.

## Size and purging

The budget is 1 GB, but smaller is better. Past 1 GB, large files move to release assets
rather than the git history.

To remove a file from the history:

1. In a fresh clone, run `git filter-repo --invert-paths --path PATH.xz`, and remove its
   row from `SHA256SUMS.txt` in the rewritten history.
2. Force-push `main` and every tag that contained it.
3. Point magic-afm's submodule at the rewritten commit. Older magic-afm commits still
   name the old one, so their real-data tests no longer find the data.
4. Ask GitHub Support to remove cached views and unreferenced objects.

Existing clones and forks keep their copies, so purging only stops further distribution.
