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
        image_path = f"{temp_dir}/{image_name}"

        lib.image_utils.generate_empty_image(image_path, sector_size, sectors)

        subprocess.run(
            [
                "mkfs.ext4", "-L", partition_name, "-O", "^metadata_csum", image_path
            ]
        )

        debugfs_cmd_file_path = os.path.join(temp_dir, "debugfs_cmds.txt")
        with open(debugfs_cmd_file_path, mode='w', encoding='utf-8') as debugfs_cmd_fd:
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    print(f"Copying: {root[len(target_dir):]}/{file}")
                    debugfs_cmd_fd.write(f"write {root}/{file} {root[len(target_dir):]}/{file}\n")

                for folder in dirs:
                    debugfs_cmd_fd.write(f"mkdir {root[len(target_dir):]}/{folder}\n")

        subprocess.run(
            [
                "debugfs", "-w", "-f", debugfs_cmd_file_path, image_path
            ], check=True
        )

        shutil.move(image_path, f"{source_dir}/{image_name}")


if __name__ == "__main__":
    pack(*sys.argv[1:])
