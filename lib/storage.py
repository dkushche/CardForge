import copy
import typing

import lib.base_storage_entities


class Storage(list):
    def __init__(self, sector_size, size_bytes):
        super().__init__()

        self.sector: int = 0
        self.idx = copy.deepcopy(self.START_ID)

        self.size_bytes: int = size_bytes
        self.size_sectors: int = size_bytes // sector_size

        lib.base_storage_entities.StorageEntity.sector_size = sector_size

    def validate_partition_type(self, partition_type: str):
        valid_types = typing.get_args(self.partition_t)
        if partition_type not in valid_types:
            raise ValueError(f"Invalid partition_type: {partition_type}. Must be one of {valid_types}")

    def add_item(self, item: lib.base_storage_entities.StorageEntity):
        self.sector = self.sector + item
        if self.sector > self.size_sectors:
            raise ValueError(f"Ran out of space {item=}")

        super().append(item)
