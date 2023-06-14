import yaml
import numpy as np
import lib.helper_functions as helper_functions
import logging
import warnings

from scipy.signal import find_peaks, peak_prominences
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm
from matplotlib import pyplot as plt


def baseline_arPLS(y, ratio, lam, niter, full_output=False):

    L = len(y)

    diag = np.ones(L - 2)
    D = sparse.spdiags([diag, -2 * diag, diag], [0, -1, -2], L, L - 2)

    # The transposes are flipped w.r.t the Algorithm on pg. 252
    H = lam * D.dot(D.T)

    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)

    crit = 1
    count = 0
    while crit > ratio:

        z = linalg.spsolve(W + H, W * y)
        d = y - z
        dn = d[d < 0]

        m = np.mean(dn)
        s = np.std(dn)

        w_new = 1 / (1 + np.exp(2 * (d - (2 * s - m)) / s))
        crit = norm(w_new - w) / norm(w)

        w = w_new
        W.setdiag(w)  # Do not create a new matrix, just update diagonal values

        count += 1

        if count > niter:
            logging.info('Maximum number of iterations exceeded')
            break

    if full_output:
        info = {'num_iter': count, 'stop_criterion': crit}
        return z, d, info
    else:
        return z


def corr_spectrum(spectrum, ratio, lam, niter):
    X = spectrum[:, 0]
    Y = spectrum[:, 1]
    Y_corr = Y - baseline_arPLS(Y, ratio, lam, niter)
    return np.stack((X, Y_corr), axis=-1)


def plot_baseline_corrected_spectrum(spectrum):
    plt.plot(spectrum[:, 0], spectrum[:, 1])
    plt.xlim([np.amin(spectrum[:, 0]), np.amax(spectrum[:, 0])])
    plt.ylim([np.amin(spectrum[:, 1]), np.amax(spectrum[:, 1])])
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity (a.u.)')
    plt.title('Original spectrum and baseline')
    plt.figure()


def plot_detected_peaks(spectrum, peak_indices, wl_start, wl_end):
    wl_start_idx = find_nearest(spectrum[:, 0], wl_start)
    wl_end_idx = find_nearest(spectrum[:, 0], wl_end)
    intensity_min = np.amin(spectrum[wl_start_idx:wl_end_idx, 1]) - np.amax(
        spectrum[wl_start_idx:wl_end_idx, 1]) * 0.02  # lower intensity limit for plots
    # upper intensity limit for plots
    intensity_max = np.amax(spectrum[wl_start_idx:wl_end_idx, 1])
    plt.plot(spectrum[:, 0], spectrum[:, 1])
    plt.plot(spectrum[peak_indices[:, 0], 0],
             spectrum[peak_indices[:, 0], 1], "4")
    plt.plot(spectrum[peak_indices[:, 1], 0],
             spectrum[peak_indices[:, 1], 1], "^")
    plt.plot(spectrum[peak_indices[:, 2], 0],
             spectrum[peak_indices[:, 2], 1], "3")
    plt.xlim([wl_start, wl_end])
    plt.ylim([intensity_min, intensity_max])
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity (a.u.)')
    plt.title('Peaks and peak borders')
    plt.figure()


def calculate_integrals(baseline_corrected_spectrum, height, wlen, output_filename=None):
    logging.info(f"""Calculating integrals using the baseline corrected spectrum and the following parameters:
    height:{height}
    wlen:{wlen}""")
    peak_integrals = integral(baseline_corrected_spectrum, height, wlen)
    if output_filename:
        np.savetxt(output_filename, peak_integrals, fmt='%.6e')
    return peak_integrals


def main(config):
    if config["enabled"]:
        filename = config["input_filename"]
        output_filename = config["output_filename"]
        ratio = float(config["baseline_correction"]["ratio"])
        lam = config["baseline_correction"]["lam"]
        niter = config["baseline_correction"]["niter"]
        height = config["peak_finder"]["height"]
        wlen = config["peak_finder"]["wlen"]
        wl_start = config["plot_options"]["wl_start"]
        wl_end = config["plot_options"]["wl_end"]

        baseline_corrected_spectrum = prepare_baseline_corrected_spectrum(
            filename, ratio, lam, niter)
        peak_indices = peakfinder(baseline_corrected_spectrum, height, wlen)
        calculate_integrals(baseline_corrected_spectrum,
                            height, wlen, output_filename=output_filename)
        plot_baseline_corrected_spectrum(baseline_corrected_spectrum)
        plot_detected_peaks(baseline_corrected_spectrum,
                            peak_indices, wl_start, wl_end)


if __name__ == "__main__":
    config = helper_functions.read_config_file("config.yaml")
    main(config["prepare_spectrum"])
