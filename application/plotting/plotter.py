from matplotlib import pyplot as plt
from scipy.signal import peak_prominences


class Plotter:
    def plot_original_spectrum(self, spectrum, spectrum_correction_data):
        plt.plot(spectrum[:, 0], spectrum[:, 1])
        plt.plot(spectrum[:, 0], spectrum_correction_data.baseline)
        plt.xlim([310, 800])
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity (a.u.)")
        plt.title("Original spectrum and baseline")
        plt.figure()

    def plot_saha_boltzmann_line_pairs(self, intensity_ratios_data):
        plt.plot(
            intensity_ratios_data.intensity_ratios[:, 0],
            intensity_ratios_data.intensity_ratios[:, 1],
            "x",
        )
        plt.plot(
            intensity_ratios_data.intensity_ratios[:, 0],
            intensity_ratios_data.intensity_ratios[:, 0]
            * intensity_ratios_data.fitted_intensity_ratios[0]
            + intensity_ratios_data.fitted_intensity_ratios[1],
        )
        plt.xlabel("Difference of upper energy levels (cm-1)")
        plt.ylabel("log of line intensity ratios (a.u.)")
        plt.title("Saha-Boltzmann line-pair plot for Au I and Ag I lines")
        plt.figure()

    def plot_baseline_corrected_spectrum_with_the_major_peaks(
        self,
        spectrum_correction_data,
        peak_indices,
        wlen,
        xlim,
        ylim,
    ):
        left = peak_prominences(
            spectrum_correction_data.corrected_spectrum[:, 1],
            peak_indices,
            wlen=wlen,
        )[
            1
        ]  # lower integration limit of each line
        right = peak_prominences(
            spectrum_correction_data.corrected_spectrum[:, 1],
            peak_indices,
            wlen=wlen,
        )[
            2
        ]  # upper integration limit of each line

        plt.plot(
            spectrum_correction_data.corrected_spectrum[:, 0],
            spectrum_correction_data.corrected_spectrum[:, 1],
        )
        plt.plot(
            spectrum_correction_data.corrected_spectrum[peak_indices, 0],
            spectrum_correction_data.corrected_spectrum[peak_indices, 1],
            "x",
        )
        plt.plot(
            spectrum_correction_data.corrected_spectrum[left, 0],
            spectrum_correction_data.corrected_spectrum[left, 1],
            "o",
        )
        plt.plot(
            spectrum_correction_data.corrected_spectrum[right, 0],
            spectrum_correction_data.corrected_spectrum[right, 1],
            "o",
        )
        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity (a.u.)")
        plt.title("Baseline corrected spectrum with the major peaks")
        plt.figure()
