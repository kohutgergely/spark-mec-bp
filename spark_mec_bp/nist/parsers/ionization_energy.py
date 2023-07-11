from spark_mec_bp.nist.fetchers import IonizationEnergyData
import pandas as pd
from io import StringIO


class IonizationEnergyParser:
    def parse_ionization_energy(
        self, ionization_energy_data: IonizationEnergyData
    ) -> pd.DataFrame:
        return self._read_ionization_energy_to_dataframe(ionization_energy_data.data)

    def _read_ionization_energy_to_dataframe(
        self, ionization_energy_data: str
    ) -> pd.DataFrame:
        return (
            pd.read_csv(StringIO(ionization_energy_data), sep="\t", index_col=False)
            .iloc[:-3, :-1]
            .infer_objects()
        )
