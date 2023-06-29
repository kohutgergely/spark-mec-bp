import numpy as np


class SpectrumReader:
    def read_ascii_spectrum_to_numpy(self, file_path: str) -> np.ndarray:
        with open(file_path) as file:
            return np.loadtxt(file)
