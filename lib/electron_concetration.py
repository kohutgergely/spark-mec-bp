import numpy as np
from data_preparation.getters import (
    PartitionFunctionDataGetter,
    IonizationEnergyDataGetter,
)

m = 9.10938291E-28  # g
k = 1.3807E-16  # cm2 g s-2 K-1
h = 6.6261E-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458E10  # cm/s
p = 1E6  # g/s^2 m
X = (2*np.pi*m*k)/np.power(h, 2)  # constant in Saha-Boltzmann equation


class ElectronConcentrationCalculator:
    def __init__(
        self,
        partition_function_data_getter: PartitionFunctionDataGetter,
        ionization_energy_data_getter: IonizationEnergyDataGetter,

    ) -> None:
        self._partition_function_data_getter = partition_function_data_getter
        self._ionization_energy_data_getter = ionization_energy_data_getter

    def calculate(self, temperature, species_name, partition_function_atom, partition_function_ion):
        partition_function_neutral_atom = self._partition_function_data_getter.get_data(
            partition_function_atom, temperature)
        partition_function_ion = self._partition_function_data_getter.get_data(
            partition_function_ion, temperature)
        ionization = self._ionization_energy_data_getter.get_data(species_name)
        ion_neutral_atom_partition_function_ratio = partition_function_ion / \
            partition_function_neutral_atom

        return (-1*self._B(temperature, ionization, ion_neutral_atom_partition_function_ratio) +
                np.sqrt(self._D(temperature, ionization, ion_neutral_atom_partition_function_ratio)))/(2*1)

    def _D(self, temperature, ionization, ion_neutral_atom_partition_function_ratio):
        return np.power(self._B(temperature, ionization, ion_neutral_atom_partition_function_ratio),
                        2) + 4*1*self._C(temperature, ionization, ion_neutral_atom_partition_function_ratio)

    def _B(self, temperature, ionization, ion_neutral_atom_partition_function_ratio):
        return 4*ion_neutral_atom_partition_function_ratio * \
            self._SB2(temperature, ionization)

    def _C(self, temperature, ionization, ion_neutral_atom_partition_function_ratio):
        return 2*ion_neutral_atom_partition_function_ratio * \
            self._SB2(temperature, ionization)*(p/(temperature*k))

    def _SB2(self, temperature, ionization):
        return 2*np.power(X, 1.5)*np.power(temperature, 1.5) * \
            np.exp(-(ionization/(temperature*0.695028)))
