from dataclasses import dataclass

import numpy as np
from data_preparation.getters import PartitionFunctionDataGetter


@dataclass
class AtomConcentrationData:
    intensity_ratios: np.ndarray
    fitted_intensity_ratios: np.ndarray
    temperature: float
    atom_concentration_ratio: float


class AtomConcentraionCalculator:
    def __init__(
        self,
        partition_function_data_getter: PartitionFunctionDataGetter,
    ) -> None:
        self._partition_function_data_getter = partition_function_data_getter

    def calculate(
        self,
        first_species_name: str,
        first_species_atomic_lines: np.ndarray,
        first_species_integrals: np.ndarray,
        second_species_name: str,
        second_species_atomic_lines: np.ndarray,
        second_species_integrals: np.ndarray,
    ):
        intensity_ratios = self._calculate_intensity_ratios(
            first_species_atomic_lines,
            first_species_integrals,
            second_species_atomic_lines,
            second_species_integrals,
        )
        fitted_ratios = self._fit_intensity_ratios(intensity_ratios)
        temperature = self._caculate_temperature(fitted_ratios)
        atom_concentration_ratio = self._calculate_atom_concentration_ratio(
            fitted_ratios, temperature, first_species_name, second_species_name
        )

        self._output = AtomConcentrationData(
            intensity_ratios=intensity_ratios,
            fitted_intensity_ratios=fitted_ratios,
            temperature=temperature,
            atom_concentration_ratio=atom_concentration_ratio,
        )

        return self._output

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

    def _caculate_temperature(self, fitted_ratios):
        return 1 / (0.695035 * fitted_ratios[0])

    def _calculate_atom_concentration_ratio(
        self, fitted_ratios, temperature, first_species_name, second_species_name
    ):
        partition_function_first_species = (
            self._partition_function_data_getter.get_data(
                first_species_name, temperature
            )
        )
        partition_function_second_species = (
            self._partition_function_data_getter.get_data(
                second_species_name, temperature
            )
        )
        return np.exp(fitted_ratios[1]) * (
            partition_function_first_species / partition_function_second_species
        )

    def _get_ln(self, species_data, integrals):
        return (integrals * species_data[:, 0] * 1e-7) / (
            species_data[:, 2] * species_data[:, 1]
        )
