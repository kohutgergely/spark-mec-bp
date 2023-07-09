from spark_mec_bp.application import models
from spark_mec_bp.readers import ASCIISpectrumReader
from spark_mec_bp.lib import (
    PeakFinder,
    PeakFinderConfig,
    SpectrumCorrector,
    SpectrumCorrectorConfig,
    )

from spark_mec_bp.logger import Logger
from spark_mec_bp.calculators import (
    AtomConcentraionCalculator,
    IonAtomConcentraionCalculator,
    TotalConcentrationCalculator,
    VoigtIntegralCalculator,
    VoigtIntegralCalculatorConfig,
    ElectronConcentrationCalculator,
    IntensityRatiosCalculator,
    TemperatureCalculator,
)
from spark_mec_bp.data_preparation.getters import (
    PartitionFunctionDataGetter,
    IonizationEnergyDataGetter,
    AtomicLinesDataGetter,
)

from spark_mec_bp.nist.fetchers import (
    AtomicLinesFetcher,
    AtomicLevelsFetcher,
    IonizationEnergyFetcher,
)

from spark_mec_bp.nist.parsers import (
    AtomicLinesParser,
    AtomicLevelsParser,
    IonizationEnergyParser,
)


class App:
    def __init__(self, config: models.AppConfig):
        self.config = config
        self.logger = Logger().new()
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
            PeakFinderConfig(self.config.peak_finding.minimum_requred_height)
        )
        self.spectrum_corrector = SpectrumCorrector(
            SpectrumCorrectorConfig(
                iteration_limit=self.config.spectrum_correction.iteration_limit,
                ratio=self.config.spectrum_correction.ratio,
                lam=self.config.spectrum_correction.lam,
            )
        )
        self.integral_calculator = VoigtIntegralCalculator(
            VoigtIntegralCalculatorConfig(
                prominance_window_length=self.config.voigt_integration.prominence_window_length
            )
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
        integrals_data = self._caluclate_integrals(spectrum_correction_data, peak_indices)
        intensity_ratio_data = self._calculate_intensity_ratios(atomic_lines, integrals_data)
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

        return models.Result(
            original_spectrum=spectrum,
            corrected_spectrum=spectrum_correction_data.corrected_spectrum,
            baseline=spectrum_correction_data.baseline,
            peak_indices=peak_indices,
            intensity_ratios=intensity_ratio_data.intensity_ratios,
            fitted_intensity_ratios=intensity_ratio_data.fitted_intensity_ratios,
            total_concentration=total_concentration,
            temperature=temperature,
            first_species_atomic_lines=atomic_lines.first_species,
            first_species_integrals_data=integrals_data.first_species,
            second_species_atomic_lines=atomic_lines.second_species,
            second_species_integrals_data=integrals_data.second_species,
        )

    def _read_spectrum(self):
        self.logger.info("Loading input spectrum")

        return self.file_reader.read_spectrum_to_numpy(
            file_path=self.config.spectrum.file_path
        )

    def _correct_spectrum(self, spectrum):
        self.logger.info("Baseline correcting input spectrum")

        return self.spectrum_corrector.correct_spectrum(
            spectrum=spectrum,
            wavelength_column_index=self.config.spectrum.wavelength_column_index,
            intensity_column_index=self.config.spectrum.intensity_column_index,
        )

    def _find_peaks(self, spectrum_correction_data):
        self.logger.info("Finding spectrum peaks")

        return self.peak_finder.find_peak_indices(
            spectrum_correction_data.corrected_spectrum[:, 1]
        )

    def _get_atomic_lines(self) -> models._NISTAtomicLinesData:
        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.first_species.atom_name}"
        )
        first_species = self.atomic_lines_getter.get_data(
            self.config.first_species.atom_name, self.config.first_species.target_peaks
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.second_species.atom_name}"
        )
        second_species = self.atomic_lines_getter.get_data(
            self.config.second_species.atom_name,
            self.config.second_species.target_peaks,
        )

        return models._NISTAtomicLinesData(
            first_species,
            second_species,
        )

    def _caluclate_integrals(
        self, spectrum_correction_data, peak_indices
    ) -> models._IntegralsData:
        self.logger.info("Calculating integrals")

        first_species_data = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.first_species.target_peaks,
        )

        second_species_data = self.integral_calculator.calculate(
            spectrum_correction_data.corrected_spectrum,
            peak_indices,
            self.config.second_species.target_peaks,
        )

        return models._IntegralsData(first_species_data, second_species_data)

    def _calculate_intensity_ratios(self, atomic_lines, integrals_data):
        self.logger.info("Calculating intensity ratios")

        return self.intensity_ratios_calculator.calculate(
            first_species_atomic_lines=atomic_lines.first_species,
            first_species_integrals=integrals_data.first_species.integrals,
            second_species_atomic_lines=atomic_lines.second_species,
            second_species_integrals=integrals_data.second_species.integrals,
        )

    def _calculate_temperature(self, intensity_ratio_data):
        self.logger.info("Calculating temperature")

        return self.temperature_calculatior.calculate(
            intensity_ratio_data.fitted_intensity_ratios
        )

    def _get_partition_functions_from_nist(
        self, temperature
    ) -> models._NISTPartitionFunctionData:
        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.first_species.atom_name}"
        )
        first_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.first_species.atom_name,
            temperature=temperature,
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.first_species.ion_name}"
        )
        first_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.first_species.ion_name, temperature=temperature
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.second_species.atom_name}"
        )
        second_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.second_species.atom_name,
            temperature=temperature,
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.second_species.ion_name}"
        )
        second_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.second_species.ion_name,
            temperature=temperature,
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.carrier_gas.atom_name}"
        )
        carrier_species_atom = self.partition_function_getter.get_data(
            species_name=self.config.carrier_gas.atom_name,
            temperature=temperature,
        )

        self.logger.info(
            f"Retrieving partition function from NIST database for {self.config.carrier_gas.ion_name}"
        )
        carrier_species_ion = self.partition_function_getter.get_data(
            species_name=self.config.carrier_gas.ion_name,
            temperature=temperature,
        )

        return models._NISTPartitionFunctionData(
            first_species_atom,
            first_species_ion,
            second_species_atom,
            second_species_ion,
            carrier_species_atom,
            carrier_species_ion,
        )

    def _get_ionization_energies_from_nist(self) -> models._NISTIonizationEnergyData:
        self.logger.info(
            f"Retrieving ionization_energy from NIST database for {self.config.first_species.atom_name}"
        )
        first_species = self.ionization_energy_getter.get_data(
            self.config.first_species.atom_name
        )

        self.logger.info(
            f"Retrieving ionization_energy from NIST database for {self.config.second_species.atom_name}"
        )
        second_species = self.ionization_energy_getter.get_data(
            self.config.second_species.atom_name
        )

        self.logger.info(
            f"Retrieving ionization_energy from NIST database for {self.config.carrier_gas.atom_name}"
        )
        carrier_species = self.ionization_energy_getter.get_data(
            self.config.carrier_gas.atom_name
        )

        return models._NISTIonizationEnergyData(
            first_species,
            second_species,
            carrier_species,
        )

    def _calculate_atom_concentration(self, intensity_ratio_data, partition_functions):
        self.logger.info("Calculating atom concentration for species")

        return self.atom_concentration_calculatior.calculate(
            fitted_ratios=intensity_ratio_data.fitted_intensity_ratios,
            first_species_atom_partition_function=partition_functions.first_species_atom,
            second_species_atom_partition_function=partition_functions.second_species_atom,
        )

    def _calculate_electron_concentration(
        self, temperature, partition_functions, ionization_energies
    ):
        self.logger.info("Estimating electron concentration")

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
    ) -> models._IonAtomConcentrationData:
        self.logger.info("Calculating ion-atom concentration")

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

        return models._IonAtomConcentrationData(
            first_species,
            second_species,
        )

    def _calculate_total_concentration(
        self, atom_concentration, ion_atom_concentrations
    ):
        self.logger.info("Calculating total concentration")

        return self.total_concentration_calculator.calculate(
            atom_concentration,
            ion_atom_concentrations.first_species,
            ion_atom_concentrations.second_species,
        )
