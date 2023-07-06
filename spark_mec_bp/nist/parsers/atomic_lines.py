from spark_mec_bp.nist.fetchers import AtomicLinesData
import pandas as pd
from io import StringIO


class AtomicLinesParser:
    def parse_atomic_lines(self, atomic_lines_data: AtomicLinesData) -> pd.DataFrame:
        return self._read_lines_to_dataframe(atomic_lines_data.data)

    def _read_lines_to_dataframe(self, atomic_lines_data: str) -> pd.DataFrame:
        return (
            pd.read_csv(StringIO(atomic_lines_data), sep="\t", index_col=False)
            .infer_objects()
            .iloc[:, :-1]
        )
