"""
Main code to sort out which script to run.
Created on 15. July 2021 by Andrea Gebek.
"""

import json
import sys
import os


paramsFilename = sys.argv[1]

with open('../' + paramsFilename + '.txt') as file:
    param = json.load(file)

mode = param['mode']
sphericalSymmetry = param['sphericalSymmetry']
RM_effect = param['RM_effect']

if mode == 'spectrum' and sphericalSymmetry:
    os.system('python pythonScripts/spheSymmetricSpectrum.py ' + paramsFilename)

elif mode == 'spectrum':
    os.system('python pythonScripts/noSymmetrySpectrum.py ' + paramsFilename)

elif mode == 'lightcurve' and not RM_effect:
    os.system('python pythonScripts/lightcurve.py ' + paramsFilename)

elif mode == 'lightcurve':
    os.system('python pythonScripts/lightcurveStarSpectrum.py ' + paramsFilename)