import numpy as np
from scipy.signal import find_peaks, peak_prominences
from data_preparation.spectrum_correction import SpectrumCorrector
from data_preparation.spectrum_reader import SpectrumReader
from data_preparation.peak_finder import PeakFinder
from data_preparation.calculation_data_preparator import CalculationDataPreparator, CalculationDataPreparatorConfig

from matplotlib import pyplot as plt

from new_codebase.electron_conentration_estimation import estimate_electron_concentration, SB
from new_codebase.gather_data import get_ionization_energy, get_partition_function


def AuAg_ratio(first_species_data, second_species_data):
    first_species_ln = get_ln(first_species_data)
    second_species_ln = get_ln(second_species_data)
    ln_ratios = np.log(first_species_ln[:, np.newaxis]/second_species_ln)
    e_values = second_species_data[:, 4] - \
        first_species_data[:, 4][:, np.newaxis]

    return np.stack((e_values.flatten(), ln_ratios.flatten()), axis=-1)


def get_ln(species_data):
    return (species_data[:, 5]*species_data[:, 1]*1E-7) / (species_data[:, 3]*species_data[:, 2])


def line_pair(line_data, T):
    intratio = line_data[:, 5]/line_data[:, 5][:, np.newaxis]
    dataratio = np.divide((((line_data[:, 3]*line_data[:, 2]) /
                            line_data[:, 1])*np.exp(-line_data[:, 4]/(0.695035*T))),
                          (((line_data[:, 3]*line_data[:, 2])/line_data[:, 1])*np.exp(-line_data[:, 4]/(0.695035*T)))[:, np.newaxis])

    return np.divide(dataratio-intratio, dataratio).T


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
first_species_target_peaks = np.array([312.278, 406.507, 479.26])
second_species_target_peaks = np.array([338.29, 520.9078, 546.54])

### Baseline and peak finding###
wl_start = 400  # lower limit for plots
wl_end = 410  # upper limit for plots
set_wlen = 40  # the wlen parameter for the prominence function
set_height = 100
first_species = "Au I"
second_species = "Ag I"
spectrum_path = "AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc"
spectrum = SpectrumReader().read_ascii_spectrum_to_numpy(
    file_path="AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc")
spectrum_corrector = SpectrumCorrector()
corrected_spectrum = spectrum_corrector.correct_spectrum(spectrum=spectrum,
                                                         wavelength_column_index=0, intensity_column_index=10)


first_species_data = CalculationDataPreparator(
    CalculationDataPreparatorConfig(
        spectrum=corrected_spectrum,
        species_name=first_species,
        species_target_peak_wavelengths=first_species_target_peaks,
    )
).prepare_calculation_data()

second_species_data = CalculationDataPreparator(
    CalculationDataPreparatorConfig(
        spectrum=corrected_spectrum,
        species_name=second_species,
        species_target_peak_wavelengths=second_species_target_peaks,
    )
).prepare_calculation_data()

AuAg_graph = AuAg_ratio(first_species_data, second_species_data)

AuAg_fit = fit_graph(AuAg_graph)

TAuAg = caculate_temperature(AuAg_fit)
partition_function_ag1 = get_partition_function("Ag I", TAuAg)
partition_function_au1 = get_partition_function("Au I", TAuAg)

nAuAg = calculate_nAuAg(
    AuAg_fit, partition_function_au1, partition_function_ag1)

partition_function_ag2 = get_partition_function("Ag II", TAuAg)
partition_function_au2 = get_partition_function("Au II", TAuAg)
partition_function_ar1 = get_partition_function("Ar I", TAuAg)
partition_function_ar2 = get_partition_function("Ar II", TAuAg)
first_ionization_energy_ag = get_ionization_energy("Ag I")
first_ionization_energy_au = get_ionization_energy("Au I")
first_ionization_energy_ar = get_ionization_energy("Ar I")


ne = estimate_electron_concentration(
    TAuAg, first_ionization_energy_ar, partition_function_ar1, partition_function_ar2)
nAgion_atom = SB(
    ne, TAuAg, first_ionization_energy_ag)*(partition_function_ag2/partition_function_ag1)
nAuion_atom = SB(
    ne, TAuAg, first_ionization_energy_au)*(partition_function_au2/partition_function_au1)
# nAgatom_ion = 1/nAgion_atom

total_n_AuAg = AuAg_n_concentration(nAuAg, nAuion_atom, nAgion_atom)

AuI_linepair_check = line_pair(first_species_data, TAuAg)
AgI_linepair_check = line_pair(second_species_data, TAuAg)

plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 1], "x")
plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 0]*AuAg_fit[0]+AuAg_fit[1])
plt.xlabel('Difference of upper energy levels (cm-1)')
plt.ylabel('log of line intensity ratios (a.u.)')
plt.title('Saha-Boltzmann line-pair plot for Au I and Ag I lines')
plt.figure()

print(
    f"The temperature is: {TAuAg}, and the total Au-to-Ag number concentration ratio is: {total_n_AuAg}")

peak_finder = PeakFinder(required_height=set_height)
peaks = peak_finder.find_peak_indices(corrected_spectrum[:, 1])

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
plt.plot(spectrum[:, 0], spectrum_corrector.calculate_baseline(
    spectrum, 10))
plt.xlim([310, 800])
# plt.ylim([4.5, 5])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Original spectrum and baseline')
plt.figure()

print(f"AuI linepair deviations: {AuI_linepair_check}")
print(f"AgI linepair deviations: {AgI_linepair_check}")
