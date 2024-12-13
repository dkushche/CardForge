import subprocess

def generate_empty_image(image_path: str, sector_size: str, sectors: str):
    subprocess.run(
        [
            "dd", "if=/dev/zero", f"of={image_path}", f"bs={sector_size}", f"count={sectors}"
        ], check=True
    )


def write_image_to_image(src_image: str, dest_image: str, sector_size: str, start: str):
    subprocess.run(
        [
            "dd",
            f"if={src_image}",
            f"of={dest_image}",
            f"bs={sector_size}",
            f"seek={start}",
            "conv=notrunc",
            "status=progress"
        ], check=True
    )


def create_partition_table(image_path: str, fdisk_layout_path: str):
    subprocess.run(
        [
            f"sfdisk {image_path} < {fdisk_layout_path}"
        ], check=True, shell=True
    )

    print(f"{image_path=} partition table:")
    subprocess.run(
        [
            "fdisk", "-l", image_path
        ], check=True
    )
