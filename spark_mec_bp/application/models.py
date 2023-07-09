from dataclasses import dataclass
import numpy as np

from spark_mec_bp.calculators import VoigtIntegralData


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
class SpectrumCorrectionConfig:
    iteration_limit: int = 50
    ratio: float = 1e-5
    lam: int = 1000000


@dataclass
class PeakFindingConfig:
    minimum_requred_height: int


@dataclass
class VoigtIntegrationConfig:
    prominence_window_length: int


@dataclass
class SpeciesConfig:
    atom_name: str
    ion_name: str
    target_peaks: list

    def __post_init__(self):
        self.target_peaks = np.array(self.target_peaks)


@dataclass
class SpectrumConfig:
    file_path: str
    wavelength_column_index: int
    intensity_column_index: int


@dataclass
class CarrierGasConfig:
    atom_name: str
    ion_name: int


@dataclass
class AppConfig:
    spectrum: SpectrumConfig
    first_species: SpeciesConfig
    second_species: SpeciesConfig
    carrier_gas: CarrierGasConfig
    spectrum_correction: SpectrumCorrectionConfig
    peak_finding: PeakFindingConfig
    voigt_integration: VoigtIntegrationConfig


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
