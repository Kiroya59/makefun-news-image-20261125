#!/usr/bin/env python3
"""news-image-20261125 entry program (Python 3.13, stdlib only).

Validates the bundled image.png (PNG magic, size limit, IHDR 1024x1024
with a correct CRC), copies it to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output), then re-reads the output and verifies it is
byte-identical to the source. No network, no drawing at run time:
the same input bytes always produce the same output bytes.
"""
import os
import struct
import sys
import zlib

MAX_BYTES = 1048576
WANT_W, WANT_H = 1024, 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "image.png")
    try:
        with open(src, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        return fail("cannot read image.png: %s" % exc)

    if len(data) > MAX_BYTES:
        return fail("image.png is %d bytes, over the 1 MiB limit" % len(data))
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        return fail("image.png is not a PNG (bad magic bytes)")
    if len(data) < 8 + 25:
        return fail("image.png is too short to hold an IHDR chunk")

    # IHDR: length (4) + "IHDR" (4) + 13 data bytes + CRC (4).
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        return fail("first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WANT_W, WANT_H):
        return fail("image is %dx%d, expected 1024x1024" % (width, height))
    ihdr_crc_stored = struct.unpack(">I", data[29:33])[0]
    ihdr_crc = zlib.crc32(b"IHDR" + data[16:29]) & 0xFFFFFFFF
    if ihdr_crc != ihdr_crc_stored:
        return fail("IHDR CRC mismatch")

    # Walk every chunk: length, type, data, CRC; each CRC must match,
    # chunks must end exactly at the IEND trailer with no trailing bytes.
    pos = 8
    seen_iend = False
    seen_idat = False
    while True:
        if pos + 8 > len(data):
            return fail("truncated chunk header at offset %d" % pos)
        clen = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + clen
        if end > len(data):
            return fail("truncated %s chunk at offset %d" % (ctype.decode("latin1"), pos))
        stored = struct.unpack(">I", data[pos + 8 + clen:pos + 12 + clen])[0]
        actual = zlib.crc32(ctype + data[pos + 8:pos + 8 + clen]) & 0xFFFFFFFF
        if stored != actual:
            return fail("%s chunk CRC mismatch" % ctype.decode("latin1"))
        pos = end
        if ctype == b"IDAT":
            seen_idat = True
        if ctype == b"IEND":
            seen_iend = True
            break
        if ctype == b"IDAT" and clen == 0:
            return fail("empty IDAT chunk")
    if not seen_iend:
        return fail("missing IEND trailer")
    if not seen_idat:
        return fail("no IDAT chunk: image carries no pixel data")
    if pos != len(data):
        return fail("%d trailing bytes after IEND" % (len(data) - pos))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        return fail("cannot create output dir: %s" % exc)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        with open(out_path, "wb") as fh:
            fh.write(data)
        with open(out_path, "rb") as fh:
            back = fh.read()
    except OSError as exc:
        return fail("cannot write/read output: %s" % exc)
    if back != data:
        return fail("output differs from image.png after copy")
    print("ok: entry.png %dx%d, %d bytes" % (width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
