import numpy as np

m = 9.10938291e-28  # g
k = 1.3807e-16  # cm2 g s-2 K-1
h = 6.6261e-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458e10  # cm/s
p = 1e6  # g/s^2 m

X = (2 * np.pi * m * k) / np.power(h, 2)  # constant in Saha-Boltzmann equation


class IonAtomConcentraionCalculator:
    def calculate(
        self,
        electron_concentration: float,
        temperature: float,
        ionization_energy: float,
        partition_function_atom: float,
        partition_function_ion: float,
    ) -> float:
        ion_concentration = self._saha_boltzmann(
            electron_concentration, temperature, ionization_energy
        )

        return ion_concentration * (partition_function_ion / partition_function_atom)

    def _saha_boltzmann(self, electron_concentration, temperature, ionization_energy):
        return (
            2
            * (1 / electron_concentration)
            * np.power(X, 1.5)
            * np.power(temperature, 1.5)
            * np.exp(-(ionization_energy / (temperature * 0.695028)))
        )
