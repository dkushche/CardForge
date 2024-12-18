import math

STORAGE_NAME: str = "card-forge.image"
DEFAULT_SECTOR_SIZE = 512
STORAGE_ALIGNMENT_SECTORS: int = 2048
MINIMAL_FAT16_SECTORS: int = 65527


class StorageEntity:
    sector_size: int = DEFAULT_SECTOR_SIZE

    def __init__(self, start_sector: int, size_sectors: int) -> None:
        self.start_sector = start_sector
        self.end_sector = start_sector + size_sectors - 1
        self.size_sectors = size_sectors

        self.start_bytes = self.start_sector * StorageEntity.sector_size
        self.size_bytes = self.size_sectors * StorageEntity.sector_size

    def __radd__(self, other: int) -> int:
        return other + self.size_sectors


class Alignment(StorageEntity):

    def __init__(self, start_sector: int, size_sectors: int = STORAGE_ALIGNMENT_SECTORS):
        super().__init__(start_sector, size_sectors)


class Partition(StorageEntity):
    def __init__(self, name: str, start_sector: int, size_sectors: int, partition_type: str):
        super().__init__(start_sector, size_sectors)
        self.name = name
        self.partition_type = partition_type

    def set_idx(self, idx: int):
        self.device = f"{STORAGE_NAME}{idx}"


class InPlacePartition(Partition):

    def __init__(self,
        name: str, start_sector: int,
        min_size_in_bytes: int, partition_type: str, fs_generation_handler: str
    ):
        self.fs_generation_handler = fs_generation_handler

        size_sectors = math.ceil(min_size_in_bytes / StorageEntity.sector_size)

        if self.fs_generation_handler == "fat16":
            if size_sectors < MINIMAL_FAT16_SECTORS:
                size_sectors = MINIMAL_FAT16_SECTORS

        end_sector_alignment = math.ceil(
            (start_sector + size_sectors) / STORAGE_ALIGNMENT_SECTORS
        ) * STORAGE_ALIGNMENT_SECTORS

        size_sectors = end_sector_alignment - start_sector

        super().__init__(name, start_sector, size_sectors, partition_type)


class ExtendedPartition(Partition):

    def __init__(self, name: str, start_sector: int, end_sector: int) -> None:
        size_sectors = end_sector - start_sector

        super().__init__(name, start_sector, size_sectors, "5")
