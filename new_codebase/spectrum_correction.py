import numpy as np
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm


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


def correct_spectrum(spectrum):
    X = spectrum[:, 0]
    Y = spectrum[:, 1]
    Y_corr = Y - baseline_arPLS(Y)
    return np.stack((X, Y_corr), axis=-1)
