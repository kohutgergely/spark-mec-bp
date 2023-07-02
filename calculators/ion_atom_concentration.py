import numpy as np

from data_preparation.getters import (
    PartitionFunctionDataGetter,
    IonizationEnergyDataGetter,
)

m = 9.10938291e-28  # g
k = 1.3807e-16  # cm2 g s-2 K-1
h = 6.6261e-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458e10  # cm/s
p = 1e6  # g/s^2 m

X = (2 * np.pi * m * k) / np.power(h, 2)  # constant in Saha-Boltzmann equation


class IonAtomConcentraionCalculator:
    def __init__(
        self,
        partition_function_data_getter: PartitionFunctionDataGetter,
        ionization_energy_data_getter: IonizationEnergyDataGetter,
    ) -> None:
        self._partition_function_data_getter = partition_function_data_getter
        self._ionization_energy_data_getter = ionization_energy_data_getter

    def calculate(
        self,
        electron_concentration: float,
        temperature: float,
        species_name: str,
        partition_function_atom_name: str,
        partition_function_ion_name: str,
    ):
        ionization_energy = self._ionization_energy_data_getter.get_data(species_name)
        ion_concentration = self._saha_boltzmann(
            electron_concentration, temperature, ionization_energy
        )

        atom_partition_function = self._partition_function_data_getter.get_data(
            partition_function_atom_name, temperature
        )
        ion_partition_function = self._partition_function_data_getter.get_data(
            partition_function_ion_name, temperature
        )

        return ion_concentration * (ion_partition_function / atom_partition_function)

    def _saha_boltzmann(self, electron_concentration, temperature, ionization_energy):
        return (
            2
            * (1 / electron_concentration)
            * np.power(X, 1.5)
            * np.power(temperature, 1.5)
            * np.exp(-(ionization_energy / (temperature * 0.695028)))
        )  # number concentration of argon ions
