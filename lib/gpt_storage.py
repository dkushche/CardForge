import typing

import lib.storage
import lib.base_storage_entities

class Storage(lib.storage.Storage):
    partition_t = typing.Literal["primary", "none"]

    START_ID: dict[partition_t, int] = {
        "primary": 1,
    }

    MAX_ID: dict[partition_t, int] = {
        "primary": 128,
    }

    def __init__(self, sector_size, size_bytes):
        super().__init__(sector_size, size_bytes)

        self.label = "gpt"

    def append(self, item: lib.base_storage_entities.StorageEntity, partition_type: partition_t):
        self.validate_partition_type(partition_type)

        if partition_type != "none":
            if self.idx[partition_type] > self.MAX_ID[partition_type]:
                raise TypeError(f"It's to much {partition_type} partitions")

            item.set_idx(self.idx[partition_type])
            self.idx[partition_type] += 1

        if isinstance(item, lib.base_storage_entities.ExtendedPartition):
            raise TypeError("GPT doesn't support ExtendedPartitions")
        
        self.add_item(item)
