from dataclasses import dataclass
from typing import List

import numpy as np

from scipy.signal import peak_prominences
from lmfit.models import PseudoVoigtModel


@dataclass
class VoigtIntegralFit:
    fit: np.ndarray
    wavelengths: np.ndarray
    intensities: np.ndarray


@dataclass
class VoigtIntegralData:
    integrals: np.ndarray
    fits: List[VoigtIntegralFit]


@dataclass
class VoigtIntegralCalculatorConfig:
    prominance_window_length: int


class VoigtIntegralCalculator:
    def __init__(self, config: VoigtIntegralCalculatorConfig) -> None:
        self.config = config

    def calculate(self, spectrum: np.ndarray, peak_index_table: np.ndarray, target_wavelengths: np.array) -> np.ndarray:
        wavelengths = spectrum[:, 0]
        intensities = spectrum[:, 1]
        peak_index_table_with_wavelengths = self._combine_peak_indices_with_wavelengths(
            wavelengths, peak_index_table
        )

        voigt_integrals, voigt_fits = [], []
        peak_indices_to_integrate = (
            self._find_peak_indices_nearest_to_target_wavelengths(
                peak_index_table_with_wavelengths, target_wavelengths
            )
        )

        for peak_index in peak_indices_to_integrate:
            area, voigt_fit = self._caluclate_voigt_integral(
                peak_index, peak_index_table_with_wavelengths, wavelengths, intensities
            )
            voigt_integrals.append(area)
            voigt_fits.append(voigt_fit)

        return VoigtIntegralData(
            integrals=np.array(voigt_integrals),
            fits=voigt_fits,
        )

    def _combine_peak_indices_with_wavelengths(
        self, wavelengths, spectrum_peak_indices
    ):
        return np.stack(
            (spectrum_peak_indices, wavelengths[spectrum_peak_indices]), axis=-1
        )

    def _find_peak_indices_nearest_to_target_wavelengths(
        self, peak_index_table_with_wavelengths, target_wavelengths
    ):
        return np.abs(
            peak_index_table_with_wavelengths[:, 1] - target_wavelengths[:, np.newaxis]
        ).argmin(axis=1)

    def _caluclate_voigt_integral(
        self,
        peak_index_in_peak_table,
        peak_index_table_with_wavelengths,
        wavelengths,
        intensities,
    ):
        peak_index_in_spectrum = int(
            peak_index_table_with_wavelengths[peak_index_in_peak_table, 0]
        )
        prominences = peak_prominences(
            intensities, [peak_index_in_spectrum], wlen=self.config.prominance_window_length
        )
        peak_start_index = int(prominences[1])
        peak_end_index = 2 * int(
            peak_index_table_with_wavelengths[peak_index_in_peak_table, 0]
        ) - int(prominences[1])
        peak_wavelengths = wavelengths[peak_start_index: peak_end_index + 1]
        peak_intensities = intensities[peak_start_index: peak_end_index + 1]
        voigt_model = PseudoVoigtModel()
        params = voigt_model.guess(peak_intensities, x=peak_wavelengths)
        voigt_fit = voigt_model.fit(peak_intensities, params, x=peak_wavelengths)

        return np.trapz(voigt_fit.best_fit, peak_wavelengths), VoigtIntegralFit(
            intensities=peak_intensities,
            wavelengths=peak_wavelengths,
            fit=voigt_fit.best_fit
        )
