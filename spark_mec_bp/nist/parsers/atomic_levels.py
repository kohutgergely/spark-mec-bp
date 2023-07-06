from spark_mec_bp.nist.fetchers import AtomicLevelsData
import pandas as pd
from io import StringIO


class AtomicLevelsParser:
    def parse_atomic_levels(self, atomic_levels_data: AtomicLevelsData) -> pd.DataFrame:
        return self._read_level_to_dataframe(atomic_levels_data.data)

    def parse_partition_function(self, atomic_levels_data: AtomicLevelsData) -> float:
        return self._read_partition_function(atomic_levels_data.data)

    def _read_level_to_dataframe(self, data: str) -> pd.DataFrame:
        return (
            pd.read_csv(StringIO(data), sep="\t", index_col=False)
            .iloc[:-1, :]
            .infer_objects()
        )

    def _read_partition_function(self, atomic_levels_data: str) -> float:
        partition_function_row = atomic_levels_data.split("\n")[-2]
        return float(partition_function_row.split(" ")[-1])
