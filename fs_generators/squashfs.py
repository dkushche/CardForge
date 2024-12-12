#!/usr/bin/env python3

import os
import sys
import shutil
import tempfile
import subprocess

def pack(source_dir: str, sector_size: str = "0", sectors: str = "0"):
    partition_name = os.path.basename(source_dir)
    source_dir = source_dir.rstrip("/")
    target_dir = f"{source_dir}/squashfs"

    with tempfile.TemporaryDirectory() as temp_dir:
        image_name = f"{partition_name}.image"
        image_path = f"{temp_dir}/{image_name}"

        subprocess.run(
            [
                "mksquashfs", target_dir, image_path,
                "-all-root", "-nopad",  "-noappend", "-b", "256K", "-comp", "xz",
                "-p", "/dev d 755 0 0",
                "-p", "/dev/console c 600 0 0 5 1"
            ], check=True
        )

        shutil.move(image_path, f"{source_dir}/{image_name}")


if __name__ == "__main__":
    pack(*sys.argv[1:])
