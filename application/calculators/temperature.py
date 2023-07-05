import numpy as np


class TemperatureCalculator:
    def calculate(self, fitted_ratios: np.ndarray) -> float:
        return 1 / (0.695035 * fitted_ratios[0])
