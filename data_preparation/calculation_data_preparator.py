import numpy as np
from dataclasses import dataclass

from data_preparation.spectrum_correction import SpectrumCorrector
from data_preparation.spectrum_reader import SpectrumReader
from data_preparation.peak_finder import PeakFinder
from data_preparation.integral_calculator import IntegralCalculator
from data_preparation.atomic_lies_data_preparator import AtomicLinesDataPreparator
from nist_sdk.atomic_lines import AtomicLinesFetcher
from parsers.atomic_lines import AtomicLinesParser


@dataclass
class CalculationDataPreparatorConfig:
    spectrum: np.ndarray
    species_name: str
    species_target_peak_wavelengths: list
    peak_hight_for_integral_calculation: int = 100
    prominance_window_length_for_integral_calculation: int = 40


class CalculationDataPreparator:
    def __init__(self, config: CalculationDataPreparatorConfig):
        self.config = config
        self.peak_finder = PeakFinder(
            required_height=config.peak_hight_for_integral_calculation
        )
        self.integral_calculator = IntegralCalculator(
            peak_finder=self.peak_finder,
            prominance_window_length=config.prominance_window_length_for_integral_calculation
        )
        self.atomic_lines_data_preparator = AtomicLinesDataPreparator(
            atomic_lines_fetcher=AtomicLinesFetcher(),
            atomic_lines_parser=AtomicLinesParser()
        )

    def prepare_calculation_data(self):
        atomic_lines_data = self.atomic_lines_data_preparator.prepare_atomic_lines_data(
            self.config.species_name, target_peaks=self.config.species_target_peak_wavelengths)
        integrals = self.integral_calculator.calculate_integrals(
            self.config.spectrum, self.config.species_target_peak_wavelengths)

        return self._combine_data(atomic_lines_data, integrals)

    def _combine_data(self, atomic_lines_data, integrals):
        return np.concatenate((self.config.species_target_peak_wavelengths[:, np.newaxis], atomic_lines_data, integrals[:, np.newaxis]), axis=1)
