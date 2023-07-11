from spark_mec_bp.nist.fetchers import IonizationEnergyData
import pandas as pd
from io import StringIO

END_OF_TABLE_STRING = "notes"


class IonizationEnergyParser:
    def parse_ionization_energy(
        self, ionization_energy_data: IonizationEnergyData
    ) -> pd.DataFrame:
        table_data = self._get_table(ionization_energy_data.data)
        return self._read_to_dataframe(table_data)

    def _get_table(self, ionization_energy_data):
        table_lines = []
        for line in StringIO(ionization_energy_data).readlines():
            if line.strip().lower().startswith(END_OF_TABLE_STRING):
                break
            table_lines.append(line)

        return "\n".join(table_lines)

    def _read_to_dataframe(self, table_data):
        return pd.read_csv(StringIO(table_data), sep="\t", index_col=False).iloc[:, :-1]
