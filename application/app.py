from dataclasses import dataclass

import numpy as np

from application.config import ApplicationConfig
from application.readers import ASCIISpectrumReader
from application.lib import PeakFinder, SpectrumCorrector, SpectrumCorrectionData
from application.calculators import (
    AtomConcentraionCalculator,
    IonAtomConcentraionCalculator,
    TotalConcentrationCalculator,
    VoigtIntegralCalculator,
    ElectronConcentrationCalculator,
    IntensityRatiosCalculator,
    TemperatureCalculator,
    IntensityRatiosData,
)
from application.data_preparation.getters import (
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


@dataclass
class ApplicationResult:
    original_spectrum: np.ndarray
    spectrum_correction_data: SpectrumCorrectionData
    peak_indices: np.ndarray
    intensity_ratio_data: IntensityRatiosData
    total_concentration: float
    temperature: float
    first_species_atomic_lines: np.ndarray
    second_species_atomic_lines: np.ndarray
    first_species_integrals: np.ndarray
    second_species_integrals: np.ndarray


class Application:
    def __init__(self, config: ApplicationConfig):
        self.config = config
        self.file_reader = ASCIISpectrumReader()
        self.partition_function_data_getter = PartitionFunctionDataGetter(
            atomic_levels_fetcher=AtomicLevelsFetcher(),
            atomic_levels_parser=AtomicLevelsParser(),
        )
        self.ionization_energy_data_getter = IonizationEnergyDataGetter(
            ionization_energy_fetcher=IonizationEnergyFetcher(),
            ionization_energy_parser=IonizationEnergyParser(),
        )

        self.atomic_lines_data_getter = AtomicLinesDataGetter(
            atomic_lines_fetcher=AtomicLinesFetcher(),
            atomic_lines_parser=AtomicLinesParser(),
        )
        self.peak_finder = PeakFinder(
            required_height=self.config.peak_minimum_requred_height
        )
        self.spectrum_corrector = SpectrumCorrector()
        self.integral_calculator = VoigtIntegralCalculator(
            prominance_window_length=self.config.prominence_window_length
        )
        self.intensity_ratios_calculator = IntensityRatiosCalculator()
        self.electron_concentration_calculation = ElectronConcentrationCalculator()
        self.temperature_calculatior = TemperatureCalculator()
        self.atom_concentration_calculatior = AtomConcentraionCalculator()
        self.ion_atom_concentration_calculator = IonAtomConcentraionCalculator()
        self.total_concentration_calculator = TotalConcentrationCalculator()

    def run(self):
        spectrum = self.file_reader.read_spectrum_to_numpy(
            file_path=self.config.spectrum_path
        )

        spectrum_correction_data = self.spectrum_corrector.correct_spectrum(
            spectrum=spectrum, wavelength_column_index=0, intensity_column_index=10
        )

        peak_indices = self.peak_finder.find_peak_indices(
            spectrum_correction_data.corrected_spectrum[:, 1]
        )

        first_species_integrals = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.first_species_target_peaks,
        )

        first_species_atomic_lines = self.atomic_lines_data_getter.get_data(
            self.config.first_species_atom_name, self.config.first_species_target_peaks
        )

        second_species_integrals = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.second_species_target_peaks,
        )

        second_species_atomic_lines = self.atomic_lines_data_getter.get_data(
            self.config.second_species_atom_name,
            self.config.second_species_target_peaks,
        )

        intensity_ratio_data = self.intensity_ratios_calculator.calculate(
            first_species_atomic_lines=first_species_atomic_lines,
            first_species_integrals=first_species_integrals,
            second_species_atomic_lines=second_species_atomic_lines,
            second_species_integrals=second_species_integrals,
        )
        temperature = self.temperature_calculatior.calculate(
            intensity_ratio_data.fitted_intensity_ratios
        )
        partition_function_first_species_atom = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.first_species_atom_name,
                temperature=temperature,
            )
        )
        partition_function_second_species_atom = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.second_species_atom_name,
                temperature=temperature,
            )
        )
        atom_concentration = self.atom_concentration_calculatior.calculate(
            fitted_ratios=intensity_ratio_data.fitted_intensity_ratios,
            first_species_atom_partition_function=partition_function_first_species_atom,
            second_species_atom_partition_function=partition_function_second_species_atom,
        )
        partition_function_medium_species_atom = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.medium_species_atom_name,
                temperature=temperature,
            )
        )
        partition_function_medium_species_ion = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.medium_species_ion_name,
                temperature=temperature,
            )
        )
        ionization_energy_medium_species = self.ionization_energy_data_getter.get_data(
            self.config.medium_species_atom_name
        )
        electron_concentration = self.electron_concentration_calculation.calculate(
            temperature=temperature,
            ionization_energy=ionization_energy_medium_species,
            partition_function_atom=partition_function_medium_species_atom,
            partition_function_ion=partition_function_medium_species_ion,
        )

        partition_function_first_species_ion = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.first_species_ion_name, temperature=temperature
            )
        )

        ionization_energy_first_species = self.ionization_energy_data_getter.get_data(
            self.config.first_species_atom_name
        )

        first_species_ion_atom_concentration = (
            self.ion_atom_concentration_calculator.calculate(
                electron_concentration=electron_concentration,
                temperature=temperature,
                ionization_energy=ionization_energy_first_species,
                partition_function_atom=partition_function_first_species_atom,
                partition_function_ion=partition_function_first_species_ion,
            )
        )

        partition_function_second_species_ion = (
            self.partition_function_data_getter.get_data(
                species_name=self.config.second_species_ion_name,
                temperature=temperature,
            )
        )

        ionization_energy_second_species = self.ionization_energy_data_getter.get_data(
            self.config.second_species_atom_name
        )

        second_species_ion_atom_concentration = (
            self.ion_atom_concentration_calculator.calculate(
                electron_concentration=electron_concentration,
                temperature=temperature,
                ionization_energy=ionization_energy_second_species,
                partition_function_atom=partition_function_second_species_atom,
                partition_function_ion=partition_function_second_species_ion,
            )
        )

        total_concentration = self.total_concentration_calculator.calculate(
            atom_concentration,
            first_species_ion_atom_concentration,
            second_species_ion_atom_concentration,
        )

        return ApplicationResult(
            original_spectrum=spectrum,
            spectrum_correction_data=spectrum_correction_data,
            peak_indices=peak_indices,
            intensity_ratio_data=intensity_ratio_data,
            total_concentration=total_concentration,
            temperature=temperature,
            first_species_atomic_lines=first_species_atomic_lines,
            first_species_integrals=first_species_integrals,
            second_species_atomic_lines=second_species_atomic_lines,
            second_species_integrals=second_species_integrals,
        )
