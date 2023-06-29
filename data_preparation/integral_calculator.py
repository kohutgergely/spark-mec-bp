import numpy as np
from data_preparation.peak_finder import PeakFinder
from scipy.signal import peak_prominences
from lmfit.models import PseudoVoigtModel


class IntegralCalculator:
    def __init__(self, peak_finder: PeakFinder, prominance_wlen: int) -> None:
        self.peak_finder = peak_finder
        self.prominance_wlen = prominance_wlen

    def calculate_integrals(self, spectrum: np.ndarray, target_peaks: np.array):
        peaks = self.peak_finder.find_peak_indices(spectrum[:, 1])
        self.wavelength = spectrum[:, 0]
        self.Y = spectrum[:, 1]
        self.all_peaks = np.stack((peaks,
                                   self.wavelength[peaks]), axis=-1)

        voigt_integrals = []
        selected_peak_indices = self._find_nearest_indices(
            self.all_peaks, target_peaks)
        for peak_index in selected_peak_indices:
            area = self._caluclate_voigt_integral(peak_index)
            voigt_integrals.append(area)

        return np.array(voigt_integrals)

    def _find_nearest_indices(self, spectrum, target_peaks):
        return np.abs(spectrum[:, 1] -
                      target_peaks[:, np.newaxis]).argmin(axis=1)

    def _caluclate_voigt_integral(self, peak_index):
        selected_peak_idx_array = np.array(
            [int(self.all_peaks[peak_index, 0])])

        prominences = peak_prominences(
            self.Y, selected_peak_idx_array, wlen=self.prominance_wlen)
        start_index = int(prominences[1])
        end_index = 2 * \
            int(self.all_peaks[peak_index, 0])-int(prominences[1])
        peak_wavelength = self.wavelength[start_index:end_index+1]
        peak_spectrum = self.Y[start_index:end_index+1]
        voigt_model = PseudoVoigtModel()
        params = voigt_model.guess(peak_spectrum, x=peak_wavelength)
        voigt_fit = voigt_model.fit(
            peak_spectrum, params, x=peak_wavelength)
        return np.trapz(voigt_fit.best_fit, peak_wavelength)
