import numpy as np
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm


class SpectrumCorrector:
    def __init__(
        self,
        spectrum: np.ndarray,
        wavelength_column_index=0,
        intensity_column_index=1
    ) -> None:
        self.spectrum = spectrum
        self.wavelength_column_index = wavelength_column_index
        self.intensity_column_index = intensity_column_index
        self._baseline = None

    def correct_spectrum(self) -> np.ndarray:
        wavelengths = self.spectrum[:, self.wavelength_column_index]
        intensities = self.spectrum[:, self.intensity_column_index]
        corrected_intensities = intensities - \
            self.get_baseline()

        return np.stack((wavelengths, corrected_intensities), axis=-1)

    def get_baseline(self):
        if self._baseline is None:
            self._baseline = self._calculate_baseline()

        return self._baseline

    def _calculate_baseline(self):
        L = len(self.spectrum[:, self.intensity_column_index])

        diag = np.ones(L - 2)
        D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)

        # The transposes are flipped w.r.t the Algorithm on pg. 252
        H = 1000000 * D.dot(D.T)

        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)

        crit = 1
        count = 0

        while crit > 1E-5:
            z = linalg.spsolve(
                W + H, W * self.spectrum[:, self.intensity_column_index])
            d = self.spectrum[:, self.intensity_column_index] - z
            dn = d[d < 0]

            m = np.mean(dn)
            s = np.std(dn)

            w_new = 1 / (1 + np.exp(2 * (d - (2*s - m))/s))

            crit = norm(w_new - w) / norm(w)

            w = w_new
            # Do not create a new matrix, just update diagonal values
            W.setdiag(w)

            count += 1

            if count > 50:
                print('Maximum number of iterations exceeded')
                break

        return z
