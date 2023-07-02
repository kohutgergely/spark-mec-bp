import numpy as np
from dataclasses import dataclass

from lib.peak_finder import PeakFinder
from calculators.integrals import IntegralsCalculator
from data_preparation.getters.atomic_lines_data_getter import AtomicLinesDataGetter
from nist.fetchers import AtomicLinesFetcher
from nist.parsers import AtomicLinesParser


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
        self.integral_calculator = IntegralsCalculator(
            peak_finder=self.peak_finder,
            prominance_window_length=config.prominance_window_length_for_integral_calculation
        )
        self.atomic_lines_data_getter = AtomicLinesDataGetter(
            atomic_lines_fetcher=AtomicLinesFetcher(),
            atomic_lines_parser=AtomicLinesParser()
        )

    def prepare_calculation_data(self):
        atomic_lines_data = self.atomic_lines_data_getter.get_data(
            self.config.species_name, target_peaks=self.config.species_target_peak_wavelengths)
        integrals = self.integral_calculator.calculate_integrals(
            self.config.spectrum, self.config.species_target_peak_wavelengths)

        return self._combine_data(atomic_lines_data, integrals)

    def _combine_data(self, atomic_lines_data, integrals):
        return np.concatenate((atomic_lines_data, integrals[:, np.newaxis]), axis=1)
