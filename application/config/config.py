import numpy as np
from dataclasses import dataclass


@dataclass
class ApplicationConfig:
    spectrum_path: str
    spectrum_wavelength_column_index: int
    spectrum_intensity_column_index: int
    first_species_target_peaks: np.ndarray
    second_species_target_peaks: np.ndarray
    first_species_atom_name: str
    first_species_ion_name: str
    second_species_atom_name: str
    second_species_ion_name: str
    carrier_species_atom_name: str
    carrier_species_ion_name: str
    prominence_window_length: int
    peak_minimum_requred_height: int
