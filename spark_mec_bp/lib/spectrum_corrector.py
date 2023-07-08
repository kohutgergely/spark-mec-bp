import warnings

import numpy as np
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm
from dataclasses import dataclass

warnings.filterwarnings("ignore")


@dataclass
class SpectrumCorrectionData:
    corrected_spectrum: np.ndarray
    baseline: np.ndarray


@dataclass
class SpectrumCorrectorConfig:
    iteration_limit: int = 50
    ratio: float = 1e-5
    lam: int = 1000000


class SpectrumCorrector:
    def __init__(self, config: SpectrumCorrectorConfig) -> None:
        self.config = config

    def correct_spectrum(
        self, spectrum: np.ndarray, wavelength_column_index: int = 0, intensity_column_index: int = 1
    ) -> SpectrumCorrectionData:
        wavelengths = spectrum[:, wavelength_column_index]
        intensities = spectrum[:, intensity_column_index]
        baseline = self._calculate_baseline(intensities)
        corrected_intensities = intensities - baseline

        return SpectrumCorrectionData(
            corrected_spectrum=np.stack((wavelengths, corrected_intensities), axis=-1),
            baseline=baseline,
        )

    def _calculate_baseline(self, intensities):
        L = len(intensities)

        diag = np.ones(L - 2)
        D = sparse.spdiags([diag, -2 * diag, diag], [0, -1, -2], L, L - 2)

        H = self.config.lam * D.dot(D.T)

        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)

        crit = 1
        count = 0

        while crit > self.config.ratio:
            z = linalg.spsolve(W + H, W * intensities)
            d = intensities - z
            dn = d[d < 0]

            m = np.mean(dn)
            s = np.std(dn)

            w_new = 1 / (1 + np.exp(2 * (d - (2 * s - m)) / s))

            crit = norm(w_new - w) / norm(w)

            w = w_new
            W.setdiag(w)

            count += 1

            if count > self.config.iteration_limit:
                break

        return z
