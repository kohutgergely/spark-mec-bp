import numpy as np
from scipy.signal import find_peaks


class PeakFinder:
    def __init__(self, required_height: int):
        self.required_height = required_height

    def find_peak_indices(self, intensities: np.array) -> np.array:
        peak_indices, _ = find_peaks(
            intensities, self.required_height, threshold=0, width=2
        )

        return peak_indices
