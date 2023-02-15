#!/bin/bash
# -*- coding: utf-8 -*-

'''
Simple script to run data processing in parallel with multiple cores or threads
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes:  
'''

import numpy as np
import uproot as ur
import awkward as ak
import time as t
import matplotlib.pyplot as plt
import argparse, sys, os, subprocess, pickle, warnings, traceback
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from array_production import process_NTuples, err_process_NTuples

## DEFS ##
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
    return MCN, _XS, _Eff, _kFact

## PRETTY OUTPUT ##
print('\n===========================')
print('==  HH4B MASS REGRESSION ==')
print('==  Data Processing .... ==')
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
parser.add_argument('--threading', dest='threading', default=False,
    action='store_true',
    help='Uses multi-threading.')
parser.add_argument('--threads', dest='threads', default=1,
    type=int, action='store',
    help='Number of threads to use per core.')
parser.add_argument('--processes', dest='processes', default=False,
    action='store_true',
    help='Uses multiple CPUs.')
parser.add_argument('--workers', dest='workers', default=1,
    type=int, action='store',
    help='Number of CPUs to use.')
parser.add_argument('--test', dest='test', default=False,
    action='store_true',
    help='Process a single file.')
args = parser.parse_intermixed_args()

InDir = args.file_directory
OutDir = args.outdir
Debug = args.debug
Verbose = args.verbose
NFiles = args.nfiles
Threading = args.threading
Threads = args.threads
Processes = args.processes
Workers = args.workers
Test = args.test

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

# Set NFiles
if not NFiles is None:
    int_str_dict = dict()
    for x in range(1000):
        int_str_dict[str(x)] = x
    try:
        NFiles = int_str_dict[NFiles]
    except KeyError as kerr:
        raise KeyError('Requested files exceeds hard coded limit of 1000. Change this '\
            'or reduce the file number using hadd.')

    # Compare with NAvailableFiles
    if NFiles > NAvailableFiles:
        raise ValueError('Not enough files in file directory for --nfile'+\
            'Requested {} but have {}.'.format(NFiles, NAvailableFiles))
    elif NAvailableFiles == 0:
        raise FileNotFoundError('No root files exist in this directory!')
    
else:
    NFiles == NAvailableFiles

if not NFiles is None:
    if Processes > NFiles:
        warnings.warn('Requested Processes greater than number of files'\
                      +'\nRequested {}'.format(Processes)
                      +'\nReducing Processes to {}'.format(NFiles))
        Processes = NFiles
    
file_list_full = []
for container, filename, emSeaNum in full_info_list:
    file_list_full.append('{}{}/{}'.format(
        InDir, container, filename.rstrip()))

if (Verbose or Debug) and not Test:
    print('\nPrinting files in file list.')
    print('--'*20+'\n')
    for file in file_list_full:
        print(file)
    print('\n -- Number of files: {}\n'.format(len(file_list_full)))


    

#-----------------------------------#
## Run Distributed Data Processing ##
#-----------------------------------#
if Test:
    tTest0 = t.time()
    # maybe just run one file here
    if Verbose:
        print('\nRunning in testing mode..')
        print('--'*20+'\n')
    
    results_dict_raw = dict()
    results_returned = dict()    
    file = file_list_full[0]
    
    mcn = find_MC_num(file)  
    MC_args = find_MC_info(mcn, fname='PMGxsecDB_mc16.txt')
    arr_prefix = array_name+'.{}._{}'.format(mcn, 0)

    with ProcessPoolExecutor(max_workers=Workers) as e:

        if Verbose:
            print('Submitting process_NTuples to ProcessPoolExecutor: [{}]'.format(0))
            print('    File: {}'.format(file))
            print('    Array prefix: {}'.format(arr_prefix))
            print('    Destination: {}'.format(OutDir))
            print('    Monte-Carlo number: {}'.format(mcn))
            print('    MC args: ({}, {}, {}, {}) -- (MCN, XS, kFact, Eff)\n'.format(
                mcn, MC_args[0], MC_args[1], MC_args[2]))
        
        results_dict_raw[0] = e.submit(process_NTuples, 
                                       full_fpath=file,
                                       array_prefix=arr_prefix,
                                       dest=OutDir,
                                       Verbose=True,
                                       MCargs=MC_args
                                      )

    if Verbose:
        print('Processes finished. Showing results!\n')

    for i in range(len(results_dict_raw)):
        res = results_dict_raw[i]
        results_returned[i] = res.result()
        if Verbose:
            print('Result type: {}'.format(type(res)))
            print('Result: {}'.format(res))
            print(res.result())
    tTest1 = t.time()
    print('\nDone!')
    sys.exit('  {:8.4f} (s)\n'.format(tTest1 - tTest0))

if Debug:
    sys.exit('\nExiting due to debugging mode.\n')

## PROCESSES ONLY
if Processes and not Threading:
    tp0 = t.time()
    if Verbose:
        print('\nRunning using processes only..')
        print('--'*20+'\n')
    
    results_dict_raw = dict()
    results_returned = dict()
    
    with ProcessPoolExecutor(max_workers=Workers) as e:
        
        for i, file in enumerate(file_list_full):
            
            arr_prefix = array_name+'_{}'.format(i)
            mcn = find_MC_num(file)        
            MC_args = find_MC_info(mcn, fname='PMGxsecDB_mc16.txt')
            arr_prefix = array_name+'.{}._{}'.format(mcn, i)
            
            if Verbose:
                print('Submitting err_process_NTuples to '\
                      +'ProcessPoolExecutor: [{}]'.format(i))
                print('    File: {}'.format(file))
                print('    Array prefix: {}'.format(arr_prefix))
                print('    Destination: {}'.format(OutDir))
                print('    Monte-Carlo number: {}'.format(mcn))
                print('    MC args: ({}, {}, {}, {}) -- (MCN, XS, kFact, Eff)\n'.format(
                    mcn, MC_args[0], MC_args[1], MC_args[2]))
                
            results_dict_raw[i] = e.submit(err_process_NTuples, 
                                           full_fpath=file,
                                           array_prefix=arr_prefix,
                                           dest=OutDir,
                                           MCargs=MC_args
                                          )
        if Verbose:
            print('\n .. Waiting on ProcessPoolExecutor ..\n')
            
    if Verbose:
        print('Processes finished. Showing results!\n')

    for i in range(len(results_dict_raw)):
        res = results_dict_raw[i]
        results_returned[i] = res.result()
        if Verbose:
            print('\nProcess: {}'.format(i))
            print('Result type: {}'.format(type(res)))
            print('Result: {}'.format(res))
            print(res.result())
            
    ## Save results as a dictionary
    try:
        with open('{}{}_dict.pickle'.format(OutDir, array_name),
                  'wb') as picklefile:
            pickle.dump(results_returned, picklefile)
    except PickleError as pke:
        warnings.warn('Unable to pickle file. Printing PickleError: \n')
        print(traceback.format_exc())
        print()

    tp1 = t.time()
    if Verbose:
        print('\n..Done!..')
        print('  {:8.4f} (s)\n'.format(tp1 - tp0))


## THREADS ONLY
elif Threading and not Processes:
    print('\nRunning using threads only..\n')


## PROCESSES AND THREADS
elif Processes and Threading:
    print('\nRunning using processes and threads..\n')


## FOR LOOP
else:
    print('\nNo processes or threads selected..')
    usr_in = input('Are you sure you would like to continue? (y/n)\n')
    if not (usr_in == 'y' or usr_in == 'yes'):
        sys.exit()
    
    tloop0 = t.time()
    
    tloop1 = t.time()
        

    