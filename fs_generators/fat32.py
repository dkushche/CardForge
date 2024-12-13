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
    target_dir = f"{source_dir}/fat32"

    with tempfile.TemporaryDirectory() as temp_dir:
        image_name = f"{partition_name}.image"
        image_path = f"{temp_dir}/{image_name}"

        lib.image_utils.generate_empty_image(image_path, sector_size, sectors)

        subprocess.run(
            [
                "mkfs.vfat", "-F16", "-S", sector_size, image_path
            ], check=True
        )

        for root, dirs, files in os.walk(target_dir):
            for file in files:
                print(f"Copying: {root[len(target_dir):]}/{file}")
                subprocess.run(
                    [
                        "mcopy", "-i", image_path, f"{root}/{file}", f"::{root[len(target_dir):]}/{file}"
                    ], check=True
                )

            for folder in dirs:
                subprocess.run(
                    [
                        "mmd", "-i", image_path, f"::{root[len(target_dir):]}/{folder}"
                    ], check=True
                )

        subprocess.run(["fatlabel", image_path, partition_name], check=True)

        shutil.move(image_path, f"{source_dir}/{image_name}")


if __name__ == "__main__":
    pack(*sys.argv[1:])
