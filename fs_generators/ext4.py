#!/usr/bin/env python3

import os
import sys
import shutil
import tempfile
import subprocess

import lib.image_utils


def pack(source_dir: str, sector_size: str, sectors: str):
    partition_name = os.path.basename(source_dir)
    source_dir = source_dir.rstrip("/")
    target_dir = f"{source_dir}/ext4"

    if not os.path.exists(target_dir):
        raise TypeError(f"{target_dir=} not found")

    with tempfile.TemporaryDirectory() as temp_dir:
        image_name = f"{partition_name}.image"
        image_path = f"{source_dir}/{image_name}"

        lib.image_utils.generate_empty_image(image_path, sector_size, sectors)

        subprocess.run(
            [
                "mkfs.ext4", "-L", partition_name, "-O", "^metadata_csum",
                "-d", target_dir, image_path
            ]
        )


if __name__ == "__main__":
    pack(*sys.argv[1:])
