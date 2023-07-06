class TotalConcentrationCalculator:
    def calculate(
        self,
        atom_concentration: float,
        first_species_ion_atom_concentration: float,
        second_species_ion_atom_concentration: float,
    ) -> float:
        return (
            (first_species_ion_atom_concentration + 1)
            / (second_species_ion_atom_concentration + 1)
        ) * atom_concentration
