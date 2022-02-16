# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 14:00:23 2022

@author: Attila Kohut
"""

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
from numpy import genfromtxt
# from scipy.signal import find_peaks, peak_prominences
# from scipy import sparse
# from scipy.sparse import linalg
# from numpy.linalg import norm
# from matplotlib import pyplot as plt
# import codecs

AuAgCu = genfromtxt('AuAgCu_NIST.txt', skip_header=1,  delimiter='\t') #atomic data from NIST

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def spec_data(NIST_data, integrals):
    spec_data = np.zeros((integrals[:,0].size,6))
    for i in range(0, integrals[:,0].size): 
        spec_data[i,0] = integrals[i,0]  # wavelength of selected line
        idx = find_nearest(NIST_data[:,2],integrals[i,0])
        spec_data[i,1] = NIST_data[idx,2] # NIST wavelength of the selected line
        spec_data[i,2] = NIST_data[idx,3] # Aki
        spec_data[i,3] = NIST_data[idx,8] # gi
        spec_data[i,4] = NIST_data[idx,6] # Ei
        spec_data[i,5] = integrals[i,1] # integral of the selected line
    return spec_data

###Input
##Filename containing the line integrals
filename = "AuAgCu_15-15-70_2eV_1E19_10000res_integrals"

###Gather data
integrals = genfromtxt(filename+".txt")
integrals_with_constants = spec_data(AuAgCu, integrals)
np.savetxt(filename+"_with_constants.txt", integrals_with_constants, fmt='%.6e')