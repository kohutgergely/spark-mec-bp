import numpy as np
# from numpy import genfromtxt
from scipy.signal import find_peaks, peak_prominences
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm
from matplotlib import pyplot as plt
# import codecs

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def baseline_arPLS(y, ratio, lam, niter, full_output=False):
    L = len(y)

    diag = np.ones(L - 2)
    D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)

    H = lam * D.dot(D.T)  # The transposes are flipped w.r.t the Algorithm on pg. 252

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

def corr_spectrum(spectrum, ratio, lam, niter):
    X = spectrum[:,0]
    Y = spectrum[:,1]
    Y_corr = Y - baseline_arPLS(Y, ratio, lam, niter) 
    return np.stack((X,Y_corr), axis=-1)

def peakfinder(spectrum, height, wlen):
    Y = spectrum[:,1]    
    peaks, _ = find_peaks(Y, height, threshold=0, width=1)
    left = peak_prominences(Y, peaks, wlen)[1] #lower integration limit of each line
    right = peak_prominences(Y, peaks, wlen)[2] #upper integration limit of each line
    peak_indices = np.stack((left,peaks, right), axis=-1)
    return peak_indices

def integral(spectrum, height, wlen):
    X = spectrum[:,0]
    Y = spectrum[:,1]
    peak_indices = peakfinder(spectrum, height, wlen)
    peak_position = peak_indices[:,1]
    left_base = peak_indices[:,0]
    right_base = peak_indices[:,2]
    integrals = np.zeros((peak_indices[:,1].size,2))
    for i in range(0, left_base.size):   
        peak_X = X[left_base[i]:right_base[i]:1]
        peak_Y = Y[left_base[i]:right_base[i]:1]
        peak_int = np.trapz(peak_Y,peak_X)
        integrals[i,0] = X[peak_position[i]]
        integrals[i,1] = peak_int
    return integrals


###Input
##Spectrum filename
filename = "AuAgCu_15-15-70_2eV_1E19_10000res"

##Baseline correction
ratio = 1E-5
lam = 1000
niter = 10

##Peak finder
height = 100
wlen = 40

##Plotting a narrow wavelength range
wl_start = 509          #lower wavelength limit for plots
wl_end = 523 #upper wavelength limit for plots

###Prepare spectrum
spectrum = np.loadtxt(filename+".txt", dtype=None, delimiter='\t')
spectrum = corr_spectrum(spectrum, ratio, lam, niter)
peak_indices = peakfinder(spectrum, height, wlen)
peak_integrals = integral(spectrum, height, wlen)
np.savetxt(filename+"_integrals.txt", peak_integrals, fmt='%.6e')


###Plotting
##Overview plot for the baseline
plt.plot(spectrum[:,0], spectrum[:,1])
plt.plot(spectrum[:,0], baseline_arPLS(spectrum[:,1], ratio, lam, niter))
plt.xlim([np.amin(spectrum[:,0]), np.amax(spectrum[:,0])])
plt.ylim([np.amin(spectrum[:,1]), np.amax(spectrum[:,1])])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Original spectrum and baseline')
plt.figure()


##Close up for peak detection
wl_start_idx = find_nearest(spectrum[:,0], wl_start)
wl_end_idx = find_nearest(spectrum[:,0], wl_end)
intensity_min = np.amin(spectrum[wl_start_idx:wl_end_idx,1]) - np.amax(spectrum[wl_start_idx:wl_end_idx,1])*0.02  #lower intensity limit for plots
intensity_max = np.amax(spectrum[wl_start_idx:wl_end_idx,1]) #upper intensity limit for plots
plt.plot(spectrum[:,0], spectrum[:,1])
plt.plot(spectrum[peak_indices[:,0],0], spectrum[peak_indices[:,0],1], "4")
plt.plot(spectrum[peak_indices[:,1],0], spectrum[peak_indices[:,1],1], "^")
plt.plot(spectrum[peak_indices[:,2],0], spectrum[peak_indices[:,2],1], "3")
plt.xlim([wl_start, wl_end])
plt.ylim([intensity_min, intensity_max])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity (a.u.)')
plt.title('Peaks and peak borders')
plt.figure()