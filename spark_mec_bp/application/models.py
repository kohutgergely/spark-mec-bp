from dataclasses import dataclass
import numpy as np

from spark_mec_bp.calculators import VoigtIntegralData


@dataclass
class Config:
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


@dataclass
class Result:
    original_spectrum: np.ndarray
    corrected_spectrum: np.ndarray
    baseline: np.ndarray
    peak_indices: np.ndarray
    intensity_ratios: np.ndarray
    fitted_intensity_ratios: np.ndarray
    total_concentration: float
    temperature: float
    first_species_atomic_lines: np.ndarray
    second_species_atomic_lines: np.ndarray
    first_species_integrals_data: VoigtIntegralData
    second_species_integrals_data: VoigtIntegralData


@dataclass
class _NISTAtomicLinesData:
    first_species: np.ndarray
    second_species: np.ndarray


@dataclass
class _NISTPartitionFunctionData:
    first_species_atom: float
    first_species_ion: float
    second_species_atom: float
    second_species_ion: float
    carrier_species_atom: float
    carrier_species_ion: float


@dataclass
class _NISTIonizationEnergyData:
    first_species: float
    second_species: float
    carrier_species: float


@dataclass
class _IntegralsData:
    first_species: VoigtIntegralData
    second_species: VoigtIntegralData


@dataclass
class _IonAtomConcentrationData:
    first_species: float
    second_species: float
