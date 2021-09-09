"""
File which stores natural constants in cgs units.
Created on 2. June 2021 by Andrea Gebek.
"""

import numpy as np

e = 4.803e-10
m_e = 9.109e-28
c = 2.998e10
G = 6.674*10**(-8)
k_B = 1.381*10**(-16)
amu = 1.661*10**(-24)
R_J = 6.99e9        #Jupiter radius
M_J = 1.898e30      #Jupiter mass
M_E = 5.974e27      #Earth mass
R_sun = 6.96e10     # Solar radius
M_sun = 1.988e33
R_Io = 1.822e8      # Io radius
m_K = 39.0983*amu
m_Na = 22.99*amu
euler_mascheroni = 0.57721 
AU = 1.496e13   # Conversion of one astronomical unit into cm

"""
Parameters for the absorption lines and species (potentially combine this)
Format: [Line intensity (cm/particle), Wavelength in vacuum (cm), HWHM of Lorentzian profile (Hz),
mass of the absorber (g), name of the absorber]
Na_D2, Na_D1: Draine 2011, Steck 2000
K_D2, K_D1: Draine 2011, Tiecke 2011
"""

absorptionlines_dict = {'Na_D2': [5.66e-13, 5891.58e-8, 3.0771e7, m_Na, 'sodium'],
'Na_D1': [2.82e-13, 5897.57e-8, 3.0677e7, m_Na, 'sodium'],
'K_D2': [6.021e-13, 7667.01e-8, 2.978e6, m_K, 'potassium'],
'K_D1': [3.002e-13, 7701.08e-8, 3.018e6, m_K, 'potassium']}

speciesMass_dict = {'sodium': m_Na,
'potassium': m_K}


"""
Planetary parameters
Format: [Stellar radius (cm), Stellar mass (g), Reference radius (cm), Planetary mass(g), Orbital distance (cm),
Stellar effective temperature (K), Stellar surface gravity (log10(cm/s^2)), Metallicity [Fe/H], Alpha-enhancement [alpha/Fe]]
WASP-49b: Wyttenbach et al. 2017 (Metallicity from Sousa+ 2018, Alpha-enhancement unknown)
HD189733b: Wyttenbach et al. 2015 (T_eff, log_g, and Metallicity from Chavero+ 2019, Alpha-enhancement unknown)
"""

planets_dict = {'WASP-49b': [1.038 * R_sun, 1.003 * M_sun, 1.198 * R_J, 0.399 * M_J, 0.03873 * AU, 5600, 4.5, -0.08, 0],
'HD189733b': [0.756 * R_sun, 0.823 * M_sun, 1.138 * R_J, 1.138 * M_J, 0.0312 * AU, 5201, 4.64, -0.02, 0]}


"""
Dictionary with possible scenarios
"""

scenario_list = ['barometric', 'hydrostatic', 'escaping', 'exomoon', 'torus']