import numpy as np

from plotting import Plotter
from readers import ASCIISpectrumReader
from lib import (
    PeakFinder,
    SpectrumCorrector,
    LinePairChecker,
    VoigtIntegralCalculator,
    ElectronConcentrationCalculator,
)
from calculators import (
    AtomConcentraionCalculator,
    IonAtomConcentraionCalculator,
    TotalConcentrationCalculator,
)
from data_preparation.getters import (
    PartitionFunctionDataGetter,
    IonizationEnergyDataGetter,
    AtomicLinesDataGetter,
)

from nist.fetchers import (
    AtomicLinesFetcher,
    AtomicLevelsFetcher,
    IonizationEnergyFetcher,
)

from nist.parsers import (
    AtomicLinesParser,
    AtomicLevelsParser,
    IonizationEnergyParser,
)


def kek():
    first_species_target_peaks = np.array([312.278, 406.507, 479.26])
    second_species_target_peaks = np.array([338.29, 520.9078, 546.54])

    set_wlen = 40  # the wlen parameter for the prominence function
    set_height = 100
    first_species_name = "Au I"
    second_species_name = "Ag I"
    spectrum_path = "AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc"

    spectrum = ASCIISpectrumReader().read_spectrum_to_numpy(file_path=spectrum_path)

    spectrum_corrector = SpectrumCorrector()
    spectrum_correction_data = spectrum_corrector.correct_spectrum(
        spectrum=spectrum, wavelength_column_index=0, intensity_column_index=10
    )

    partition_function_data_getter = PartitionFunctionDataGetter(
        atomic_levels_fetcher=AtomicLevelsFetcher(),
        atomic_levels_parser=AtomicLevelsParser(),
    )
    ionization_energy_data_getter = IonizationEnergyDataGetter(
        ionization_energy_fetcher=IonizationEnergyFetcher(),
        ionization_energy_parser=IonizationEnergyParser(),
    )

    atomic_lines_data_getter = AtomicLinesDataGetter(
        atomic_lines_fetcher=AtomicLinesFetcher(),
        atomic_lines_parser=AtomicLinesParser(),
    )
    peak_finder = PeakFinder(required_height=set_height)

    integral_calculator = VoigtIntegralCalculator(prominance_window_length=set_wlen)

    peak_indices = peak_finder.find_peak_indices(
        spectrum_correction_data.corrected_spectrum[:, 1]
    )

    first_species_integrals = integral_calculator.calculate_integrals(
        spectrum_correction_data.corrected_spectrum,
        peak_indices,
        first_species_target_peaks,
    )

    first_species_atomic_lines = atomic_lines_data_getter.get_data(
        first_species_name, first_species_target_peaks
    )

    second_species_integrals = integral_calculator.calculate_integrals(
        spectrum_correction_data.corrected_spectrum,
        peak_indices,
        second_species_target_peaks,
    )

    second_species_atomic_lines = atomic_lines_data_getter.get_data(
        second_species_name, second_species_target_peaks
    )

    atom_concentration_data = AtomConcentraionCalculator(
        partition_function_data_getter=partition_function_data_getter
    ).calculate(
        first_species_name=first_species_name,
        first_species_atomic_lines=first_species_atomic_lines,
        first_species_integrals=first_species_integrals,
        second_species_name=second_species_name,
        second_species_atomic_lines=second_species_atomic_lines,
        second_species_integrals=second_species_integrals,
    )

    electron_concentration = ElectronConcentrationCalculator(
        partition_function_data_getter=partition_function_data_getter,
        ionization_energy_data_getter=ionization_energy_data_getter,
    ).calculate(
        temperature=atom_concentration_data.temperature,
        species_name="Ar I",
        partition_function_atom="Ar I",
        partition_function_ion="Ar II",
    )

    nAgion_atom = IonAtomConcentraionCalculator(
        partition_function_data_getter=partition_function_data_getter,
        ionization_energy_data_getter=ionization_energy_data_getter,
    ).calculate(
        electron_concentration=electron_concentration,
        temperature=atom_concentration_data.temperature,
        species_name="Ag I",
        partition_function_atom_name="Ag I",
        partition_function_ion_name="Ag II",
    )

    nAuion_atom = IonAtomConcentraionCalculator(
        partition_function_data_getter=partition_function_data_getter,
        ionization_energy_data_getter=ionization_energy_data_getter,
    ).calculate(
        electron_concentration=electron_concentration,
        temperature=atom_concentration_data.temperature,
        species_name="Au I",
        partition_function_atom_name="Au I",
        partition_function_ion_name="Au II",
    )

    total_concentration = TotalConcentrationCalculator().calculate(
        atom_concentration_data.atom_concentration_ratio,
        nAuion_atom,
        nAgion_atom,
    )

    AuI_linepair_check = LinePairChecker().check_line_pairs(
        first_species_atomic_lines,
        first_species_integrals,
        atom_concentration_data.temperature,
    )
    AgI_linepair_check = LinePairChecker().check_line_pairs(
        second_species_atomic_lines,
        second_species_integrals,
        atom_concentration_data.temperature,
    )

    print(
        f"The number concentration ratio for {first_species_name}-{second_species_name}: {total_concentration:8.5f}"
    )
    print(f"The temperature is: {atom_concentration_data.temperature:6.3f} K")
    print(f"{first_species_name} linepair deviations: {AuI_linepair_check}")
    print(f"{second_species_name} linepair deviations: {AgI_linepair_check}")
    print(spectrum_correction_data.baseline)

    plotter = Plotter()
    plotter.plot_original_spectrum(
        spectrum=spectrum, spectrum_correction_data=spectrum_correction_data
    )

    plotter.plot_saha_boltzmann_line_pairs(
        atom_concentration_data=atom_concentration_data
    )

    plotter.plot_baseline_corrected_spectrum_with_the_major_peaks(
        spectrum_correction_data=spectrum_correction_data,
        peak_indices=peak_indices,
        wlen=set_wlen,
        xlim=[400, 410],
        ylim=[0, 200],
    )
