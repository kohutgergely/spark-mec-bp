from dataclasses import dataclass

import numpy as np

from application.config import ApplicationConfig
from application.readers import ASCIISpectrumReader
from application.lib import PeakFinder, SpectrumCorrector
from application.calculators import (
    AtomConcentraionCalculator,
    IonAtomConcentraionCalculator,
    TotalConcentrationCalculator,
    VoigtIntegralCalculator,
    ElectronConcentrationCalculator,
    IntensityRatiosCalculator,
    TemperatureCalculator,
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
    corrected_spectrum: np.ndarray
    baseline: np.ndarray
    peak_indices: np.ndarray
    intensity_ratios: np.ndarray
    fitted_intensity_ratios: np.ndarray
    total_concentration: float
    temperature: float
    first_species_atomic_lines: np.ndarray
    second_species_atomic_lines: np.ndarray
    first_species_integrals: np.ndarray
    second_species_integrals: np.ndarray


class Application:
    @dataclass
    class _NISTAtomicLinesData:
        first_species: np.ndarray
        second_species: np.ndarray

    @dataclass
    class _NISTPartitionFunctionData:
        first_species_atom: float
        first_species_ion: float
        second_species_atom: float
        second_species_ion: float
        carrier_species_atom: float
        carrier_species_ion: float

    @dataclass
    class _NISTIonizationEnergyData:
        first_species: float
        second_species: float
        carrier_species: float

    @dataclass
    class _IntegralsData:
        first_species: float
        second_species: float

    @dataclass
    class _IonAtomConcentrationData:
        first_species: float
        second_species: float

    def __init__(self, config: ApplicationConfig):
        self.config = config
        self.file_reader = ASCIISpectrumReader()
        self.atomic_lines_getter = AtomicLinesDataGetter(
            atomic_lines_fetcher=AtomicLinesFetcher(),
            atomic_lines_parser=AtomicLinesParser(),
        )
        self.partition_function_getter = PartitionFunctionDataGetter(
            atomic_levels_fetcher=AtomicLevelsFetcher(),
            atomic_levels_parser=AtomicLevelsParser(),
        )
        self.ionization_energy_getter = IonizationEnergyDataGetter(
            ionization_energy_fetcher=IonizationEnergyFetcher(),
            ionization_energy_parser=IonizationEnergyParser(),
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
        spectrum = self._read_spectrum()
        spectrum_correction_data = self._correct_spectrum(spectrum)
        peak_indices = self._find_peaks(spectrum_correction_data)
        atomic_lines = self._get_atomic_lines()
        integrals = self._caluclate_integrals(spectrum_correction_data, peak_indices)
        intensity_ratio_data = self._calculate_intensity_ratios(atomic_lines, integrals)
        temperature = self._calculate_temperature(intensity_ratio_data)
        partition_functions = self._get_partition_functions_from_nist(temperature)
        ionization_energies = self._get_ionization_energies_from_nist()
        atom_concentration = self._calculate_atom_concentration(
            intensity_ratio_data, partition_functions
        )
        electron_concentration = self._calculate_electron_concentration(
            temperature, partition_functions, ionization_energies
        )
        ion_atom_concentrations = self._calculate_ion_atom_concentrations(
            temperature,
            partition_functions,
            ionization_energies,
            electron_concentration,
        )
        total_concentration = self._calculate_total_concentration(
            atom_concentration, ion_atom_concentrations
        )

        return ApplicationResult(
            original_spectrum=spectrum,
            corrected_spectrum=spectrum_correction_data.corrected_spectrum,
            baseline=spectrum_correction_data.baseline,
            peak_indices=peak_indices,
            intensity_ratios=intensity_ratio_data.intensity_ratios,
            fitted_intensity_ratios=intensity_ratio_data.fitted_intensity_ratios,
            total_concentration=total_concentration,
            temperature=temperature,
            first_species_atomic_lines=atomic_lines.first_species,
            first_species_integrals=integrals.first_species,
            second_species_atomic_lines=atomic_lines.second_species,
            second_species_integrals=integrals.second_species,
        )

    def _read_spectrum(self):
        return self.file_reader.read_spectrum_to_numpy(
            file_path=self.config.spectrum_path
        )

    def _correct_spectrum(self, spectrum):
        return self.spectrum_corrector.correct_spectrum(
            spectrum=spectrum,
            wavelength_column_index=self.config.spectrum_wavelength_column_index,
            intensity_column_index=self.config.spectrum_intensity_column_index,
        )

    def _find_peaks(self, spectrum_correction_data):
        return self.peak_finder.find_peak_indices(
            spectrum_correction_data.corrected_spectrum[:, 1]
        )

    def _get_atomic_lines(self) -> _NISTAtomicLinesData:
        first_species = self.atomic_lines_getter.get_data(
            self.config.first_species_atom_name, self.config.first_species_target_peaks
        )

        second_species = self.atomic_lines_getter.get_data(
            self.config.second_species_atom_name,
            self.config.second_species_target_peaks,
        )

        return self._NISTAtomicLinesData(
            first_species,
            second_species,
        )

    def _caluclate_integrals(
        self, spectrum_correction_data, peak_indices
    ) -> _IntegralsData:
        first_species = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.first_species_target_peaks,
        )

        second_species = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.second_species_target_peaks,
        )

        return self._IntegralsData(first_species, second_species)

    def _calculate_intensity_ratios(self, atomic_lines, integrals):
        return self.intensity_ratios_calculator.calculate(
            first_species_atomic_lines=atomic_lines.first_species,
            first_species_integrals=integrals.first_species,
            second_species_atomic_lines=atomic_lines.second_species,
            second_species_integrals=integrals.second_species,
        )

    def _calculate_temperature(self, intensity_ratio_data):
        return self.temperature_calculatior.calculate(
            intensity_ratio_data.fitted_intensity_ratios
        )

    def _get_partition_functions_from_nist(
        self, temperature
    ) -> _NISTPartitionFunctionData:
        first_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.first_species_atom_name,
            temperature=temperature,
        )

        first_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.first_species_ion_name, temperature=temperature
        )

        second_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.second_species_atom_name,
            temperature=temperature,
        )

        second_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.second_species_ion_name,
            temperature=temperature,
        )

        carrier_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.carrier_species_atom_name,
            temperature=temperature,
        )

        carrier_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.carrier_species_ion_name,
            temperature=temperature,
        )

        return self._NISTPartitionFunctionData(
            first_species_atom,
            first_species_ion,
            second_species_atom,
            second_species_ion,
            carrier_species_atom,
            carrier_species_ion,
        )

    def _get_ionization_energies_from_nist(self):
        first_species = self.ionization_energy_getter.get_data(
            self.config.first_species_atom_name
        )
        second_species = self.ionization_energy_getter.get_data(
            self.config.second_species_atom_name
        )
        carrier_species = self.ionization_energy_getter.get_data(
            self.config.carrier_species_atom_name
        )

        return self._NISTIonizationEnergyData(
            first_species,
            second_species,
            carrier_species,
        )

    def _calculate_atom_concentration(self, intensity_ratio_data, partition_functions):
        return self.atom_concentration_calculatior.calculate(
            fitted_ratios=intensity_ratio_data.fitted_intensity_ratios,
            first_species_atom_partition_function=partition_functions.first_species_atom,
            second_species_atom_partition_function=partition_functions.second_species_atom,
        )

    def _calculate_electron_concentration(
        self, temperature, partition_functions, ionization_energies
    ):
        return self.electron_concentration_calculation.calculate(
            temperature=temperature,
            ionization_energy=ionization_energies.carrier_species,
            partition_function_atom=partition_functions.carrier_species_atom,
            partition_function_ion=partition_functions.carrier_species_ion,
        )

    def _calculate_ion_atom_concentrations(
        self,
        temperature,
        partition_functions,
        ionization_energies,
        electron_concentration,
    ) -> _IonAtomConcentrationData:
        first_species = self.ion_atom_concentration_calculator.calculate(
            electron_concentration=electron_concentration,
            temperature=temperature,
            ionization_energy=ionization_energies.first_species,
            partition_function_atom=partition_functions.first_species_atom,
            partition_function_ion=partition_functions.first_species_ion,
        )

        second_species = self.ion_atom_concentration_calculator.calculate(
            electron_concentration=electron_concentration,
            temperature=temperature,
            ionization_energy=ionization_energies.second_species,
            partition_function_atom=partition_functions.second_species_atom,
            partition_function_ion=partition_functions.second_species_ion,
        )

        return self._IonAtomConcentrationData(
            first_species,
            second_species,
        )

    def _calculate_total_concentration(
        self, atom_concentration, ion_atom_concentrations
    ):
        return self.total_concentration_calculator.calculate(
            atom_concentration,
            ion_atom_concentrations.first_species,
            ion_atom_concentrations.second_species,
        )
