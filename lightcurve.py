"""
Calculate the light curve of a transiting exoplanet.
Created on 15. July 2021 by Andrea Gebek.
"""

import numpy as np
import json
import sys
from datetime import datetime
from constants import *
from n_profiles import *
from sigma_abs import *


startTime = datetime.now()


"""
Helper function for the intersection area of two circles
"""

def A_intersect(r1, r2, y, x):

    A = []

    for idx, d in enumerate(y):

        if np.abs(d) > (r1 + r2) or x[idx] < 0:
            A.append(0)
        
        elif np.abs(d) < np.abs(r1 - r2):
            A.append(np.pi * np.min((r1, r2))**2)
        
        else:
            term1 = (r1**2 - r2**2 + d**2) / (2. * np.abs(d))
            term2 = (r2**2 - r1**2 + d**2) / (2. * np.abs(d))
            term3 = r1**2 * np.arccos(term1 / r1) - term1 * np.sqrt(r1**2 - term1**2)
            term4 = r2**2 * np.arccos(term2 / r2) - term2 * np.sqrt(r2**2 - term2**2)

            A.append(term3 + term4)
  
    return np.array(A)




"""
Calculation of the theoretical transit depth in two steps,
first calculating the (wavelength-dependent) optical depth along the 
chord at various impact parameters, then integrate over all possible 
impact parameters to obtain the (wavelength-dependent) transit depth
"""



def optical_depth(phi, rho, wavelength, x_p, y_p):

    x = np.linspace(-x_border, x_border, int(x_steps) + 1, dtype = np.dtype('f4'))[:-1] + x_border / float(x_steps)
    delta_x = 2 * x_border / float(x_steps)
    xx, phiphi, rhorho, yy_pp = np.meshgrid(x, phi, rho, y_p)

    r_fromP = np.sqrt(xx**2 + (rhorho * np.sin(phiphi) - yy_pp)**2 + (rhorho * np.cos(phiphi))**2)
    
    tau = 0
    for key_scenario in species_dict.keys():

        number_density = number_density_dict[key_scenario]        

        if key_scenario == 'barometric' or key_scenario == 'hydrostatic' or key_scenario == 'escaping':
        
            n = number_density(r_fromP, scenario_dict[key_scenario])

        elif key_scenario == 'exomoon':

            current_orbphase_moon = orbphase_moon + orbphase * np.sqrt((a_p**3 * M_p) / (a_moon**3 * M_s)) # Assuming Keplerian orbits of massless points

            x_moonFrame = xx - a_moon * np.cos(current_orbphase_moon)
            y_moonFrame = np.sin(phiphi) * rhorho - yy_pp - a_moon * np.sin(current_orbphase_moon)
            z_moonFrame = np.cos(phiphi) * rhorho

            r_fromMoon = np.sqrt(x_moonFrame**2 + y_moonFrame**2 + z_moonFrame**2)

            n = number_density(r_fromMoon, scenario_dict[key_scenario])

        elif key_scenario == 'torus':

            aa = np.sqrt(xx**2 + (np.sin(phiphi) * rhorho - yy_pp)**2)
            zz = np.cos(phiphi) * rhorho

            n = number_density(aa, zz, scenario_dict[key_scenario])

        yy = rhorho * np.sin(phiphi)
        zz = np.cos(phiphi) * rhorho
        blockingPlanet = (np.sqrt((yy - yy_pp)**2 + zz**2) < R_0)
        n = np.where(blockingPlanet, 0, n)

        behindStar = (xx + x_p < 0)
        n = np.where(behindStar, 0, n)

        if ExomoonSource: # Correct for chords which are blocked by the exomoon

            current_orbphase_moon = orbphase_moon + orbphase * np.sqrt((a_p**3 * M_p) / (a_moon**3 * M_s)) # Assuming Keplerian orbits of massless points
            y_moon = yy_pp + a_moon * np.sin(current_orbphase_moon)

            blockingMoon = ((yy - y_moon)**2 + zz**2 < R_moon**2) 

            n = np.where(blockingMoon, 0, n)

        N = delta_x * np.sum(n, axis = 1)

        sigma = 0
        for key_species in species_dict[key_scenario].keys():

            chi = species_dict[key_scenario][key_species]['chi'] # Mixing ratio OR number of absorbing atoms

            T_abs = species_dict[key_scenario][key_species]['T_abs']

            sigma += absorption_cross_section(wavelength, chi, T_abs, key_species, lines_dict)

        if 'RayleighScatt' in scenario_dict[key_scenario].keys():
            if scenario_dict[key_scenario]['RayleighScatt']:
                sigma += rayleigh_scattering(wavelength)

        tau += np.tensordot(sigma, N, axes = 0)

    return tau


def transit_depth(wavelength, orbphase):
    """Calculate the wavelength-dependent transit depth
    """

    phi = np.linspace(0, 2 * np.pi, int(phi_steps) + 1, dtype = np.dtype('f4'))[:-1] + np.pi / float(phi_steps)
    rho = np.linspace(0, R_s, int(z_steps) + 1, dtype = np.dtype('f4'))[:-1] + 0.5 * R_s / float(z_steps)

    x_p = a_p * np.cos(orbphase)
    y_p = np.array(a_p * np.sin(orbphase), dtype = np.dtype('f4'))
    
    single_chord = np.exp(-optical_depth(phi, rho, wavelength, x_p, y_p))

    delta_rho = R_s / float(z_steps)
    delta_phi = 2 * np.pi / float(phi_steps)

    integral_phi = delta_phi * np.sum(single_chord, axis = 1)
    
    A_occ_p = A_intersect(R_0, R_s, y_p, x_p) # Area of the planet blocking the stellar disk

    sum_over_chords = delta_rho * np.tensordot(rho, integral_phi, axes = [0, 1]) - A_occ_p
    
    if ExomoonSource:

        current_orbphase_moon = orbphase_moon + orbphase * np.sqrt((a_p**3 * M_p) / (a_moon**3 * M_s)) # Assuming Keplerian orbits of massless points

        y_p_moon = a_moon * np.sin(current_orbphase_moon) # y-coordinate of the exomoon relative to the exoplanet

        y_moon = y_p + y_p_moon # y-coordinate of the exomoon in the main coordinate frame

        A_moonOnP = np.where(A_occ_p > 0, A_intersect(R_moon, R_0, y_p_moon, x_p), 0) # If the planet is not transiting the area of the moon on the planet does not matter
        A_occ_moon = np.clip(A_intersect(R_moon, R_s, y_moon, x_p) - A_moonOnP, a_min = 0, a_max = None) 
        # Area of the exomoon blocking the stellar disk (but not the exoplanet). The above equation is wrong during planetary ingress and egress,
        # as the actual A_occ_moon is the area of the moon on the stellar disk minus the intersection area of moon, planet and star.
        # But this becomes extremely cumbersome...

        sum_over_chords -= A_occ_moon

    return sum_over_chords / (np.pi * R_s**2)


""".
Read in values from the setup file
"""

paramsFilename = sys.argv[1]

with open('../' + paramsFilename + '.txt') as file:
    param = json.load(file)

ExomoonSource = param['ExomoonSource']


architecture_dict = param['Architecture']

R_s = architecture_dict['R_star']
M_s = architecture_dict['M_star']
R_0 = architecture_dict['R_0']
M_p = architecture_dict['M_p']
a_p = architecture_dict['a_p']

if ExomoonSource:
    R_moon = architecture_dict['R_moon']
    a_moon = architecture_dict['a_moon']
    orbphase_moon = architecture_dict['orbphase_moon']


scenario_dict = param['Scenarios']
lines_dict = param['Lines']
species_dict = param['Species']

grids_dict = param['Grids']

wavelength = np.array(grids_dict['wavelength'])
orbphase_border = grids_dict['orbphase_border']
orbphase = np.linspace(-orbphase_border, orbphase_border, 1 + int(grids_dict['orbphase_steps']))[:-1] + orbphase_border / float(grids_dict['orbphase_steps'])
x_border = grids_dict['x_border']
x_steps = grids_dict['x_steps']
z_steps = grids_dict['z_steps']
phi_steps = grids_dict['phi_steps']

output_dict = param['Output']

number_density_dict = {'barometric': barometric, 'hydrostatic': hydrostatic, 'escaping': escaping, 'exomoon': exomoon, 'torus': torus}


"""
Execute the code and save the output as a .txt file
"""

header = 'Orbital phase'

for w in wavelength:
    header += ', Light curve at ' + str(w * 1e8) + ' A'

lightcurve = transit_depth(wavelength, orbphase)
np.savetxt('../' + paramsFilename + '_lightcurve.txt', np.c_[orbphase / (2 * np.pi), lightcurve.T], header = header)

elapsed_time = datetime.now() - startTime

print("PROMETHEUS finished, yay! Elapsed time is:", elapsed_time)

print("The maximal flux decrease due to atmospheric/exospheric absorption in percent is:", np.abs(np.round(100 * (1 - np.min(lightcurve)), 5)))

print("The minimal flux decrease due to atmospheric/exospheric absorption in percent is:", np.abs(np.round(100 * (1 - np.max(lightcurve)), 5)))