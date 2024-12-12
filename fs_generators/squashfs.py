#!/usr/bin/env python3

import os
import sys
import subprocess

def pack(partition_name: str, sector_size: str, sectors: str, source_dir: str):
    source_dir = source_dir.rstrip("/")
    image = f"{source_dir}.image.squashfs"

    subprocess.call(
        [
            "mksquashfs", source_dir, image,
            "-all-root", "-nopad",  "-noappend", "-b", "256K", "-comp", "xz",
            "-p", "/dev d 755 0 0",
            "-p", "/dev/console c 600 0 0 5 1"
        ], check=True
    )


if __name__ == "__main__":
    pack(*sys.argv[1:])
