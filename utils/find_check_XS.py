#!/bin/bash
# -*- coding: utf-8 -*-

'''
Script to check cross sections of each process. Sanity check included for each root file
to compare with one another to see if the XS is the same! Raise value error if not.
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes:  
'''

import numpy as np
import uproot as ur
import awkward as ak
import argparse, sys, os, subprocess, pickle, warnings
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from array_production import process_NTuples, err_process_NTuples

def find_MC_num(_str):
    spl_str = _str.split('.')
    mSeaNum = None
    for substr in spl_str:
        if len(substr) == 6 and substr.isdigit():
            mSeaNum = substr
    return mSeaNum

def find_MC_info(MCN, fname='PMGxsecDB_mc16.txt'):
    MC_inf_arr = np.loadtxt(fname, skiprows=1, usecols=(0,2,3,4),
                            dtype=float, encoding='ascii')
    MCN_full = np.full(MC_inf_arr[:,0].shape, MCN, dtype=float)
    row_idx = np.argmax(MCN_full == MC_inf_arr[:,0])
    row = MC_inf_arr[row_idx,:]
    _XS, _Eff, _kFact = row[1:]
    return _XS, _Eff, _kFact

print('\n===========================')
print('==  HH4B MASS REGRESSION ==')
print('==  Check XS Information ==')
print('===========================\n')
print('Numpy version: {}'.format(np.__version__))
print('Uproot version: {}'.format(ur.__version__))
print('Awkward version: {}\n'.format(ak.__version__))

## ARGPARSING ##
parser = argparse.ArgumentParser(description='Main script to create numpy\
    .npy files from root files.')
parser.add_argument('file_directory', #positional argument
    action='store',
    type=str, default=None,
    help='Directory where the root files live.')
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
parser.add_argument('--test', dest='test', default=False,
    action='store_true',
    help='Process a single file.')
args = parser.parse_intermixed_args()

InDir = args.file_directory
Debug = args.debug
Verbose = args.verbose
NFiles = args.nfiles
Test = args.test

if InDir[-1] != '/':
    InDir = InDir + '/'
    
if os.path.isdir(InDir):
    InDir_last = InDir.split('/')[-1]
else:
    raise ValueError('\nDirectory {} not found!\n'.format(InDir))


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
grep_root = subprocess.run('grep .root'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)

# get a list of all the containers
containers = grep_root.stdout.decode('utf-8').split()

# loop through the containers and create a list with the files inside
full_info_list = []
for container in containers:
    
    MCnum = find_MC_num(container)
    if MCnum is None:
        raise ValueError('\nCould not find MC Number in container.\n')
        
    ls_container = subprocess.run('ls {}{}'.format(InDir, container).split(),
                                    stdout=subprocess.PIPE)
    grep_root = subprocess.run('grep .root'.split(),
                              input=ls_container.stdout,
                               stdout=subprocess.PIPE)
    files_in_container = grep_root.stdout.decode('utf-8').split()
    
    for file in files_in_container:
        full_info_list.append((container, file, MCnum))

if Debug:
    for tup_obj in full_info_list:
        print('container: {}'.format(tup_obj[0]))
        print('file inside: {}'.format(tup_obj[1]))
        print('MCnum: {}'.format(tup_obj[2]))
    
NAvailableFiles = len(full_info_list)
    
file_list_full = []
XS_list = []
MCN_dict = dict()
for container, filename, emSeaNum in full_info_list:
    file_list_full.append('{}{}/{}'.format(
        InDir, container, filename.rstrip()))
    
    xs, eff, kfact = find_MC_info(emSeaNum, fname='PMGxsecDB_mc16.txt')
    if not str(emSeaNum) in MCN_dict.keys():
        MCN_dict[str(emSeaNum)] = [xs]
    else:
        MCN_dict[str(emSeaNum)].append(xs)

        
print(' -- MCN Cross Sections -- ')
print('-'*26+'\n')
for mcn in MCN_dict.keys():
    for xs in MCN_dict[mcn][1:]:
        if xs != MCN_dict[mcn][0]:
            warnings.warn('Warning: different cross sections found'\
                         +' for MC# {}'.format(mcn))

    print(' -- {} cross section: {}\n'.format(mcn, MCN_dict[mcn][0]))

