import numpy as np
from scipy.signal import find_peaks, peak_prominences
from data_preparation.spectrum_correction import SpectrumCorrector
from data_preparation.spectrum_reader import SpectrumReader
from data_preparation.peak_finder import PeakFinder
from data_preparation.integral_calculator import IntegralCalculator
import scipy

from matplotlib import pyplot as plt

from lmfit.models import PseudoVoigtModel

from new_codebase.electron_conentration_estimation import estimate_electron_concentration, SB
from new_codebase.gather_data import get_atomic_lines, get_ionization_energy, get_partition_function, read_spectrum


def peakfinder(Y, height):
    peak_indices, _ = find_peaks(Y, height, threshold=0, width=2)
    return peak_indices


def find_nearest_indices(spectrum_data, target_peaks, taget_column):
    indices = np.abs(spectrum_data[:, taget_column] -
                     target_peaks[:, np.newaxis]).argmin(axis=1)

    return indices


def Voigt_integral(spectrum, peaks, selected_peaks):
    wavelength = spectrum[:, 0]
    Y = spectrum[:, 1]
    all_peaks = np.stack((peaks,
                         wavelength[peaks]), axis=-1)

    voigt_integrals = []
    selected_peak_indices = find_nearest_indices(all_peaks, selected_peaks, 1)
    for selected_peak_idx in selected_peak_indices:
        selected_peak_idx_array = np.array(
            [int(all_peaks[selected_peak_idx, 0])])

        prominences = peak_prominences(
            Y, selected_peak_idx_array, wlen=set_wlen)
        start_index = int(prominences[1])
        end_index = 2*int(all_peaks[selected_peak_idx, 0])-int(prominences[1])
        peak_wavelength = wavelength[start_index:end_index+1]
        peak_spectrum = Y[start_index:end_index+1]
        voigt_model = PseudoVoigtModel()
        params = voigt_model.guess(peak_spectrum, x=peak_wavelength)
        voigt_fit = voigt_model.fit(peak_spectrum, params, x=peak_wavelength)
        plt.plot(peak_wavelength, peak_spectrum,
                 'o', label='Original spectrum')
        plt.plot(peak_wavelength, voigt_fit.best_fit, label='Voigt fit')
        plt.legend()
        plt.show()
        area = np.trapz(voigt_fit.best_fit, peak_wavelength)
        voigt_integrals.append(area)
        # print(f"The area under the fitted Voigt function is: {area}")
    return np.array(voigt_integrals)


def find_nearest(array, value):
    array = np.asarray(array)
    return (np.abs(array - value)).argmin()


def AuAg_ratio(AuIdata, AgIdata):
    ln_ratio = np.zeros((len(AuIdata), len(AgIdata)))
    E_value = np.zeros((len(AuIdata), len(AgIdata)))
    AuI_ln = np.divide(np.multiply(
        AuIdata[:, 5], AuIdata[:, 1]*1E-7), np.multiply(AuIdata[:, 3], AuIdata[:, 2]))
    AgI_ln = (np.divide(np.multiply(
        AgIdata[:, 5], AgIdata[:, 1]*1E-7), np.multiply(AgIdata[:, 3], AgIdata[:, 2])))

    for i in range(0, len(AuIdata)):
        ln_ratio[i, :] = np.log(np.divide(AuI_ln[i], AgI_ln))
        E_value[i, :] = np.subtract(AgIdata[:, 4], AuIdata[i, 4])

    ln_ratios = np.reshape(ln_ratio, len(AuIdata)*len(AgIdata))
    E_values = np.reshape(E_value, len(AuIdata)*len(AgIdata))

    return np.stack((E_values, ln_ratios), axis=-1)


def line_pair(peak_table, line_data, T):
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


def fit_graph(graph):
    return np.polyfit(graph[:, 0], graph[:, 1], 1)


def caculate_temperature(fitted_graph):
    return 1/(0.695035*fitted_graph[0])


def calculate_nAuAg(AuAg_fit, partition_function_au1, partition_function_ag1):
    return np.exp(AuAg_fit[1])*(partition_function_au1/partition_function_ag1)


def AuAg_n_concentration(nAuAg, nAuion_atom, nAgion_atom):
    return ((nAuion_atom+1)/(nAgion_atom+1))*nAuAg


def prepare_data(target_peaks, atomic_lines, voigt_area):
    return np.concatenate((target_peaks[:, np.newaxis], atomic_lines, voigt_area[:, np.newaxis]), axis=1)


### Peak tables###
AuI_species = np.array([312.278, 406.507, 479.26])
AgI_species = np.array([338.29, 520.9078, 546.54])

### Baseline and peak finding###
wl_start = 400  # lower limit for plots
wl_end = 410  # upper limit for plots
set_wlen = 40  # the wlen parameter for the prominence function
set_height = 100

spectrum = SpectrumReader().read_ascii_spectrum_to_numpy(
    file_path="AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc")
spectrum_corrector = SpectrumCorrector(spectrum=spectrum,
                                       wavelength_column_index=0, intensity_column_index=10)
corrected_spectrum = spectrum_corrector.correct_spectrum()
peak_finder = PeakFinder(required_height=set_height)

peaks = peak_finder.find_peak_indices(corrected_spectrum[:, 1])

integral_calculator = IntegralCalculator(
    peak_finder=peak_finder, prominance_wlen=set_wlen)
au1_integrals = integral_calculator.calculate_integrals(
    corrected_spectrum, AuI_species)
ag1_integrals = integral_calculator.calculate_integrals(
    corrected_spectrum, AgI_species)

atomic_lines_au1 = get_atomic_lines("Au I", target_peaks=AuI_species)
atomic_lines_ag1 = get_atomic_lines("Ag I", target_peaks=AgI_species)


AuIdata = prepare_data(AuI_species, atomic_lines_au1, au1_integrals)
AgIdata = prepare_data(AgI_species, atomic_lines_ag1, ag1_integrals)

AuAg_graph = AuAg_ratio(AuIdata, AgIdata)

AuAg_fit = fit_graph(AuAg_graph)

TAuAg = caculate_temperature(AuAg_fit)

partition_function_ag1 = get_partition_function("Ag I", TAuAg)
partition_function_ag2 = get_partition_function("Ag II", TAuAg)
partition_function_au1 = get_partition_function("Au I", TAuAg)
partition_function_au2 = get_partition_function("Au II", TAuAg)
partition_function_ar1 = get_partition_function("Ar I", TAuAg)
partition_function_ar2 = get_partition_function("Ar II", TAuAg)
first_ionization_energy_ag = get_ionization_energy("Ag I")
first_ionization_energy_au = get_ionization_energy("Au I")
first_ionization_energy_ar = get_ionization_energy("Ar I")

nAuAg = calculate_nAuAg(
    AuAg_fit, partition_function_au1, partition_function_ag1)

ne = estimate_electron_concentration(
    TAuAg, first_ionization_energy_ar, partition_function_ar1, partition_function_ar2)
nAgion_atom = SB(
    ne, TAuAg, first_ionization_energy_ag)*(partition_function_ag2/partition_function_ag1)
nAuion_atom = SB(
    ne, TAuAg, first_ionization_energy_au)*(partition_function_au2/partition_function_au1)
# nAgatom_ion = 1/nAgion_atom

total_n_AuAg = AuAg_n_concentration(nAuAg, nAuion_atom, nAgion_atom)

AuI_linepair_check = line_pair(AuI_species, AuIdata, TAuAg)
AgI_linepair_check = line_pair(AgI_species, AgIdata, TAuAg)

plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 1], "x")
plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 0]*AuAg_fit[0]+AuAg_fit[1])
plt.xlabel('Difference of upper energy levels (cm-1)')
plt.ylabel('log of line intensity ratios (a.u.)')
plt.title('Saha-Boltzmann line-pair plot for Au I and Ag I lines')
plt.figure()

print(
    f"The temperature is: {TAuAg}, and the total Au-to-Ag number concentration ratio is: {total_n_AuAg}")

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

plt.plot(spectrum[:, 0], spectrum[:, 1])
plt.plot(spectrum[:, 0], spectrum_corrector.get_baseline())
plt.xlim([310, 800])
# plt.ylim([4.5, 5])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Original spectrum and baseline')
plt.figure()

print(f"AuI linepair deviations: {AuI_linepair_check}")
print(f"AgI linepair deviations: {AgI_linepair_check}")
