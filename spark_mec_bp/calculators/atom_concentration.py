import numpy as np


class AtomConcentraionCalculator:
    def calculate(
        self,
        fitted_ratios: np.ndarray,
        first_species_atom_partition_function: float,
        second_species_atom_partition_function: float,
    ) -> float:
        return np.exp(fitted_ratios[1]) * (
            first_species_atom_partition_function
            / second_species_atom_partition_function
        )
