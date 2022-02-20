from operator import index
import re
from urllib import request
from adapters.nist_spectrum_level_adapter import SpectrumLevelData
from adapters.nist_ionization_energy_adapter import IonizationEnergyData
from adapters.nist_spectrum_line_adapter import SpectrumLineAdapter
from configs.nist_spectrum_line_adapter_config import SpectrumLineAdapterConfig
from io import StringIO

import yaml
import pandas as pd
import numpy as np


def get_partition_function(spectrum_level_data: SpectrumLevelData) -> float:
    partition_function_raw_line = spectrum_level_data.data.split("\n")[-2]
    partition_function_value = float(partition_function_raw_line.split()[-1])

    return partition_function_value

def get_ionization_energy(spectrum, ionization_energy_data: IonizationEnergyData):
    ionization_energy_df = pd.read_csv(StringIO(ionization_energy_data.data), sep="\t")
    return float(ionization_energy_df[ionization_energy_df['Sp. Name'] == spectrum]['Ionization Energy (eV)'])

def read_config_file(config_file: str) -> dict:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

def gather_nist_data(species, upper_wavelength, lower_wavelength):
    spectrum_line_config = SpectrumLineAdapterConfig()
    spectrum_line_adapter = SpectrumLineAdapter(spectrum_line_config)
    requested_spectrum = spectrum_line_adapter.request_data(
    spectrum=species,
    lower_wavelength=lower_wavelength,
    upper_wavelength=upper_wavelength)
    return pd.read_csv(StringIO(requested_spectrum.data), sep="\t", index_col=False, usecols=[2,3,6,8])

def _find_constants_closest_to_experimental_wavelength(experimental_wavelength, constants):
    index_of_wavelength_closest_to_experimental = constants.iloc[:,0].sub(experimental_wavelength).abs().argmin()
    return constants.iloc[index_of_wavelength_closest_to_experimental,:]

def merge_constants_and_integrals(constants: pd.DataFrame, integrals: pd.DataFrame):
    filtered_constants = integrals.iloc[:,0].apply(lambda exp_wavelength: _find_constants_closest_to_experimental_wavelength(exp_wavelength, constants))
    merged_and_reordered_data = pd.concat([integrals,filtered_constants], axis=1).iloc[:,[0, 2, 3, 5, 4, 1]]
    return merged_and_reordered_data
