# Physical constants for Rubidium 87 

import scipy.constants as ct
from numpy import pi
hbar=ct.hbar
c=ct.c
lambdaRb=780.241*1e-9 #D2 line wavelength of Rubidium
delta = 0
epsilon = 7/15

sigma0 = 3*lambdaRb**2/(2*pi)*epsilon 


if __name__ == "__main__":
    print(sigma0)