import typing

import lib.storage
import lib.base_storage_entities

class Storage(lib.storage.Storage):
    partition_t = typing.Literal["primary", "logical", "none"]

    START_ID: dict[partition_t, int] = {
        "primary": 1,
        "logical": 5,
    }

    MAX_ID: dict[partition_t, int] = {
        "primary": 4,
        "logical": 29,
    }

    def __init__(self, sector_size, size_bytes):
        super().__init__(sector_size, size_bytes)

        self.label = "dos"
        self.contains_extended: bool = False

    def append(self, item: lib.base_storage_entities.StorageEntity, partition_type: partition_t):
        self.validate_partition_type(partition_type)

        if partition_type != "none":
            if self.idx[partition_type] > self.MAX_ID[partition_type]:
                raise TypeError(f"It's to much {partition_type} partitions")

            item.set_idx(self.idx[partition_type])

            self.idx[partition_type] += 1

        if isinstance(item, lib.base_storage_entities.ExtendedPartition):
            if self.contains_extended is True:
                raise TypeError("It can't be more then one extended partition for MBR")

            self.contains_extended = True
            super().insert((self.START_ID["logical"] - self.idx["logical"]) * 2, item)
        else:
            self.add_item(item)


    def calculate(self, partitions: dict):
        self.append(
            lib.base_storage_entities.Alignment(self.sector),
            "none"
        )

        for name, partition_info in partitions.items():
            print(f"Processing partition: {name}")

            match partition_info:
                case list():
                    extended_partition_start_block = self.sector

                    for logical_partition in partition_info:
                        for logical_partition_name, logical_partition_info in logical_partition.items():
                            print(f"Processing logical partition: {logical_partition_name}")

                            self.append(
                                lib.base_storage_entities.Alignment(self.sector),
                                "none"
                            )
                            self.append(
                                lib.base_storage_entities.InPlacePartition(
                                    logical_partition_name, start_sector=self.sector,
                                    **logical_partition_info
                                ),
                                "logical"
                            )

                    self.append(
                        lib.base_storage_entities.ExtendedPartition(
                            name, extended_partition_start_block, self.sector
                        ),
                        "primary"
                    )

                case dict():
                    self.append(
                        lib.base_storage_entities.InPlacePartition(
                            name, start_sector=self.sector, **partition_info
                        ),
                        "primary"
                    )
