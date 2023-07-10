import numpy as np


class LinePairChecker:
    def check_line_pairs(self, atomic_lines: np.ndarray, integrals: np.ndarray, temperature: float) -> np.ndarray:
        intratio = integrals / integrals[:, np.newaxis]
        dataratio = np.divide(
            (
                ((atomic_lines[:, 2] * atomic_lines[:, 1]) / atomic_lines[:, 0])
                * np.exp(-atomic_lines[:, 3] / (0.695035 * temperature))
            ),
            (
                ((atomic_lines[:, 2] * atomic_lines[:, 1]) / atomic_lines[:, 0])
                * np.exp(-atomic_lines[:, 3] / (0.695035 * temperature))
            )[:, np.newaxis],
        )

        return np.divide(dataratio - intratio, dataratio).T
