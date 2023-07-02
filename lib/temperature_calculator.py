class TemperatureCalculator:
    def calculate(self, fitted_ratios):
        return 1 / (0.695035 * fitted_ratios[0])
