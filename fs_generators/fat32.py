#!/usr/bin/env python3

import os
import sys
import subprocess

def pack(partition_name: str, sector_size: str, sectors: str, source_dir: str):
    source_dir = source_dir.rstrip("/")
    image = f"{source_dir}.image.vfat"

    subprocess.run(
        [
            "dd", "if=/dev/zero", f"of={image}", f"bs={sector_size}", f"count={sectors}"
        ], check=True
    )

    subprocess.run(
        [
            "mkfs.vfat", "-F16", "-S", sector_size, image
        ], check=True
    )

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            print(f"Copying: {root[len(source_dir):]}/{file}")
            subprocess.run(
                [
                    "mcopy", "-i", image, f"{root}/{file}", f"::{root[len(source_dir):]}/{file}"
                ], check=True
            )

        for folder in dirs:
            subprocess.run(
                [
                    "mmd", "-i", image, f"::{root[len(source_dir):]}/{folder}"
                ], check=True
            )

    subprocess.run(["fatlabel", image, partition_name], check=True)


if __name__ == "__main__":
    pack(*sys.argv[1:])
