from io import StringIO

import pandas as pd

from spark_mec_bp.nist.fetchers import AtomicLevelsData


class AtomicLevelsParser:
    def parse_atomic_levels(self, atomic_levels_data: AtomicLevelsData) -> pd.DataFrame:
        return self._read_level_to_dataframe(atomic_levels_data.data)

    def parse_partition_function(self, atomic_levels_data: AtomicLevelsData) -> float:
        return self._read_partition_function(atomic_levels_data.data)

    def _read_level_to_dataframe(self, data: str) -> pd.DataFrame:
        return (
            pd.read_csv(StringIO(data), sep="\t", index_col=False)
            .iloc[:-1, :]
        )

    def _read_partition_function(self, atomic_levels_data: str) -> float:
        for dataline in StringIO(atomic_levels_data).readlines():
            striped_dataline = dataline.strip().lower()
            if striped_dataline.startswith("partition function"):
                return float(striped_dataline.split(" ")[-1])
