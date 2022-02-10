from adapters.nist_spectrum_level_adapter import SpectrumLevelData
from adapters.nist_ionization_energy_adapter import IonizationEnergyData
from io import StringIO
import pandas as pd

def get_partition_function(spectrum_level_data: SpectrumLevelData) -> float:
    partition_function_raw_line = spectrum_level_data.data.split("\n")[-2]
    partition_function_value = float(partition_function_raw_line.split()[-1])

    return partition_function_value


def get_ionization_energy(spectrum, ionization_energy_data: IonizationEnergyData):
    ionization_energy_df = pd.read_csv(StringIO(ionization_energy_data.data), sep="\t")
    return float(ionization_energy_df[ionization_energy_df['Sp. Name'] == spectrum]['Ionization Energy (eV)'])