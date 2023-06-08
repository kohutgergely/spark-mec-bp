import numpy as np
from numpy import genfromtxt
from scipy.signal import find_peaks, peak_prominences
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm
from matplotlib import pyplot as plt
import codecs
from scipy.optimize import curve_fit
from lmfit.models import VoigtModel, PseudoVoigtModel
from nist_sdk.atomic_lines import AtomicLinesFetcher
from nist_sdk.atomic_levels import AtomicLevelsFetcher
from parsers.atomic_lines import AtomicLinesParser
from parsers.atomic_levels import AtomicLevelsParser

### Constants###
m = 9.10938291E-28  # g
k = 1.3807E-16  # cm2 g s-2 K-1
h = 6.6261E-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458E10  # cm/s
p = 1E6  # g/s^2 m

X = (2*np.pi*m*k)/np.power(h, 2)  # constant in Saha-Boltzmann equation

conv = 11604.525

Ionization_Au = np.array([74410.39, 165347.465, 241971.9])
Ionization_Ag = np.array([61107.58, 173332.54, 280929.38])
Ionization_Ar = np.array([127112.678, 222853.296, 328597.84])


def get_atomic_lines(spectrum: str, lower_wavelength: int, upper_wavelength: int):
    atomic_lines_data = AtomicLinesFetcher().fetch(
        spectrum, lower_wavelength, upper_wavelength)
    parsed_data = AtomicLinesParser().parse_atomic_lines(atomic_lines_data)
    filtered_data = parsed_data[[
        "obs_wl_air(nm)", "Aki(s^-1)", "Acc", "Ei(cm-1)", "Ek(cm-1)", "g_i", "g_k", "Type"]]
    return filtered_data[filtered_data["Aki(s^-1)"].notna()].to_numpy()


def get_partition_function(spectrum: str, temperature: int):
    atomic_levels_data = AtomicLevelsFetcher().fetch(spectrum, temperature)
    return AtomicLevelsParser().parse_partition_function(atomic_levels_data)


AuI = get_atomic_lines("Au I", lower_wavelength=300, upper_wavelength=800)
AgI = get_atomic_lines("Ag I", lower_wavelength=300, upper_wavelength=800)

### Polynomials for partition function###
Cu = np.array([[1.08605, 8.66998, -18.3398, 15.77519, -2.11931],
               [1.28222, -2.77724, 5.89866, -3.161, 1.00284],
               [5.62783, 8.5162, -7.8181, 3.38896, -0.5737]])

Au = np.array([[1.60027, 3.10448, -3.53278, 4.07054, -0.91752],
               [1.13259, -1.71445, 4.56106, -1.21503, 0.19769],
               [6, 0, 0, 0, 0]])

Ag = np.array([[1.56653, 4.5309, -11.60646, 10.07343, -2.1638],
               [0.996, 0.07564, -0.34489, 0.38715, 0.01687],
               [5.42309, 5.33618, -3.85329, 1.47616, -0.16201]])

Ar = np.array([[2.20045, -5.74972, 9.98936, -7.80378, 2.63179],
               [4.05678, 3.47587, -2.36249, 0.62967, -0.06836],
               [5.40247, 7.20943, -4.62452, 1.73503, -0.31713]])


def rD(ne, T):
    # Debye radius in cm (formula is from Fridman Plasma Physics and Enginiering, p202)
    rD = 742*np.sqrt((T*0.695028)/ne)
    return rD


def ZI(T, polynom):
    T = T/conv
    Z = polynom[0, 0] + polynom[0, 1]*T + polynom[0, 2] * \
        np.power(T, 2) + polynom[0, 3]*np.power(T,
                                                3) + polynom[0, 4]*np.power(T, 4)
    return Z


def ZII(T, polynom):
    T = T/conv
    Z = polynom[1, 0] + polynom[1, 1]*T + polynom[1, 2] * \
        np.power(T, 2) + polynom[1, 3]*np.power(T,
                                                3) + polynom[1, 4]*np.power(T, 4)
    return Z


def SB(ne, T, Ionization):
    SB = 2*(1/ne)*np.power(X, 1.5)*np.power(T, 1.5) * \
        np.exp(-(Ionization/(T*0.695028)))  # number concentration of argon ions
    return SB


def SB2(T, Ionization):
    # number concentration of argon ions
    SB2 = 2*np.power(X, 1.5)*np.power(T, 1.5) * \
        np.exp(-(Ionization/(T*0.695028)))
    return SB2


def B(T, Ionization, polynom):
    B = 4*(ZII(T, polynom)/ZI(T, polynom))*SB2(T, Ionization)
    return B


def C(T, Ionization, polynom):
    C = 2*(ZII(T, polynom)/ZI(T, polynom))*SB2(T, Ionization)*(p/(T*k))
    return C


def D(T, Ionization, polynom):
    D = np.power(B(T, Ionization, polynom), 2) + 4*1*C(T, Ionization, polynom)
    return D


def ne_estimate(T, Ionization, polynom):
    ne_estimate = (-1*B(T, Ionization, polynom) +
                   np.sqrt(D(T, Ionization, polynom)))/(2*1)
    return ne_estimate


def peakfinder(Y, height):
    peak_indices, _ = find_peaks(Y, height, threshold=0, width=2)
    return peak_indices


def baseline_arPLS(y, ratio=1E-5, lam=1000000, niter=50, full_output=False):
    L = len(y)

    diag = np.ones(L - 2)
    D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)

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

        w_new = 1 / (1 + np.exp(2 * (d - (2*s - m))/s))

        crit = norm(w_new - w) / norm(w)

        w = w_new
        W.setdiag(w)  # Do not create a new matrix, just update diagonal values

        count += 1

        if count > niter:
            print('Maximum number of iterations exceeded')
            break

    if full_output:
        info = {'num_iter': count, 'stop_criterion': crit}
        return z, d, info
    else:
        return z


def integral(spectrum):
    X = spectrum[:, 0]
    Y = spectrum[:, 1]
    peaks = peakfinder(Y, height=set_height)
    prominences = peak_prominences(Y, peaks, wlen=set_wlen)
    left_base = prominences[1]
    right_base = prominences[2]
    integrals = np.zeros((X.size, 2))
    for i in range(0, left_base.size):
        peak_X = X[left_base[i]:right_base[i]:1]
        peak_Y = Y[left_base[i]:right_base[i]:1]
        peak_int = np.trapz(peak_Y, peak_X)
        integrals[i, 0] = X[peaks[i]]
        integrals[i, 1] = peak_int  # *(h*c/(X[peaks[i]]*1E-7))
    return integrals


def Voigt_integral(spectrum, selected_peak):
    wavelength = spectrum[:, 0]
    Y = spectrum[:, 1]
    all_peaks = np.stack((peakfinder(Y, height=set_height),
                         wavelength[peakfinder(Y, height=set_height)]), axis=-1)
    selected_peak_idx = find_nearest(all_peaks[:, 1], selected_peak)
    selected_peak_idx_array = np.array([int(all_peaks[selected_peak_idx, 0])])
    prominences = peak_prominences(Y, selected_peak_idx_array, wlen=set_wlen)
    start_index = int(prominences[1])
    end_index = 2*int(all_peaks[selected_peak_idx, 0])-int(prominences[1])
    # start_wavelength = wavelength[start_index]
    # end_wavelength = wavelength[end_index]
    peak_wavelength = wavelength[start_index:end_index+1]
    peak_spectrum = Y[start_index:end_index+1]
    voigt_model = PseudoVoigtModel()
    params = voigt_model.guess(peak_spectrum, x=peak_wavelength)
    voigt_fit = voigt_model.fit(peak_spectrum, params, x=peak_wavelength)
    plt.plot(peak_wavelength, peak_spectrum, 'o', label='Original spectrum')
    plt.plot(peak_wavelength, voigt_fit.best_fit, label='Voigt fit')
    plt.legend()
    plt.show()
    area = np.trapz(voigt_fit.best_fit, peak_wavelength)
    # print(f"The area under the fitted Voigt function is: {area}")
    return area


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def spec_data(species, peak_table, spectrum):
    spec_data = np.zeros((species.size, 7))
    integrals = integral(spectrum)
    for i in range(0, species.size):
        spec_data[i, 0] = species[i]  # wavelength of selected line
        idx = find_nearest(peak_table[:, 0], species[i])
        # NIST wavelength of the selected line
        spec_data[i, 1] = peak_table[idx, 0]
        spec_data[i, 2] = peak_table[idx, 1]  # Aki
        spec_data[i, 3] = peak_table[idx, 6]  # gi
        spec_data[i, 4] = peak_table[idx, 4]  # Ei
        idx2 = find_nearest(integrals[:, 0], species[i])
        Voigt_area = Voigt_integral(spectrum, species[i])
        # spec_data[i,5] = integrals[idx2,1] # integral of the line
        spec_data[i, 5] = Voigt_area  # integral of the line
        spec_data[i, 6] = integrals[idx2, 0]
    return spec_data


def corr_spectrum(spectrum):
    X = spectrum[:, 0]
    Y = spectrum[:, 1]
    Y_corr = Y - baseline_arPLS(Y)
    return np.stack((X, Y_corr), axis=-1)


def rsquare(x, y, f):
    y_mean = np.mean(y)
    SS_tot = np.sum(np.power(y-y_mean, 2))
    SS_res = np.sum(np.power(y-f, 2))
    R2 = 1 - SS_res/SS_tot
    return R2


def T_fit(plot):
    E = plot[:, 0]
    ln = plot[:, 1]
    lin_params = np.polyfit(E, ln, 1)  # Fitting linear to the data
    linear = lin_params[0]*E + lin_params[1]  # The fitted linear
    R2 = rsquare(E, ln, linear)
    T = np.abs(-1/(0.695035*lin_params[0]))
    n = np.exp(lin_params[1])
    return np.array([T, n, R2])


def AuAg_ratio(AuI_species, AgI_species, spectrum):
    ln_ratio = np.zeros((AuI_species.size, AgI_species.size))
    E_value = np.zeros((AuI_species.size, AgI_species.size))
    AuIdata = spec_data(AuI_species, AuI, spectrum)
    AuI_ln = np.divide(np.multiply(
        AuIdata[:, 5], AuIdata[:, 1]*1E-7), np.multiply(AuIdata[:, 3], AuIdata[:, 2]))
    AgIdata = spec_data(AgI_species, AgI, spectrum)
    AgI_ln = (np.divide(np.multiply(
        AgIdata[:, 5], AgIdata[:, 1]*1E-7), np.multiply(AgIdata[:, 3], AgIdata[:, 2])))

    for i in range(0, AuI_species.size):
        ln_ratio[i, :] = np.log(np.divide(AuI_ln[i], AgI_ln))
        E_value[i, :] = np.subtract(AgIdata[:, 4], AuIdata[i, 4])

    ln_ratios = np.reshape(ln_ratio, AuI_species.size*AgI_species.size)
    E_values = np.reshape(E_value, AuI_species.size*AgI_species.size)

    return np.stack((E_values, ln_ratios), axis=-1)


def line_pair(peak_table, species, spectrum, T):
    line_data = spec_data(peak_table, species, spectrum)
    linepairs = np.zeros((peak_table.size, peak_table.size))
    linepairs[:, 0] = peak_table
    linepairs[0, :] = peak_table
    for i in range(0, peak_table.size):
        for j in range(0, peak_table.size):
            intratio = line_data[i, 5]/line_data[j, 5]
            dataratio = np.divide(((line_data[i, 3]*line_data[i, 2])/line_data[i, 1])*np.exp(-line_data[i, 4]/(
                0.695035*T)), ((line_data[j, 3]*line_data[j, 2])/line_data[j, 1])*np.exp(-line_data[j, 4]/(0.695035*T)))
            linepairs[i, j] = np.divide(dataratio-intratio, dataratio)

    return linepairs

## Saha-Boltzmann line-pair plots for Ag/Au###


def AuAg_n_concentration(Au_peak_table, Ag_peak_table, spectrum):
    AuAg_graph = AuAg_ratio(Au_peak_table, Ag_peak_table, spectrum)
    AuAg_fit = np.polyfit(AuAg_graph[:, 0], AuAg_graph[:, 1], 1)
    TAuAg = (1/(0.695035*AuAg_fit[0]))
    ag1 = get_partition_function("Ag I", TAuAg)
    ag2 = get_partition_function("Ag II", TAuAg)
    print("partition Ag1", ag1)
    print("partition Ag2", ag2)
    print("ag2/ag1", ag2/ag1)
    print("Z2/Z1", ZII(TAuAg, Ag)/ZI(TAuAg, Ag))
    print(TAuAg)
    nAuAg = np.exp(AuAg_fit[1])*(ZI(TAuAg, Au)/ZI(TAuAg, Ag))
    # n_ion_AuAg = nAuAg*(ZII(TAuAg, Au)/ZII(TAuAg, Ag))*(ZI(TAuAg, Ag)/ZI(TAuAg, Au))*np.exp((Ionization_Ag[0]-Ionization_Au[0])/(0.695035*TAuAg))

    ne = ne_estimate(TAuAg, Ionization_Ar[0], Ar)
    nAgion_atom = SB(
        ne, TAuAg, Ionization_Ag[0])*(ZII(TAuAg, Ag)/ZI(TAuAg, Ag))
    nAuion_atom = SB(
        ne, TAuAg, Ionization_Au[0])*(ZII(TAuAg, Au)/ZI(TAuAg, Au))
    # nAgatom_ion = 1/nAgion_atom

    total_n_AuAg = ((nAuion_atom+1)/(nAgion_atom+1))*nAuAg

    plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 1], "x")
    plt.plot(AuAg_graph[:, 0], AuAg_graph[:, 0]*AuAg_fit[0]+AuAg_fit[1])
    plt.xlabel('Difference of upper energy levels (cm-1)')
    plt.ylabel('log of line intensity ratios (a.u.)')
    plt.title('Saha-Boltzmann line-pair plot for Au I and Ag I lines')
    plt.figure()

    print(
        f"The temperature is: {TAuAg}, and the total Au-to-Ag number concentration ratio is: {total_n_AuAg}")

    return (TAuAg, total_n_AuAg)


### Spectrum to be processed###
with codecs.open('AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc', encoding='utf-8-sig') as f:
    spectrum = np.loadtxt(f)
    spectrum = np.stack((spectrum[:, 0], spectrum[:, 10]), axis=-1)

corr_spectrum = corr_spectrum(spectrum)

### Peak tables###
AuI_species = np.array([312.278, 406.507, 479.26])
AgI_species = np.array([338.29, 520.9078, 546.54])

### Baseline and peak finding###
wl_start = 400  # lower limit for plots
wl_end = 410  # upper limit for plots
set_wlen = 40  # the wlen parameter for the prominence function
set_height = 100


plt.plot(spectrum[:, 0], spectrum[:, 1])
plt.plot(spectrum[:, 0], baseline_arPLS(spectrum[:, 1]))
plt.xlim([310, 800])
# plt.ylim([4.5, 5])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Original spectrum and baseline')
plt.figure()

# major peaks in the spectrum
peaks = peakfinder(corr_spectrum[:, 1], set_height)
integrals = integral(corr_spectrum)  # integrals of the peaks
left = peak_prominences(corr_spectrum[:, 1], peaks, wlen=set_wlen)[
    1]  # lower integration limit of each line
right = peak_prominences(corr_spectrum[:, 1], peaks, wlen=set_wlen)[
    2]  # upper integration limit of each line

plt.plot(corr_spectrum[:, 0], corr_spectrum[:, 1])
plt.plot(corr_spectrum[peaks, 0], corr_spectrum[peaks, 1], "x")
plt.plot(corr_spectrum[left, 0], corr_spectrum[left, 1], "o")
plt.plot(corr_spectrum[right, 0], corr_spectrum[right, 1], "o")
plt.xlim([wl_start, wl_end])
plt.ylim([-100, 10000])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Baseline corrected spectrum with the major peaks')
plt.figure()


TAuAg = AuAg_n_concentration(AuI_species, AgI_species, corr_spectrum)[0]
total_n_AuAg = AuAg_n_concentration(AuI_species, AgI_species, corr_spectrum)[1]

AuI_linepair_check = line_pair(AuI_species, AuI, corr_spectrum, TAuAg)
AgI_linepair_check = line_pair(AgI_species, AgI, corr_spectrum, TAuAg)

print(f"AuI linepair deviations: {AuI_linepair_check}")
print(f"AgI linepair deviations: {AgI_linepair_check}")
