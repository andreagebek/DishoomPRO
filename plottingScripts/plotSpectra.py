"""
Author: Andrea Gebek
Created on 3.9.2021
Plot a transmission spectrum
from a lightcurve txt file.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
import sys

matplotlib.rcParams['axes.linewidth'] = 2.5
matplotlib.rcParams['xtick.major.size'] = 10
matplotlib.rcParams['xtick.minor.size'] = 6
matplotlib.rcParams['xtick.major.width'] = 2.5
matplotlib.rcParams['xtick.minor.width'] = 1.5
matplotlib.rcParams['ytick.major.size'] = 10
matplotlib.rcParams['ytick.minor.size'] = 6
matplotlib.rcParams['ytick.major.width'] = 2.5
matplotlib.rcParams['ytick.minor.width'] = 1.5
matplotlib.rcParams['image.origin'] = 'lower'
matplotlib.rcParams.update({'font.size': 26, 'font.weight': 'bold'})

"""
Read in settings file and stored lightcurve.
Calculate the transmission spectrum by averaging
the depth in the lightcurve during full occultation
of the planet's R_0.
"""

plotMeanSpectrum = False # Plot the spectrum averaged over all orbital phases between planetary ingress and egress
plotSpectra = True  # Plot the spectra at all orbital phases
plotBenchmarkSpectra = True # Plot barometric benchmark spectra at all orbital phases (only if the barometric benchmark option is True in the setup file)

paramsFilename = sys.argv[1]

with open('../../setupFiles/' + paramsFilename + '.txt') as file:
    param = json.load(file)

architectureDict = param['Architecture']
gridsDict = param['Grids']

orbphase = np.linspace(-gridsDict['orbphase_border'], gridsDict['orbphase_border'], int(gridsDict['orbphase_steps']))
wavelength = np.arange(gridsDict['lower_w'], gridsDict['upper_w'], gridsDict['resolution']) * 1e8 # In Angstrom

R_star = architectureDict['R_star']
R_0 = architectureDict['R_0']
a_p = architectureDict['a_p']

benchmark = param['Output']['benchmark']

LightcurveFile = np.loadtxt('../../output/' + paramsFilename + '_lightcurve.txt')

R = LightcurveFile[:, 2].reshape(len(wavelength), len(orbphase))

R_plot = []
for idx in range(len(orbphase)):

    R_plot.append(R[:, idx] + (1 - np.max(R[:, idx]))) # Normalize the transit depth such that the smallest flux decrease is shifted to 1

if benchmark:

    R_benchmark = np.loadtxt('../../output/' + paramsFilename + '_barometricBenchmark.txt')[:, 2].reshape(len(wavelength), len(orbphase))

    R_benchmark_plot = []
    for idx in range(len(orbphase)):

        R_benchmark_plot.append(R_benchmark[:, idx] + (1 - np.max(R_benchmark[:, idx]))) # Normalize the transit depth such that the smallest flux decrease is shifted to 1

"""
Plot the spectrum and store the figure
"""


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

cmap = matplotlib.cm.get_cmap('Accent')

for idx, r in enumerate(R_plot):

    if plotSpectra:
        ax.plot(wavelength, r, color = cmap(float(idx) / float(len(orbphase))), linewidth = 1, label = r'$\phi=$' + str(np.round(orbphase[idx], 3)))

    if benchmark and plotBenchmarkSpectra:

        ax.plot(wavelength, R_benchmark_plot[idx], color = cmap(float(idx) / float(len(orbphase))), linewidth = 1, linestyle = '--')

if len(orbphase) > 1 and plotMeanSpectrum:

    orbphaseFullIngress = np.arcsin((R_star - R_0) / a_p) / (2. * np.pi) # Orbital phase at which the planet's R_0 is fully within the stellar disk

    SEL = np.abs(orbphase) <= orbphaseFullIngress
    R_avg = np.mean(R[:, SEL], axis = 1)
    R_avg_norm = R_avg + (1 - np.max(R_avg))

    ax.plot(wavelength, R_avg_norm, color = 'black', linewidth = 2, label = 'Mean')




lg = ax.legend(loc = 'center right')
lg.get_frame().set_alpha(0)
lg.get_frame().set_linewidth(0)

ax.set_xlabel(r'$\lambda\,[\AA]$')
ax.set_ylabel(r'$\Re$')

ax.minorticks_on()
ax.tick_params(which = 'both', direction = 'in', right = True, top = True)

ax.set_xlim(np.min(wavelength), np.max(wavelength))
ax.set_ylim(np.min(R_plot) - 0.05 * (1 - np.min(R_plot)), 1 + 0.05 * (1 - np.min(R_plot)))

plt.tight_layout()

plt.savefig('../../figures/' + paramsFilename + '_spectrumPlot.pdf', dpi = 150)