from dataclasses import dataclass
import numpy as np
from scipy.signal import find_peaks


@dataclass
class PeakFinderConfig:
    required_height: int


class PeakFinder:
    def __init__(self, config: PeakFinderConfig) -> None:
        self.config = config

    def find_peak_indices(self, intensities: np.array) -> np.ndarray:
        peak_indices, _ = find_peaks(
            intensities, self.config.required_height, threshold=0, width=2
        )

        return peak_indices
