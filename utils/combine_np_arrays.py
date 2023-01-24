#!/bin/bash
# -*- coding: utf-8 -*-

'''
Combine the numpy arrays into a single array for signal or background
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes:  
'''

import numpy as np
import sys, os, subprocess, time, argparse
from time import perf_counter as cput()

print('\n===========================')
print('==  HH4B MASS REGRESSION ==')
print('==  Combine Arrays ..... ==')
print('===========================\n')

## ARGPARSING ##
parser = argparse.ArgumentParser(description='Main script to create numpy\
    .npy files from root files.')
parser.add_argument('file_directory', #positional argument
    action='store',
    type=str, default=None,
    help='Directory where the root files live.')
parser.add_argument('--outdir', dest='outdir',
    action='store', type=str, default=None,
    help='Output directory for the *.npy files.')
parser.add_argument('-f', dest='force', action='store_true',
    help='Will force the creation of input and output files.',
    default=False)
parser.add_argument('--nfiles', dest='nfiles',
    action='store', type=str, default=None,
    help='How many files to process. If left to default, all files will '\
        +'be processed.')
parser.add_argument('--debug', dest='debug', action='store_true',
    help='Run this script with debugging enabled.')
parser.add_argument('--verbose', dest='verbose', action='store_true',
    help='Print out as much information into the terminal as possible.',
    default=False)

args = parser.parse_intermixed_args()

InDir = args.file_directory
OutDir = args.outdir
Force = args.force
Debug = args.debug
Verbose = args.verbose

if InDir[-1] != '/':
    InDir = InDir + '/'
if OutDir is None:
    OutDir = InDir
if OutDir[-1] != '/':
    OutDir = OutDir + '/'
    
if os.path.isdir(InDir):
    InDir_last = InDir.split('/')[-1]
else:
    raise ValueError('\nDirectory {} not found!\n'.format(InDir))

if not os.path.isdir(OutDir):
    print('{} Is not a directory. Would you like this to be created?')
    create = False
    while create is False:
        answer = input('    Enter \'yes/y\' or \'no/n\'')
        if answer == 'yes' or answer == 'y':
            create == True
        elif answer == 'no' or ansewr == 'n':
            sys.exit('\nExiting..\n')
        else: 
            pass
    # make the directory    
    os.system('mkdir {}'.format(OutDir))

InDir_list_split = InDir.split('/')
array_name = '{}-{}'.format(InDir_list_split[-3], InDir_list_split[-2])
if Verbose:
    print('Array prefixes: {}'.format(array_name))


#===========================================#
## LOOK FOR ROOT FILES IN OUTPUT DIRECTORY ##
#===========================================#
cmd='ls {}'.format(InDir)
if Verbose or Debug:
    print('cmd = {}'.format(cmd))

ls_dir_path = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
grep_npy = subprocess.run('grep .npy'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)

file_list_raw = grep_npy.stdout.decode('utf-8').split()

NAvailableFiles = len(file_list_raw)

nEvts = 0
for file in file_list_raw:
    X_tmp = np.load(file)
    nevts += X_tmp.shape[0]

nFeatures = X_tmp.shape[1]
X_all = np.empty((nEvts, nFeatures))

c = 0
for i, file in enumerate(file_list_raw):
    X_tmp = np.load(file)
    n_X_tmp = X_tmp.shape[0]
    X_all[c:c+n_X_tmp,:] = np.ndarray.copy(X_tmp)
    c += n_X_tmp
    
array_name += 'X_full'
np.save(X_all, array_name)















