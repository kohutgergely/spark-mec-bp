import numpy as np
from scipy.signal import find_peaks, peak_prominences
import scipy

from matplotlib import pyplot as plt

from lmfit.models import PseudoVoigtModel

from new_codebase.spectrum_correction import correct_spectrum, baseline_arPLS
from new_codebase.electron_conentration_estimation import estimate_electron_concentration, SB
from new_codebase.gather_data import get_atomic_lines, get_ionization_energy, get_partition_function, read_spectrum


def peakfinder(Y, height):
    peak_indices, _ = find_peaks(Y, height, threshold=0, width=2)
    return peak_indices


def integral(spectrum):
    X = spectrum[:, 0]
    Y = spectrum[:, 1]
    peaks = peakfinder(Y, height=set_height)
    prominences = peak_prominences(Y, peaks, wlen=set_wlen)
    left_base = prominences[1]
    right_base = prominences[2]
    integrals = np.zeros((X.size, 2))
    for i in range(0, left_base.size):
        peak_X = X[left_base[i]:right_base[i]:1]
        peak_Y = Y[left_base[i]:right_base[i]:1]
        peak_int = np.trapz(peak_Y, peak_X)
        integrals[i, 0] = X[peaks[i]]
        integrals[i, 1] = peak_int  # *(h*c/(X[peaks[i]]*1E-7))
    return integrals


def Voigt_integral(spectrum, selected_peak):
    wavelength = spectrum[:, 0]
    Y = spectrum[:, 1]
    all_peaks = np.stack((peakfinder(Y, height=set_height),
                         wavelength[peakfinder(Y, height=set_height)]), axis=-1)
    selected_peak_idx = find_nearest(all_peaks[:, 1], selected_peak)
    selected_peak_idx_array = np.array([int(all_peaks[selected_peak_idx, 0])])
    prominences = peak_prominences(Y, selected_peak_idx_array, wlen=set_wlen)
    start_index = int(prominences[1])
    end_index = 2*int(all_peaks[selected_peak_idx, 0])-int(prominences[1])
    # start_wavelength = wavelength[start_index]
    # end_wavelength = wavelength[end_index]
    peak_wavelength = wavelength[start_index:end_index+1]
    peak_spectrum = Y[start_index:end_index+1]
    voigt_model = PseudoVoigtModel()
    params = voigt_model.guess(peak_spectrum, x=peak_wavelength)
    voigt_fit = voigt_model.fit(peak_spectrum, params, x=peak_wavelength)
    plt.plot(peak_wavelength, peak_spectrum, 'o', label='Original spectrum')
    plt.plot(peak_wavelength, voigt_fit.best_fit, label='Voigt fit')
    plt.legend()
    plt.show()
    area = np.trapz(voigt_fit.best_fit, peak_wavelength)
    # print(f"The area under the fitted Voigt function is: {area}")
    return area


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def spec_data(species, peak_table, spectrum):
    spec_data = np.zeros((species.size, 7))
    integrals = integral(spectrum)
    for i in range(0, species.size):
        spec_data[i, 0] = species[i]  # wavelength of selected line
        idx = find_nearest(peak_table[:, 0], species[i])
        # NIST wavelength of the selected line
        spec_data[i, 1] = peak_table[idx, 0]
        spec_data[i, 2] = peak_table[idx, 1]  # Aki
        spec_data[i, 3] = peak_table[idx, 6]  # gi
        spec_data[i, 4] = peak_table[idx, 4]  # Ei
        idx2 = find_nearest(integrals[:, 0], species[i])
        Voigt_area = Voigt_integral(spectrum, species[i])
        # spec_data[i,5] = integrals[idx2,1] # integral of the line
        spec_data[i, 5] = Voigt_area  # integral of the line
        spec_data[i, 6] = integrals[idx2, 0]
    return spec_data


def AuAg_ratio(AuI_species, AgI_species, spectrum, atomic_lines_au1, atomic_lines_ag1):
    ln_ratio = np.zeros((AuI_species.size, AgI_species.size))
    E_value = np.zeros((AuI_species.size, AgI_species.size))
    AuIdata = spec_data(AuI_species, atomic_lines_au1, spectrum)
    AuI_ln = np.divide(np.multiply(
        AuIdata[:, 5], AuIdata[:, 1]*1E-7), np.multiply(AuIdata[:, 3], AuIdata[:, 2]))
    AgIdata = spec_data(AgI_species, atomic_lines_ag1, spectrum)
    AgI_ln = (np.divide(np.multiply(
        AgIdata[:, 5], AgIdata[:, 1]*1E-7), np.multiply(AgIdata[:, 3], AgIdata[:, 2])))

    for i in range(0, AuI_species.size):
        ln_ratio[i, :] = np.log(np.divide(AuI_ln[i], AgI_ln))
        E_value[i, :] = np.subtract(AgIdata[:, 4], AuIdata[i, 4])

    ln_ratios = np.reshape(ln_ratio, AuI_species.size*AgI_species.size)
    E_values = np.reshape(E_value, AuI_species.size*AgI_species.size)

    return np.stack((E_values, ln_ratios), axis=-1)


def line_pair(peak_table, species, spectrum, T):
    line_data = spec_data(peak_table, species, spectrum)
    linepairs = np.zeros((peak_table.size, peak_table.size))
    linepairs[:, 0] = peak_table
    linepairs[0, :] = peak_table
    for i in range(0, peak_table.size):
        for j in range(0, peak_table.size):
            intratio = line_data[i, 5]/line_data[j, 5]
            dataratio = np.divide(((line_data[i, 3]*line_data[i, 2])/line_data[i, 1])*np.exp(-line_data[i, 4]/(
                0.695035*T)), ((line_data[j, 3]*line_data[j, 2])/line_data[j, 1])*np.exp(-line_data[j, 4]/(0.695035*T)))
            linepairs[i, j] = np.divide(dataratio-intratio, dataratio)

    return linepairs

## Saha-Boltzmann line-pair plots for Ag/Au###


def AuAg_n_concentration(Au_peak_table, Ag_peak_table, spectrum, atomic_lines_au1, atomic_lines_ag1):
    AuAg_graph = AuAg_ratio(Au_peak_table, Ag_peak_table,
                            spectrum, atomic_lines_au1, atomic_lines_ag1)
    AuAg_fit = np.polyfit(AuAg_graph[:, 0], AuAg_graph[:, 1], 1)
    TAuAg = (1/(0.695035*AuAg_fit[0]))
    partition_function_ag1 = get_partition_function("Ag I", TAuAg)
    partition_function_ag2 = get_partition_function("Ag II", TAuAg)
    partition_function_au1 = get_partition_function("Au I", TAuAg)
    partition_function_au2 = get_partition_function("Au II", TAuAg)
    partition_function_ar1 = get_partition_function("Ar I", TAuAg)
    partition_function_ar2 = get_partition_function("Ar II", TAuAg)
    first_ionization_energy_ag = get_ionization_energy("Ag I")
    first_ionization_energy_au = get_ionization_energy("Au I")
    first_ionization_energy_ar = get_ionization_energy("Ar I")
    nAuAg = np.exp(AuAg_fit[1])*(partition_function_au1/partition_function_ag1)
    # n_ion_AuAg = nAuAg*(ZII(TAuAg, Au)/ZII(TAuAg, Ag))*(ZI(TAuAg, Ag)/ZI(TAuAg, Au))*np.exp((Ionization_Ag[0]-Ionization_Au[0])/(0.695035*TAuAg))

    ne = estimate_electron_concentration(
        TAuAg, first_ionization_energy_ar, partition_function_ar1, partition_function_ar2)
    nAgion_atom = SB(
        ne, TAuAg, first_ionization_energy_ag)*(partition_function_ag2/partition_function_ag1)
    nAuion_atom = SB(
        ne, TAuAg, first_ionization_energy_au)*(partition_function_au2/partition_function_au1)
    # nAgatom_ion = 1/nAgion_atom

    total_n_AuAg = ((nAuion_atom+1)/(nAgion_atom+1))*nAuAg

    plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 1], "x")
    plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 0]*AuAg_fit[0]+AuAg_fit[1])
    plt.xlabel('Difference of upper energy levels (cm-1)')
    plt.ylabel('log of line intensity ratios (a.u.)')
    plt.title('Saha-Boltzmann line-pair plot for Au I and Ag I lines')
    plt.figure()

    print(
        f"The temperature is: {TAuAg}, and the total Au-to-Ag number concentration ratio is: {total_n_AuAg}")

    return (TAuAg, total_n_AuAg)


spectrum = read_spectrum(
    "AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc")
corrected_spectrum = correct_spectrum(spectrum)

### Peak tables###
AuI_species = np.array([312.278, 406.507, 479.26])
AgI_species = np.array([338.29, 520.9078, 546.54])

### Baseline and peak finding###
wl_start = 400  # lower limit for plots
wl_end = 410  # upper limit for plots
set_wlen = 40  # the wlen parameter for the prominence function
set_height = 100


plt.plot(spectrum[:, 0], spectrum[:, 1])
plt.plot(spectrum[:, 0], baseline_arPLS(spectrum[:, 1]))
plt.xlim([310, 800])
# plt.ylim([4.5, 5])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Original spectrum and baseline')
plt.figure()

# major peaks in the spectrum
peaks = peakfinder(corrected_spectrum[:, 1], set_height)
integrals = integral(corrected_spectrum)  # integrals of the peaks
left = peak_prominences(corrected_spectrum[:, 1], peaks, wlen=set_wlen)[
    1]  # lower integration limit of each line
right = peak_prominences(corrected_spectrum[:, 1], peaks, wlen=set_wlen)[
    2]  # upper integration limit of each line

plt.plot(corrected_spectrum[:, 0], corrected_spectrum[:, 1])
plt.plot(corrected_spectrum[peaks, 0], corrected_spectrum[peaks, 1], "x")
plt.plot(corrected_spectrum[left, 0], corrected_spectrum[left, 1], "o")
plt.plot(corrected_spectrum[right, 0], corrected_spectrum[right, 1], "o")
plt.xlim([wl_start, wl_end])
plt.ylim([-100, 10000])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Baseline corrected spectrum with the major peaks')
plt.figure()

atomic_lines_au1 = get_atomic_lines(
    "Au I", lower_wavelength=300, upper_wavelength=800)
atomic_lines_ag1 = get_atomic_lines(
    "Ag I", lower_wavelength=300, upper_wavelength=800)

TAuAg = AuAg_n_concentration(
    AuI_species, AgI_species, corrected_spectrum, atomic_lines_au1, atomic_lines_ag1)[0]
total_n_AuAg = AuAg_n_concentration(
    AuI_species, AgI_species, corrected_spectrum, atomic_lines_au1, atomic_lines_ag1)[1]

AuI_linepair_check = line_pair(
    AuI_species, atomic_lines_au1, corrected_spectrum, TAuAg)
AgI_linepair_check = line_pair(
    AgI_species, atomic_lines_ag1, corrected_spectrum, TAuAg)

print(f"AuI linepair deviations: {AuI_linepair_check}")
print(f"AgI linepair deviations: {AgI_linepair_check}")
