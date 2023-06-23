# Physical constants for dysprosium

import scipy.constants as ct
from numpy import pi
hbar=ct.hbar
c=ct.c
lambdaDy=421*1e-9 
delta = 0
epsilon = 1

sigma0 = 3*lambdaDy**2/(2*pi)*epsilon 


if __name__ == "__main__":
    print(sigma0)