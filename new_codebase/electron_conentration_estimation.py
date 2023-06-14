import numpy as np

m = 9.10938291E-28  # g
k = 1.3807E-16  # cm2 g s-2 K-1
h = 6.6261E-27  # cm2 g s-1
e = -1  # elementary charge
c = 2.99792458E10  # cm/s
p = 1E6  # g/s^2 m

X = (2*np.pi*m*k)/np.power(h, 2)  # constant in Saha-Boltzmann equation


def SB(ne, T, ionization):
    return 2*(1/ne)*np.power(X, 1.5)*np.power(T, 1.5) * \
        np.exp(-(ionization/(T*0.695028)))  # number concentration of argon ions


def SB2(T, ionization):
    # number concentration of argon ions
    return 2*np.power(X, 1.5)*np.power(T, 1.5) * \
        np.exp(-(ionization/(T*0.695028)))


def B(T, ionization, ion_neutral_atom_partition_function_ratio):
    B = 4*ion_neutral_atom_partition_function_ratio * \
        SB2(T, ionization)
    return B


def C(T, ionization, ion_neutral_atom_partition_function_ratio):
    C = 2*ion_neutral_atom_partition_function_ratio * \
        SB2(T, ionization)*(p/(T*k))
    return C


def D(T, ionization, ion_neutral_atom_partition_function_ratio):
    D = np.power(B(T, ionization, ion_neutral_atom_partition_function_ratio),
                 2) + 4*1*C(T, ionization, ion_neutral_atom_partition_function_ratio)
    return D


def estimate_electron_concentration(T, ionization, partition_function_neutral_atom, partition_function_ion):
    ion_neutral_atom_partition_function_ratio = partition_function_ion / \
        partition_function_neutral_atom

    ne_estimate = (-1*B(T, ionization, ion_neutral_atom_partition_function_ratio) +
                   np.sqrt(D(T, ionization, ion_neutral_atom_partition_function_ratio)))/(2*1)
    return ne_estimate
