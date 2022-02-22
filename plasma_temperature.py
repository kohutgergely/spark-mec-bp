import numpy as np
from numpy import genfromtxt
from matplotlib import pyplot as plt
import lib.helper_functions as helper_functions
import pandas as pd
import scipy.stats

###Constants###
m = 9.10938291E-28  # g
k = 1.3807E-16  # cm2 g s-2 K-1
h = 6.6261E-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458E10  # cm/s

X = (2 * np.pi * m * k) / np.power(h, 2)  # constant in Saha-Boltzmann equation

conv = 11604.525

Ionization_Cu = np.array([62319.056, 163673.02, 297149.56])

Cu = np.array([[1.08605, 8.66998, -18.3398, 15.77519, -2.11931],
               [1.28222, -2.77724, 5.89866, -3.161, 1.00284],
               [5.62783, 8.5162, -7.8181, 3.38896, -0.5737]])


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def rsquare(x, y, f):
    y_mean = np.mean(y)
    SS_tot = np.sum(np.power(y - y_mean, 2))
    SS_res = np.sum(np.power(y - f, 2))
    R2 = 1 - SS_res / SS_tot
    return R2


def spec_data(peak_table, integrals_with_constants):
    peak_data = np.zeros((peak_table.size, 6))
    for i in range(0, peak_table.size):
        idx = find_nearest(integrals_with_constants[:, 0], peak_table[i])
        peak_data[i, 0] = integrals_with_constants[idx, 0]  # wavelength of selected line
        peak_data[i, 1] = integrals_with_constants[idx, 1]  # NIST wavelength of the selected line
        peak_data[i, 2] = integrals_with_constants[idx, 2]  # Aki
        peak_data[i, 3] = integrals_with_constants[idx, 3]  # gi
        peak_data[i, 4] = integrals_with_constants[idx, 4]  # Ei
        peak_data[i, 5] = integrals_with_constants[idx, 5]  # integral of the selected line
    return peak_data


def BPlot(peak_table, integrals_with_constants):
    peak_data = spec_data(peak_table, integrals_with_constants)
    ln = np.log(np.divide(np.multiply(peak_data[:, 5], peak_data[:, 1] * 1E-7),
                          np.multiply(h * c * peak_data[:, 3], peak_data[:, 2])))
    E = peak_data[:, 4]
    print(np.stack((E, ln), axis=-1))
    return np.stack((E, ln), axis=-1)


def T_fit(plot):
    E = plot[:, 0]
    ln = plot[:, 1]
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(E, ln)
    T = np.abs(-1 / (0.695035 * slope))
    n = np.exp(intercept)
    return np.array([T, n, r_value**2])


def atom_ion_ratio(ne, T, atom_peak_table, ion_peak_table, integrals_with_constants, Ionization):
    atomdata = spec_data(atom_peak_table, integrals_with_constants)
    iondata = spec_data(ion_peak_table, integrals_with_constants)
    ln_ratio = np.zeros((ion_peak_table.size, atom_peak_table.size))
    E_value = np.zeros((ion_peak_table.size, atom_peak_table.size))
    atom_ln = np.divide(np.multiply(atomdata[:, 5], atomdata[:, 1] * 1E-7),
                        np.multiply(h * c * atomdata[:, 3], atomdata[:, 2]))
    ion_ln = (
        np.divide(np.multiply(iondata[:, 5], iondata[:, 1] * 1E-7), np.multiply(h * c * iondata[:, 3], iondata[:, 2])))

    for i in range(0, ion_peak_table.size):
        ln_ratio[i, :] = np.log(np.divide(ion_ln[i], atom_ln))
        E_value[i, :] = np.subtract(iondata[i, 4] + Ionization, atomdata[:, 4])

    ln_ratios = np.reshape(ln_ratio, atom_peak_table.size * ion_peak_table.size)
    E_values = np.reshape(E_value, atom_peak_table.size * ion_peak_table.size)

    return np.stack((E_values, ln_ratios), axis=-1)


def SBPlot_classic(ne, T, atom_peak_table, ion_peak_table, integrals_with_constants, Ionization):
    atomdata = spec_data(atom_peak_table, integrals_with_constants)
    iondata = spec_data(ion_peak_table, integrals_with_constants)
    ln_atom = np.log(np.divide(np.multiply(atomdata[:, 5], atomdata[:, 1] * 1E-7),
                               np.multiply(h * c * atomdata[:, 3], atomdata[:, 2])))
    ln_ion = np.log(np.divide(np.multiply(iondata[:, 5], iondata[:, 1] * 1E-7),
                              np.multiply(h * c * iondata[:, 3], iondata[:, 2]))) - np.log(
        2 * np.power(X, 1.5) * np.divide(np.power(T, 1.5), ne))
    ln = np.concatenate((ln_atom, ln_ion))
    E = np.concatenate((atomdata[:, 4], iondata[:, 4] + Ionization))
    return np.stack((E, ln), axis=-1)


def SBLP(ne_init, T_init, atom_peak_table, ion_peak_table, integrals_with_constants, Ionization, max_iter, T_tolerance,
         ne_tolerance):
    T_values = np.zeros(max_iter)
    ne_values = np.zeros(max_iter)
    T_values[0] = T_init
    ne_values[0] = ne_init
    i = 0
    plot = atom_ion_ratio(ne_values[i], T_values[i], atom_peak_table, ion_peak_table, integrals_with_constants,
                          Ionization)
    T = T_fit(plot)[0]
    ne = np.divide(2 * np.power(X * T, 1.5), T_fit(plot)[1])

    diff_T = np.abs(T - T_values[i]) / T
    diff_ne = np.abs(ne - ne_values[i]) / ne

    while diff_T >= T_tolerance and diff_ne >= ne_tolerance:
        plot = atom_ion_ratio(ne_values[i], T_values[i], atom_peak_table, ion_peak_table, integrals_with_constants,
                              Ionization)
        T = T_fit(plot)[0]
        ne = np.divide(2 * np.power(X * T, 1.5), T_fit(plot)[1])
        diff_T = np.abs(T - T_values[i]) / T
        diff_ne = np.abs(ne - ne_values[i]) / ne
        i = i + 1
        T_values[i] = T
        ne_values[i] = ne
        print(T, ne)

    R2 = T_fit(plot)[2]

    return np.array([T, ne, R2])

def BPlot2(peak_table, integrals_with_constants):
    peak_data = helper_functions.find_constants_closest_to_values(peak_table, integrals_with_constants).to_numpy()
    ln = np.log(np.divide(np.multiply(peak_data[:, 5], peak_data[:, 1] * 1E-7),
                          np.multiply(h * c * peak_data[:, 3], peak_data[:, 2])))
    E = peak_data[:, 4]
    return E, ln

def calculate_boltzmann_plot_params(species: list, integrals_with_constants: pd.DataFrame):
    species_series = pd.Series(species, name="selected_wavelengths")
    E, ln = BPlot2(species_series, integrals_with_constants)
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(E, ln)
    T = np.abs(-1 / (0.695035 * slope))
    n = np.exp(intercept)
    return np.array([T, n, r_value**2])

def main(config):
    if config["enabled"]:
        integrals_with_constants = pd.read_csv((config["input_filename"]), sep="\s+",
                                               names=["exp_wl(nm)", "obs_wl_air(nm)", "Aki(s^-1)", "g_k", "Ek(cm-1)",
                                                      "intensity"])
        CuI_species = [465.11, 510.55, 515.32, 521.82]
        BPlot_CuI_results = calculate_boltzmann_plot_params(CuI_species, integrals_with_constants)
        print(BPlot_CuI_results)




        # CuI_species = np.array([465.11, 510.55, 515.32, 521.82])
        # integrals_with_constants = genfromtxt("AuAgCu_15-15-70_2eV_1E19_10000res_integrals_with_constants" + ".txt")
        # BPlot_CuI = BPlot(CuI_species, integrals_with_constants)
        # BPlot_CuI_results = T_fit(BPlot_CuI)
        # print(BPlot_CuI)
        # BPlot_CuI_fit = np.polyfit(BPlot_CuI[:, 0], BPlot_CuI[:, 1], 1)
        # print('Temperature from Boltzmann plot of Cu I lines:', BPlot_CuI_results[0], 'K', 'with an R2:',
        #       BPlot_CuI_results[2])
        #
        # plt.plot(BPlot_CuI[:, 0], BPlot_CuI[:, 1], "o")
        # plt.plot(BPlot_CuI[:, 0], BPlot_CuI[:, 0] * BPlot_CuI_fit[0] + BPlot_CuI_fit[1])
        # plt.xlabel('Upper energy level (cm-1)')
        # plt.ylabel('log of line intensity (a.u.)')
        # plt.title('Classical Boltzmann plot of Cu I lines')
        # plt.figure()


if __name__ == "__main__":
    config = helper_functions.read_config_file("config.yaml")
    main(config["plasma_temperature"])

# ###Cu II Boltzmann plot###
# CuII_species = np.array([495.36, 512.18, 518.34])
# BPlot_CuII = BPlot(CuII_species, integrals_with_constants)
# BPlot_CuII_results = T_fit(BPlot_CuII)
# BPlot_CuII_fit = np.polyfit(BPlot_CuII[:,0], BPlot_CuII[:,1], 1)
# print('Temperature from Boltzmann plot of Cu II lines:', BPlot_CuII_results[0], 'K', 'with an R2:', BPlot_CuII_results[2])
#
# plt.plot(BPlot_CuII[:,0], BPlot_CuII[:,1], "o")
# plt.plot(BPlot_CuII[:,0], BPlot_CuII[:,0]*BPlot_CuII_fit[0]+BPlot_CuII_fit[1])
# plt.xlabel('Upper energy level (cm-1)')
# plt.ylabel('log of line intensity (a.u.)')
# plt.title('Classical Boltzmann plot of Cu II lines')
# plt.figure()
#
# ###Saha-Boltzmann line-pair plot Cu I/Cu II###
# ne_init = 1E18 #initial value for electron concentration calculation
# T_init = 20000 #initial value for temperature calculation
# SBLP_Cu_results = SBLP(ne_init, T_init, CuI_species, CuII_species, integrals_with_constants, Ionization_Cu[0], 100, 1E-3, 1E-3) #results of the SB line-pCui method
# SBLP_Cu_graph = atom_ion_ratio(SBLP_Cu_results[1], SBLP_Cu_results[0], CuI_species, CuII_species, integrals_with_constants, Ionization_Cu[0])
# SBLP_Cu_fit = np.polyfit(SBLP_Cu_graph[:,0], SBLP_Cu_graph[:,1], 1)
# print('The Saha-Boltzmann line-pair method resulted in an electron concetration of', SBLP_Cu_results[1]/1E16, '*1E16 cm-3', 'and a temperature of', SBLP_Cu_results[0], 'K', 'with an R2:', SBLP_Cu_results[2], 'for the Cu lines')
# plt.plot(SBLP_Cu_graph[:,0], SBLP_Cu_graph[:,1], "x")
# plt.plot(SBLP_Cu_graph[:,0], SBLP_Cu_graph[:,0]*SBLP_Cu_fit[0]+SBLP_Cu_fit[1])
# plt.xlabel('DifCurence of upper energy levels (cm-1)')
# plt.ylabel('log of line intensity ratios (a.u.)')
# plt.title('Saha-Boltzmann line-pair plot for Cu II and Cu I lines')
# plt.figure()
