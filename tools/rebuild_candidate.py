#!/usr/bin/env python3
"""Rebuild the verified mh2lm TWRP v0 image from its normal-mode donor."""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path


SOURCE_SHA256 = "ffc0a4e401192b57b00ba3bf90b23d8c17f675ae4fbad779ce8590b4d972c3bc"
OUTPUT_SHA256 = "b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3"
OUTPUT_SIZE = 47_796_224
MODE_SUFFIX = b" androidboot.mode=normal"


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def rebuild(source: Path) -> bytes:
    image = bytearray(source.read_bytes())
    source_hash = hashlib.sha256(image).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError(f"unexpected donor SHA-256: {source_hash}")
    if image[:8] != b"ANDROID!":
        raise ValueError("donor is not an Android boot image")

    (
        kernel_size,
        _kernel_addr,
        ramdisk_size,
        _ramdisk_addr,
        second_size,
        _second_addr,
        _tags_addr,
        page_size,
        header_version,
        _os_version,
    ) = struct.unpack_from("<10I", image, 8)

    if header_version != 0 or page_size != 4096 or second_size != 0:
        raise ValueError("unexpected boot header version, page size, or second stage")

    cmdline = bytes(image[64:576]).split(b"\0", 1)[0]
    if not cmdline.endswith(MODE_SUFFIX):
        raise ValueError("expected androidboot.mode=normal suffix is missing")

    rebuilt_cmdline = cmdline[: -len(MODE_SUFFIX)]
    if b"disable_skip_initramfs" not in rebuilt_cmdline:
        raise ValueError("required disable_skip_initramfs token is missing")
    if b"androidboot.mode=normal" in rebuilt_cmdline or len(rebuilt_cmdline) > 512:
        raise ValueError("unexpected command line")
    image[64:576] = rebuilt_cmdline + b"\0" * (512 - len(rebuilt_cmdline))

    kernel_offset = page_size
    ramdisk_offset = kernel_offset + align_up(kernel_size, page_size)
    second_offset = ramdisk_offset + align_up(ramdisk_size, page_size)
    if second_offset + second_size > len(image):
        raise ValueError("boot image components extend past end of donor")

    digest = hashlib.sha1()
    for offset, size in (
        (kernel_offset, kernel_size),
        (ramdisk_offset, ramdisk_size),
        (second_offset, second_size),
    ):
        digest.update(image[offset : offset + size])
        digest.update(struct.pack("<I", size))
    image[576:608] = digest.digest() + b"\0" * 12

    result = bytes(image)
    output_hash = hashlib.sha256(result).hexdigest()
    if len(result) != OUTPUT_SIZE or output_hash != OUTPUT_SHA256:
        raise ValueError(
            f"rebuilt output mismatch: size={len(result)}, SHA-256={output_hash}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="verified twrp-normal-mode.img donor")
    parser.add_argument("output", type=Path, help="new output path; must not exist")
    args = parser.parse_args()

    try:
        result = rebuild(args.source)
        with args.output.open("xb") as output:
            output.write(result)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"created: {args.output}")
    print(f"size: {len(result)}")
    print(f"sha256: {hashlib.sha256(result).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
