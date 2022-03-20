#%%
import numpy as np
from numpy import genfromtxt
from matplotlib import pyplot as plt
import lib.helper_functions as helper_functions
import pandas as pd
import scipy.stats
import logging

###Constants###
m = 9.10938291E-28  # g
k = 1.3807E-16  # cm2 g s-2 K-1
h = 6.6261E-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458E10  # cm/s
X = (2 * np.pi * m * k) / np.power(h, 2)  # constant in Saha-Boltzmann equation



def prepare_saha_boltzmann_plot(species_name, atom_peak_table, ion_peak_table, integrals_with_constants, ionization, plot=True):
    E, ln = get_atom_ion_ratio(atom_peak_table, ion_peak_table, integrals_with_constants, ionization)
    slope, intercept, r_value = fit_boltzmann_parameters(E, ln)
    T = get_temperature_from_boltzmann_plot(slope)
    ne = np.divide(2 * np.power(X * T, 1.5), get_concentration_from_boltzmann_plot(intercept))
    logging.info(f"The Saha-Boltzmann line-pair method resulted in an electron concetration of {ne/1E16}*1E16 cm-3 and a temperature of {T} K with an R2: {r_value**2} for the {species_name} lines")
    if plot:
        plot_saha_boltzmann_parameters("Cu", E, ln, slope, intercept)
    return T, ne, r_value**2

def get_atom_ion_ratio(atom_peak_table, ion_peak_table, integrals_with_constants, ionization):
    atomdata = helper_functions.find_constants_closest_to_values(pd.Series(atom_peak_table), integrals_with_constants).to_numpy()
    iondata = helper_functions.find_constants_closest_to_values(pd.Series(ion_peak_table), integrals_with_constants).to_numpy()
    atom_raw_y = get_boltzmann_plot_raw_y(atomdata)
    ion_raw_y = get_boltzmann_plot_raw_y(iondata)
    ln_ratios = get_ln_boltzmann_ratios(atom_raw_y, ion_raw_y)
    E_values = get_energy_differences(atomdata, iondata, ionization)
    return E_values, ln_ratios

def get_ln_boltzmann_ratios(atom_ln, ion_ln):
    return np.log(
        np.divide(ion_ln[:, np.newaxis], atom_ln)
    ).reshape(-1)

def get_energy_differences(atomdata, iondata, ionization):
    return np.subtract(iondata[:, 4][:, np.newaxis] + ionization, atomdata[:, 4]).reshape(-1)

def plot_saha_boltzmann_parameters(species_name: str, E: float, ln: float, slope: float, intercept: float):
    plt.plot(E, ln, "o")
    plt.plot(E, E * slope + intercept)
    plt.xlabel('DifCurence of upper energy levels (cm-1)')
    plt.ylabel('log of line intensity ratios (a.u.)')
    plt.title(F'Saha-Boltzmann line-pair plot for {species_name} lines')
    plt.figure()

def prepare_boltzmann_plot(species_name: str, traget_lines: list, integrals_with_constants: pd.DataFrame, plot=True):
    E, ln = get_boltzmann_fit_parameters(traget_lines, integrals_with_constants)
    slope, intercept, r_square = fit_boltzmann_parameters(E, ln)
    T = get_temperature_from_boltzmann_plot(slope)
    n = get_concentration_from_boltzmann_plot(intercept)
    logging.info(f"Temperature from Boltzmann plot of {species_name} lines: {T:10.6f} K with an R2: {r_square:10.6f}")
    if plot:
        plot_boltzmann_parameters(species_name, E, ln, slope, intercept)

def get_boltzmann_fit_parameters(target_lines: list, integrals_with_constants: pd.DataFrame):
    atomdata = helper_functions.find_constants_closest_to_values(pd.Series(target_lines), integrals_with_constants).to_numpy()
    ln = np.log(get_boltzmann_plot_raw_y(atomdata))
    E = atomdata[:, 4]
    return E, ln

def get_boltzmann_plot_raw_y(atomdata):
    return np.divide(np.multiply(atomdata[:, 5], atomdata[:, 1] * 1E-7),
                        np.multiply(h * c * atomdata[:, 3], atomdata[:, 2]))

def fit_boltzmann_parameters(E: float, ln: float):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(E, ln)
    return slope, intercept, r_value**2

def get_temperature_from_boltzmann_plot(boltzmann_plot_slope):
    return np.abs(-1 / (0.695035 * boltzmann_plot_slope))

def get_concentration_from_boltzmann_plot(boltzmann_plot_intercept):
    return np.exp(boltzmann_plot_intercept)

def plot_boltzmann_parameters(species_name: str, E: float, ln: float, slope: float, intercept: float):
    plt.plot(E, ln, "o")
    plt.plot(E, E * slope + intercept)
    plt.xlabel('Upper energy level (cm-1)')
    plt.ylabel('log of line intensity (a.u.)')
    plt.title(f'Classical Boltzmann plot of {species_name} lines')
    plt.figure()

def main(config):
    if config["enabled"]:
        target_lines = config["target_lines"]
        integrals_with_constants = pd.read_csv((config["input_filename"]), sep="\s+",
                                               names=["exp_wl(nm)", "obs_wl_air(nm)", "Aki(s^-1)", "g_k", "Ek(cm-1)",
                                                      "intensity"])
        prepare_boltzmann_plot(list(target_lines.keys())[0], target_lines[list(target_lines.keys())[0]], integrals_with_constants)
        prepare_boltzmann_plot(list(target_lines.keys())[1], target_lines[list(target_lines.keys())[1]], integrals_with_constants)
        ionization_energy = helper_functions.get_ionization_energy(config["ionization_energy"])
        prepare_saha_boltzmann_plot(config["species_name"], target_lines[list(target_lines.keys())[0]], target_lines[list(target_lines.keys())[1]], integrals_with_constants, ionization_energy)

if __name__ == "__main__":
    config = helper_functions.read_config_file("config.yaml")
    main(config["plasma_temperature"])
