import numpy as np


m = 9.10938291e-28  # g
k = 1.3807e-16  # cm2 g s-2 K-1
h = 6.6261e-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458e10  # cm/s
p = 1e6  # g/s^2 m
X = (2 * np.pi * m * k) / np.power(h, 2)  # constant in Saha-Boltzmann equation


class ElectronConcentrationCalculator:
    def calculate(
        self,
        temperature: float,
        ionization_energy: float,
        partition_function_atom: float,
        partition_function_ion: float,
    ) -> float:
        ion_neutral_atom_partition_function_ratio = (
            partition_function_ion / partition_function_atom
        )

        return (
            -1
            * self._B(
                temperature,
                ionization_energy,
                ion_neutral_atom_partition_function_ratio,
            )
            + np.sqrt(
                self._D(
                    temperature,
                    ionization_energy,
                    ion_neutral_atom_partition_function_ratio,
                )
            )
        ) / 2

    def _D(
        self, temperature, ionization_energy, ion_neutral_atom_partition_function_ratio
    ):
        return np.power(
            self._B(
                temperature,
                ionization_energy,
                ion_neutral_atom_partition_function_ratio,
            ),
            2,
        ) + 4 * 1 * self._C(
            temperature, ionization_energy, ion_neutral_atom_partition_function_ratio
        )

    def _B(
        self, temperature, ionization_energy, ion_neutral_atom_partition_function_ratio
    ):
        return (
            4
            * ion_neutral_atom_partition_function_ratio
            * self._SB2(temperature, ionization_energy)
        )

    def _C(
        self, temperature, ionization_energy, ion_neutral_atom_partition_function_ratio
    ):
        return (
            2
            * ion_neutral_atom_partition_function_ratio
            * self._SB2(temperature, ionization_energy)
            * (p / (temperature * k))
        )

    def _SB2(self, temperature, ionization_energy):
        return (
            2
            * np.power(X, 1.5)
            * np.power(temperature, 1.5)
            * np.exp(-(ionization_energy / (temperature * 0.695028)))
        )
