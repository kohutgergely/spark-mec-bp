import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import peak_prominences
from typing import List

from spark_mec_bp.calculators import VoigtIntegralFit


class Plotter:
    def plot_original_spectrum(
        self,
        spectrum: np.ndarray,
        baseline: np.ndarray,
        spectrum_intensity_column_index: int
    ) -> None:
        plt.plot(spectrum[:, 0], spectrum[:, spectrum_intensity_column_index])
        plt.plot(spectrum[:, 0], baseline)
        plt.xlim([310, 800])
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity (a.u.)")
        plt.title("Original spectrum and baseline")
        plt.figure()

    def plot_saha_boltzmann_line_pairs(self, intensity_ratios: np.ndarray, fitted_intensity_ratios: np.ndarray):
        plt.plot(
            intensity_ratios[:, 0],
            intensity_ratios[:, 1],
            "x",
        )
        plt.plot(
            intensity_ratios[:, 0],
            intensity_ratios[:, 0]
            * fitted_intensity_ratios[0]
            + fitted_intensity_ratios[1],
        )
        plt.xlabel("Difference of upper energy levels (cm-1)")
        plt.ylabel("log of line intensity ratios (a.u.)")
        plt.title("Multi-element combinatory Boltzmann plot for Au I and Ag I lines")
        plt.figure()

    def plot_baseline_corrected_spectrum_with_the_major_peaks(
        self,
        corrected_spectrum: np.ndarray,
        peak_indices: np.ndarray,
        wlen: int,
        xlim: List[int],
        ylim: List[int],
    ):
        _, left, right = peak_prominences(
            corrected_spectrum[:, 1],
            peak_indices,
            wlen=wlen,
        )
        plt.plot(
            corrected_spectrum[:, 0],
            corrected_spectrum[:, 1],
        )
        plt.plot(
            corrected_spectrum[peak_indices, 0],
            corrected_spectrum[peak_indices, 1],
            "x",
        )
        plt.plot(
            corrected_spectrum[left, 0],
            corrected_spectrum[left, 1],
            "o",
        )
        plt.plot(
            corrected_spectrum[right, 0],
            corrected_spectrum[right, 1],
            "o",
        )
        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity (a.u.)")
        plt.title("Baseline corrected spectrum with the major peaks")
        plt.figure()

    def plot_voigt_fit(self, species_name: str, voigt_integral_fits: List[VoigtIntegralFit]):
        for voigt_integral_fit in voigt_integral_fits:
            plt.title(f"Voigt fit for {species_name}")
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Intensity (a.u.)")
            plt.plot(voigt_integral_fit.wavelengths, voigt_integral_fit.intensities, 'o', label='Original spectrum')
            plt.plot(voigt_integral_fit.wavelengths, voigt_integral_fit.fit, label='Voigt fit')
            plt.legend()
            plt.show()
