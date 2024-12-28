import os
import string

import lib.base_storage_entities
import lib.storage

LAYOUT_TAMPLATE_PATH = "assets/fs_disk_layout.template"

PRECONFIG_RESULT_DIR = "preparation"
PRECONFIG_CONFIG_DIR = f"{PRECONFIG_RESULT_DIR}/configs"
PRECONFIG_PRATITIONS_DATA_DIR = f"{PRECONFIG_RESULT_DIR}/partitions_data"

FDISK_LAYOUT_FILENAME = "fdisk_layout"
ENV_CONFIG_FILENAME = "layout_env"
UBOOT_ENV_CONFIG_FILENAME = "layout_uboot_env"

class PreConfigurators:

    def __init__(self, complete_layout: lib.storage.Storage, out_dir: str):
        self.complete_layout = complete_layout

        self.config_output_dir = f"{out_dir}/{PRECONFIG_CONFIG_DIR}"
        os.makedirs(self.config_output_dir)

        self.partition_data_output_dir = f"{out_dir}/{PRECONFIG_PRATITIONS_DATA_DIR}"
        os.makedirs(self.partition_data_output_dir)

    def _iface_fsdisk_layout(self):
        with open(LAYOUT_TAMPLATE_PATH) as layout_template_fd:
            layout_template = string.Template(layout_template_fd.read())

        partitions = ""
        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.Partition):
                partition_info = ", ".join([
                    f"start={partition.start_sector}",
                    f"size={partition.size_sectors}",
                    f"type={partition.partition_type}",
                    f"name={partition.name}"
                ])
                partitions += f"{partition.device} : {partition_info}\n"

        with open(f"{self.config_output_dir}/{FDISK_LAYOUT_FILENAME}", mode="w") as layout_fd:
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

        with open(f"{self.config_output_dir}/{ENV_CONFIG_FILENAME}", mode="w") as layout_fd:
            layout_fd.write(f"IMAGE_NAME={lib.base_storage_entities.STORAGE_NAME}\n")
            layout_fd.write(f"IMAGE_BLOCKS={self.complete_layout.sector}\n")
            layout_fd.write(f"BLOCK_SIZE={lib.base_storage_entities.StorageEntity.sector_size}\n")

            for partition in self.complete_layout:
                if isinstance(partition, lib.base_storage_entities.Partition):
                    idx += 1
                    layout_fd.write(f"{partition.name.upper()}_PARTITION_ID={idx}\n")
                    layout_fd.write(f"{partition.name.upper()}_START={partition.start_sector}\n")
                    layout_fd.write(f"{partition.name.upper()}_SECTORS={partition.size_sectors}\n")

    def __uboot_base_env_file(self, layout_fd):
        idx = 0

        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.Partition):
                idx += 1
                layout_fd.write(f"{partition.name}_partition_id={idx}\n")

    def _iface_uboot_minimal_env_file(self):
        layout_fd = open(f"{self.config_output_dir}/{UBOOT_ENV_CONFIG_FILENAME}", mode="w")
        self.__uboot_base_env_file(layout_fd)
        layout_fd.close()

    def _iface_uboot_gpt_env_file(self):
        gpt_parts = ""

        layout_fd = open(f"{self.config_output_dir}/{UBOOT_ENV_CONFIG_FILENAME}", mode="w")
        self.__uboot_base_env_file(layout_fd)

        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.Partition):
                gpt_parts += f"name={partition.name},start={partition.start_bytes},size={partition.size_bytes},type={partition.partition_type};"

        layout_fd.write(f'gpt_parts={gpt_parts}\n')
        layout_fd.close()

    def _iface_uboot_mbr_env_file(self):
        mbr_parts = ""

        layout_fd = open(f"{self.config_output_dir}/{UBOOT_ENV_CONFIG_FILENAME}", mode="w")
        self.__uboot_base_env_file(layout_fd)

        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.Partition):
                mbr_parts += f"name={partition.name},start={partition.start_bytes},size={partition.size_bytes},"
                partition_type_info = partition.partition_type.split(',')
                partition_type = partition_type_info[0]
                if len(partition_type_info) == 2:
                    assert "bootable" in partition_type_info[1]
                    mbr_parts += "bootable,"

                mbr_parts += f"id={hex(int(partition_type, 16))};"

        layout_fd.write(f'mbr_parts={mbr_parts}\n')
        layout_fd.close()

    def _iface_directory_structure(self):
        for partition in self.complete_layout:
            if isinstance(partition, lib.base_storage_entities.InPlacePartition):
                partition_data_dir = f"{self.partition_data_output_dir}/{partition.name}"
                os.makedirs(partition_data_dir)

                if partition.fs_generation_handler is not None:
                    os.makedirs(f"{partition_data_dir}/{partition.fs_generation_handler}", exist_ok=True)
