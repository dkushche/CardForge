import math

STORAGE_NAME: str = "card-forge.img"
DEFAULT_SECTOR_SIZE = 512
STORAGE_ALIGNMENT_SECTORS: int = 2048
MINIMAL_FAT32_SECTORS: int = 65527


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

    def __init__(self, start_sector: int):
        super().__init__(start_sector, STORAGE_ALIGNMENT_SECTORS)


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
        min_size_in_bytes: int, partition_type: str,
        fs_generator: str | None
    ):
        size_sectors = math.ceil(min_size_in_bytes / StorageEntity.sector_size)

        if partition_type.startswith("c"):
            if size_sectors < MINIMAL_FAT32_SECTORS:
                size_sectors = MINIMAL_FAT32_SECTORS

        end_sector_alignment = math.ceil(
            (start_sector + size_sectors) / STORAGE_ALIGNMENT_SECTORS
        ) * STORAGE_ALIGNMENT_SECTORS

        size_sectors = end_sector_alignment - start_sector

        self.fs_generator = fs_generator

        super().__init__(name, start_sector, size_sectors, partition_type)


class ExtendedPartition(Partition):

    def __init__(self, name: str, start_sector: int, end_sector: int) -> None:
        size_sectors = end_sector - start_sector

        super().__init__(name, start_sector, size_sectors, "5")
