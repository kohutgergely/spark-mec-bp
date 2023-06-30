import numpy as np
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm


class SpectrumCorrector:
    def correct_spectrum(
        self,
        spectrum: np.ndarray,
        wavelength_column_index=0,
        intensity_column_index=1
    ) -> np.ndarray:
        wavelengths = spectrum[:, wavelength_column_index]
        intensities = spectrum[:, intensity_column_index]
        corrected_intensities = intensities - \
            self.calculate_baseline(spectrum, intensity_column_index)

        return np.stack((wavelengths, corrected_intensities), axis=-1)

    def calculate_baseline(self, spectrum, intensity_column_index):
        L = len(spectrum[:, intensity_column_index])

        diag = np.ones(L - 2)
        D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)

        H = 1000000 * D.dot(D.T)

        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)

        crit = 1
        count = 0

        while crit > 1E-5:
            z = linalg.spsolve(
                W + H, W * spectrum[:, intensity_column_index])
            d = spectrum[:, intensity_column_index] - z
            dn = d[d < 0]

            m = np.mean(dn)
            s = np.std(dn)

            w_new = 1 / (1 + np.exp(2 * (d - (2*s - m))/s))

            crit = norm(w_new - w) / norm(w)

            w = w_new
            W.setdiag(w)

            count += 1

            if count > 50:
                break

        return z
