import numpy as np

from plotting import Plotter
from logger import Logger
from application import ApplicationConfig
from readers import ASCIISpectrumReader
from lib import (
    PeakFinder,
    SpectrumCorrector,
    LinePairChecker,
)
from calculators import (
    AtomConcentraionCalculator,
    IonAtomConcentraionCalculator,
    TotalConcentrationCalculator,
    VoigtIntegralCalculator,
    ElectronConcentrationCalculator,
    IntensityRatiosCalculator,
    TemperatureCalculator,
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


class Application:
    def __init__(self, config: ApplicationConfig):
        self.config = config
        self.logger = Logger().new()

    def run(self):
        spectrum = ASCIISpectrumReader().read_spectrum_to_numpy(
            file_path=self.config.spectrum_path
        )

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
        peak_finder = PeakFinder(
            required_height=self.config.peak_minimum_requred_height
        )

        integral_calculator = VoigtIntegralCalculator(
            prominance_window_length=self.config.prominence_window_length
        )

        peak_indices = peak_finder.find_peak_indices(
            spectrum_correction_data.corrected_spectrum[:, 1]
        )

        first_species_integrals = integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.first_species_target_peaks,
        )

        first_species_atomic_lines = atomic_lines_data_getter.get_data(
            self.config.first_species_atom_name, self.config.first_species_target_peaks
        )

        second_species_integrals = integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.second_species_target_peaks,
        )

        second_species_atomic_lines = atomic_lines_data_getter.get_data(
            self.config.second_species_atom_name,
            self.config.second_species_target_peaks,
        )

        intensity_ratio_data = IntensityRatiosCalculator().calculate(
            first_species_atomic_lines=first_species_atomic_lines,
            first_species_integrals=first_species_integrals,
            second_species_atomic_lines=second_species_atomic_lines,
            second_species_integrals=second_species_integrals,
        )
        temperature = TemperatureCalculator().calculate(
            intensity_ratio_data.fitted_intensity_ratios
        )
        partition_function_first_species_atom = partition_function_data_getter.get_data(
            species_name=self.config.first_species_atom_name, temperature=temperature
        )
        partition_function_second_species_atom = (
            partition_function_data_getter.get_data(
                species_name=self.config.second_species_atom_name,
                temperature=temperature,
            )
        )
        atom_concentration = AtomConcentraionCalculator().calculate(
            fitted_ratios=intensity_ratio_data.fitted_intensity_ratios,
            first_species_partition_function=partition_function_first_species_atom,
            second_species_partition_function=partition_function_second_species_atom,
        )
        partition_function_medium_species_atom = (
            partition_function_data_getter.get_data(
                species_name=self.config.medium_species_atom_name,
                temperature=temperature,
            )
        )
        partition_function_medium_species_ion = partition_function_data_getter.get_data(
            species_name=self.config.medium_species_ion_name, temperature=temperature
        )
        ionization_energy_medium_species = ionization_energy_data_getter.get_data(
            self.config.medium_species_atom_name
        )
        electron_concentration = ElectronConcentrationCalculator().calculate(
            temperature=temperature,
            ionization_energy=ionization_energy_medium_species,
            partition_function_atom=partition_function_medium_species_atom,
            partition_function_ion=partition_function_medium_species_ion,
        )

        partition_function_first_species_ion = partition_function_data_getter.get_data(
            species_name=self.config.first_species_ion_name, temperature=temperature
        )

        ionization_energy_first_species = ionization_energy_data_getter.get_data(
            self.config.first_species_atom_name
        )

        first_species_ion_atom_concentration = (
            IonAtomConcentraionCalculator().calculate(
                electron_concentration=electron_concentration,
                temperature=temperature,
                ionization_energy=ionization_energy_first_species,
                partition_function_atom=partition_function_first_species_atom,
                partition_function_ion=partition_function_first_species_ion,
            )
        )

        partition_function_second_species_ion = partition_function_data_getter.get_data(
            species_name=self.config.second_species_ion_name, temperature=temperature
        )

        ionization_energy_second_species = ionization_energy_data_getter.get_data(
            self.config.second_species_atom_name
        )

        second_species_ion_atom_concentration = (
            IonAtomConcentraionCalculator().calculate(
                electron_concentration=electron_concentration,
                temperature=temperature,
                ionization_energy=ionization_energy_second_species,
                partition_function_atom=partition_function_second_species_atom,
                partition_function_ion=partition_function_second_species_ion,
            )
        )

        total_concentration = TotalConcentrationCalculator().calculate(
            atom_concentration,
            first_species_ion_atom_concentration,
            second_species_ion_atom_concentration,
        )

        AuI_linepair_check = LinePairChecker().check_line_pairs(
            first_species_atomic_lines,
            first_species_integrals,
            temperature,
        )
        AgI_linepair_check = LinePairChecker().check_line_pairs(
            second_species_atomic_lines,
            second_species_integrals,
            temperature,
        )

        self.logger.info(
            f"The number concentration ratio for {self.config.first_species_atom_name}-{self.config.second_species_atom_name}: {total_concentration:8.5f}"
        )
        self.logger.info(f"The temperature is: {temperature:6.3f} K")
        self.logger.info(
            f"{self.config.first_species_atom_name} linepair deviations: {AuI_linepair_check}"
        )
        self.logger.info(
            f"{self.config.second_species_atom_name} linepair deviations: {AgI_linepair_check}"
        )

        plotter = Plotter()
        plotter.plot_original_spectrum(
            spectrum=spectrum, spectrum_correction_data=spectrum_correction_data
        )

        plotter.plot_saha_boltzmann_line_pairs(
            intensity_ratios_data=intensity_ratio_data
        )

        plotter.plot_baseline_corrected_spectrum_with_the_major_peaks(
            spectrum_correction_data=spectrum_correction_data,
            peak_indices=peak_indices,
            wlen=self.config.prominence_window_length,
            xlim=[400, 410],
            ylim=[0, 200],
        )


if __name__ == "__main__":
    config = ApplicationConfig(
        spectrum_path="AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc",
        first_species_target_peaks=np.array([312.278, 406.507, 479.26]),
        first_species_atom_name="Au I",
        first_species_ion_name="Au II",
        second_species_target_peaks=np.array([338.29, 520.9078, 546.54]),
        second_species_atom_name="Ag I",
        second_species_ion_name="Ag II",
        medium_species_atom_name="Ar I",
        medium_species_ion_name="Ar II",
        prominence_window_length=40,
        peak_minimum_requred_height=100,
    )
    app = Application(config)
    app.run()
