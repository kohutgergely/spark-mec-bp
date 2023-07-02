from dataclasses import dataclass

import numpy as np


@dataclass
class IntensityRatiosData:
    intensity_ratios: np.ndarray
    fitted_intensity_ratios: np.ndarray


class IntensityRatiosCalculator:
    def calculate(
        self,
        first_species_atomic_lines: np.ndarray,
        first_species_integrals: np.ndarray,
        second_species_atomic_lines: np.ndarray,
        second_species_integrals: np.ndarray,
    ) -> IntensityRatiosData:
        intensity_ratios = self._calculate_intensity_ratios(
            first_species_atomic_lines,
            first_species_integrals,
            second_species_atomic_lines,
            second_species_integrals,
        )
        fitted_ratios = self._fit_intensity_ratios(intensity_ratios)

        return IntensityRatiosData(
            intensity_ratios=intensity_ratios,
            fitted_intensity_ratios=fitted_ratios,
        )

    def _calculate_intensity_ratios(
        self,
        first_species_atomic_lines,
        first_species_integrals,
        second_species_atomic_lines,
        second_species_integrals,
    ):
        first_species_ln = self._get_ln(
            first_species_atomic_lines, first_species_integrals
        )
        second_species_ln = self._get_ln(
            second_species_atomic_lines, second_species_integrals
        )
        ln_ratios = np.log(first_species_ln[:, np.newaxis] / second_species_ln)
        e_values = (
            second_species_atomic_lines[:, 3]
            - first_species_atomic_lines[:, 3][:, np.newaxis]
        )

        return np.stack((e_values.flatten(), ln_ratios.flatten()), axis=-1)

    def _fit_intensity_ratios(self, intensity_ratios):
        return np.polyfit(intensity_ratios[:, 0], intensity_ratios[:, 1], 1)

    def _get_ln(self, species_data, integrals):
        return (integrals * species_data[:, 0] * 1e-7) / (
            species_data[:, 2] * species_data[:, 1]
        )
