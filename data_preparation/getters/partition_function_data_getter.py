from nist.fetchers import AtomicLevelsFetcher
from nist.parsers import AtomicLevelsParser

KELVIN_TO_ELECTRONVOLT_CONVERSION_FACTOR = 8.61732814974493E-05


class PartitionFunctionDataGetter:
    def __init__(self, atomic_levels_fetcher: AtomicLevelsFetcher, atomic_levels_parser: AtomicLevelsParser) -> None:
        self.atomic_levels_fetcher = atomic_levels_fetcher
        self.atomic_levels_parser = atomic_levels_parser

    def get_data(self, species_name: str, temperature: float):
        atomic_levels_data = self.atomic_levels_fetcher.fetch(
            species_name, temperature*KELVIN_TO_ELECTRONVOLT_CONVERSION_FACTOR)

        return self.atomic_levels_parser.parse_partition_function(atomic_levels_data)
