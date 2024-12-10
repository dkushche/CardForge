import string

import lib.base_storage_entities
import lib.storage

class ConfigurationsGenerator:

    def __init__(self, complete_layout: lib.storage.Storage, layout_path_no_ext: str):
        self.complete_layout = complete_layout
        self.layout_path_no_ext = layout_path_no_ext

    def _iface_fsdisk_layout(self):
        with open("layout.template") as layout_template_fd:
            layout_template = string.Template(layout_template_fd.read())

        partitions = ""
        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.Partition):
                partitions += f"{partition.device} : start={partition.start_sector}, size={partition.size_sectors}, type={partition.partition_type}\n"

        with open(self.layout_path_no_ext, mode="w") as layout_fd:
            layout_fd.write(
                layout_template.substitute(
                    label=self.complete_layout.label,
                    device_name=lib.base_storage_entities.STORAGE_NAME,
                    sector_size=lib.base_storage_entities.StorageEntity.sector_size,
                    partitions=partitions
                )
            )

    def _iface_env_file(self):
        idx = 0

        with open(f"{self.layout_path_no_ext}_env", mode="w") as layout_fd:
            layout_fd.write(f"IMAGE_NAME={lib.base_storage_entities.STORAGE_NAME}\n")
            layout_fd.write(f"IMAGE_BLOCKS={self.complete_layout.sector}\n")
            layout_fd.write(f"BLOCK_SIZE={lib.base_storage_entities.StorageEntity.sector_size}\n")

            for partition in self.complete_layout:
                if isinstance(partition, lib.base_storage_entities.Partition):
                    idx += 1
                    layout_fd.write(f"{partition.name.upper()}_PARTITION_ID={idx}\n")
                    layout_fd.write(f"{partition.name.upper()}_START={partition.start_sector}\n")
                    layout_fd.write(f"{partition.name.upper()}_SECTORS={partition.size_sectors}\n")

    def _iface_uboot_env_file(self):
        idx = 0
        mbr_parts = ""

        with open(f"{self.layout_path_no_ext}_uboot_env", mode="w") as layout_fd:
            for partition in self.complete_layout:
                if isinstance(partition, lib.base_storage_entities.Partition):
                    idx += 1
                    layout_fd.write(f"{partition.name}_partition_id={idx}\n")

                    mbr_parts += f"name={partition.name},start={partition.start_bytes},size={partition.size_bytes},"
                    partition_type_info = partition.partition_type.split(',')
                    partition_type = partition_type_info[0]
                    if len(partition_type_info) == 2:
                        assert "bootable" in partition_type_info[1]
                        mbr_parts += "bootable,"

                    mbr_parts += f"id={hex(int(partition_type, 16))};"
            layout_fd.write(f'mbr_parts={mbr_parts}')
