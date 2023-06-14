import numpy as np
import codecs

from nist_sdk.atomic_lines import AtomicLinesFetcher
from nist_sdk.atomic_levels import AtomicLevelsFetcher
from nist_sdk.ionization_energy import IonizationEnergyFetcher
from parsers.atomic_lines import AtomicLinesParser
from parsers.atomic_levels import AtomicLevelsParser
from parsers.ionization_energy import IonizationEnergyParser


def get_atomic_lines(spectrum: str, lower_wavelength: int, upper_wavelength: int):
    atomic_lines_data = AtomicLinesFetcher().fetch(
        spectrum, lower_wavelength, upper_wavelength)
    parsed_data = AtomicLinesParser().parse_atomic_lines(atomic_lines_data)
    filtered_data = parsed_data[[
        "obs_wl_air(nm)", "Aki(s^-1)", "Acc", "Ei(cm-1)", "Ek(cm-1)", "g_i", "g_k", "Type"]]

    return filtered_data[filtered_data["Aki(s^-1)"].notna()].to_numpy()


def get_partition_function(spectrum: str, temperature: int):
    KELVIN_TO_ELECTRONVOLT_CONVERSION_FACTOR = 8.61732814974493E-05

    atomic_levels_data = AtomicLevelsFetcher().fetch(
        spectrum, temperature*KELVIN_TO_ELECTRONVOLT_CONVERSION_FACTOR)

    return AtomicLevelsParser().parse_partition_function(atomic_levels_data)


def get_ionization_energy(spectrum: str):
    ionziation_energy_data = IonizationEnergyFetcher().fetch(spectrum)
    parsed_ionization_energy_data = IonizationEnergyParser(
    ).parse_ionziation_energy(ionziation_energy_data)

    return float(parsed_ionization_energy_data["Ionization Energy (1/cm)"].iloc[0])


def read_spectrum(file_name):
    with codecs.open(file_name, encoding='utf-8-sig') as f:
        spectrum = np.loadtxt(f)
    return np.stack((spectrum[:, 0], spectrum[:, 10]), axis=-1)
