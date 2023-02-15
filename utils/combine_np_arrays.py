#!/bin/bash
# -*- coding: utf-8 -*-

'''
Combine the numpy arrays into a single array for signal or background
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes: This code should only be carried out for pt slices of the same process.
Some signals for vbf analysis this is not the case, so this code should not
be executed.

- Eventually get rid of the reduced arrays in the procedure that was carried
out before. It works but for the wrong reasons. Keep it as it works for now.
'''

import numpy as np
import sys, os, subprocess, time, argparse, warnings, copy, pickle
from time import perf_counter as cput

def accept_reject(p, n, replacement=True):
    selection = False
    indices = list(range(len(p)))
    choices = []
    max_p = np.max(p)
    while selection == False:
        ranf = np.random.uniform(low=0, high=max_p)
        rand_int = np.random.randint(low=0, high=len(indices))
        rand_idx = indices[rand_int]
        if ranf < p[rand_idx]:
            choices.append(rand_idx)
            selection = True
            if replacement == False:
                indices.remove(rand_idx)
    return choices

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
parser.add_argument('--job_summary', dest='job_summary', action='store_true',
    help='Summarize the job in the pickle file.',
    default=False)
parser.add_argument('--downsampling', dest='downsampling', action='store',
    help='Down-sample the MC events to create an *effective* sample. '\
        +'This reduces the need for carrying weights.',
    choices=['replacement', 'no-replacement'],
    nargs=1, type=str, default=None)

args = parser.parse_intermixed_args()

InDir = args.file_directory
OutDir = args.outdir
Force = args.force
Debug = args.debug
Verbose = args.verbose
JobSummary = args.job_summary
Downsample = args.downsampling

if not Downsample is None:
    Downsample = Downsample[0]
    if Downsample != 'replacement' and Downsample != 'no-replacement':
        raise ValueError('Unrecognized argument passed to --downsampling')

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


#===================================================#
## REFINE LISTS OF NUMPY FILES IN OUTPUT DIRECTORY ##
#===================================================#
cmd='ls {}'.format(InDir)
if Verbose or Debug:
    print('cmd = {}'.format(cmd))

ls_dir_path = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
grep_npy = subprocess.run('grep .npy'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)
grep_pickle = subprocess.run('grep .pickle'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)
file_list_raw = grep_npy.stdout.decode('utf-8').split()
pickle_files = grep_pickle.stdout.decode('utf-8').split()

# Eliminate combined files
for f in copy.copy(file_list_raw):
    if 'all' in f:
        file_list_raw.remove(f)
        
if len(file_list_raw)/3 % 1 != 0:
    raise ValueError('\nExpected *.npy files to be multiple of three.'\
                     +' Check file outputs.\n')
NAvailableFiles = int(len(file_list_raw)/3)
filenum_last = int(file_list_raw[-1].split('.')[-2].split('_')[1])
if Verbose:
    print('last filenum: {}'.format(filenum_last))
    print('NAvailableFiles: {}'.format(NAvailableFiles))

if Debug:
    print('-- debugging mode -- printing all files in list')
    for file in file_list_raw:
        print(file)
    print('\n-- NAvailableFiles: {}'.format(NAvailableFiles))
    print('-- last file number: {}\n'.format(filenum_last))

nEvts = 0
file_list_X, file_list_Y, file_list_MC = [], [], []
# makes a more efficient search
file_list_raw_reduced = copy.copy(file_list_raw)
MC_numbers = []

for filenum in range(filenum_last+1):
    xf_str = '_{}_X'.format(filenum)
    yf_str = '_{}_Y'.format(filenum)
    mcf_str = '_{}_mc'.format(filenum)
    found_x, found_y, found_mc = False, False, False
    
    # need to copy list because .remove() produced unexpected behaviour
    # with list that was iterated through!!!
    for file in copy.copy(file_list_raw_reduced):
        f_suffix = file.split('.')[-2]
        MC_tag = file.split('.')[-3]
        if f_suffix == xf_str:
            file_list_X.append(file)
            file_list_raw_reduced.remove(file)
            found_x = True
        elif f_suffix == yf_str:
            file_list_Y.append(file)
            file_list_raw_reduced.remove(file)
            found_y = True
        elif f_suffix == mcf_str:
            file_list_MC.append(file)
            file_list_raw_reduced.remove(file)
            found_mc = True
        
        if not MC_tag in MC_numbers:
            MC_numbers.append(MC_tag)
            
        if found_y and found_x and found_mc:
            break
            
    if (found_x and found_y and found_mc) == False:
        warnings.warn('Missing {}, {}, {}'.format(
            xf_str, yf_str, mcf_str))

if Debug:
    print('\nleftover files:')
    for file in file_list_raw_reduced:
        print(file)
    print('\nMonte-Carlo numbers:')
    for MC_numba in MC_numbers:
        print(MC_numba)
    print('\nprinting file list X, Y, MC')
    for xf, yf, mcf in zip(file_list_X, file_list_Y, file_list_MC):
        print(xf)
        print(yf)
        print(mcf)
        print()


#===========================#
## Loop through Job Status ##
#===========================#
''' For now we are safe because the MC numbers are different for each file
however this does not scale. We will need to devise a different scheme to
deal with this on a per MC number basis. 

Part of this is superfluous and needs to be re-written after the mcEventWeight
changes to the code.
'''
if len(pickle_files) != 1:
    raise ValueError('\nExpected only one pickle file in directory.\n')
else:
    pickle_file = open(InDir+pickle_files[0], 'rb')
job_sum = pickle.load(pickle_file)

if JobSummary:
    for key in job_sum.keys():
        job_tmp = job_sum[key]
        print('\nJob Number: {}'.format(key))
        print('\nprinting keys..')
        for tkey, value in job_tmp.items():
            print('{}: {}'.format(tkey, value))
        print()


N_ph, XS_tot, SF_lg = 0, 0, 0
for key in job_sum.keys():
    job_tmp = job_sum[key]
    
    if job_tmp['status'] == 'failed':
        continue
    
    # keep track of physical events and total cross section
    N_ph += job_tmp['N_ph']
    XS_tot += job_tmp['XS']
    
    # find largest scale factor to normalize
    if job_tmp['SF'] > SF_lg:
        SF_lg = job_tmp['SF']

    if Verbose:
        print('\nprinting keys..')
        for key, value in job_tmp.items():
            print('{}: {}'.format(key, value))
        print()


nEvt_tot = 0 # this is with scaling down using SF
N_mc_tot = 0 # this is the total MC events we have
good_keys = [] # jobs which did not fail or are not empty
norm_dict = dict() # hold values relevant for combination
mcEventWeight_sum_sel = 0
for key, MCi in zip(job_sum.keys(), file_list_MC):
    
    if job_sum[key]['status'] == 'failed':
        continue

    good_keys.append(key)

    # track number of events based on scale factors
    norm_dict[key] = dict()
    ratio = job_sum[key]['SF'] / SF_lg
    norm_dict[key]['SF'] = ratio
    nEvts = round(job_sum[key]['N_mc'] * ratio)    
    norm_dict[key]['num'] =  nEvts
    nEvt_tot += nEvts

    # track total MC events (for full arrays)
    N_mc_tot += job_sum[key]['N_mc']

    # track N events based on mcEventWeights
    tmp_arr = np.load(InDir+MCi)
    norm_dict[key]['adj_sum_mcEventWeight'] = np.sum(tmp_arr) * ratio
    mcEventWeight_sum_sel += norm_dict[key]['adj_sum_mcEventWeight']
    
# one last loop (sadly this has to be done in succession)
nEvt_tot_ds = 0 # finding the total event with mc-downsampling
for key, MCi in zip(job_sum.keys(), file_list_MC):
    if job_sum[key]['status'] == 'failed':
        continue
    num_ds = int(norm_dict[key]['adj_sum_mcEventWeight']\
                       / mcEventWeight_sum_sel)
    nEvt_tot_ds += num_ds
    norm_dict[key]['num_ds'] = nEvt_tot_ds
    
if Verbose:
    print('\n -- Summary for data --')
    print('Total events physical {:6.2e}'.format(N_ph))
    print('Total cross section: {:6.2e}\n'.format(XS_tot))

    
# save info to a text file here
with open(InDir+'Physics_Info.txt', 'w') as f:
    f.write('## '+str(InDir))
    f.write('## Cross Section')
    f.write(str(XS_tot))


#=================================#
## Combine numpy arrays finally! ##
#=================================#
X_all = np.empty((nEvt_tot, 40))
Y_all = np.empty((nEvt_tot, 2))
MC_all = np.empty((nEvt_tot,))

X_full = np.empty((N_mc_tot, 40))
Y_full = np.empty((N_mc_tot, 2))
MC_full = np.empty((N_mc_tot,))

if not Downsample is None:
    X_alld = np.empty((nEvt_tot, 40))
    Y_alld = np.empty((nEvt_tot, 2))
    MC_alld = np.empty((nEvt_tot,))

if Debug:
    print('\nCombining arrays..')
    print('Size of X_all: {}'.format(X_all.shape))
    print('Size of X_full: {}\n'.format(X_full.shape))

sv_count = 0
sv_count2 = 0
sv_count3 = 0
for key, Xi, Yi, MCi in zip(good_keys, file_list_X, file_list_Y, file_list_MC):
    
    # this is redundant as we already check for good keys
    if job_sum[key]['status'] == 'failed':
        if Debug:
            print('\nKey: {}'.format(key))
            print('Job status: {}'.format(job_sum[key]['status']))
        continue

    # N_mc = job_sum[key]['N_mc']
    norm_vals = norm_dict[key]
    num = norm_vals['num'] # subset number based on normalized SF
    SF_adj = norm_vals['SF'] # legacy from when we 'normalized' the SF
    num_ds = norm_vals['num_ds'] # number to downsample to based on weights
    X_tmp = np.load(InDir+Xi)
    Y_tmp = np.load(InDir+Yi)
    MC_tmp = np.load(InDir+MCi)
    num_full = X_tmp.shape[0]

    if Debug:
        print('\nkey: {}'.format(key))
        print('Job status: {}'.format(job_sum[key]['status']))
        print('num: {}'.format(num))
        print('save count: {}'.format(sv_count))

    # Regular arrays
    high_idx = num + sv_count
    subset = np.random.choice(np.arange(num_full),
                              size=(num,), replace=False)
    X_all[sv_count:high_idx, :] = X_tmp[subset,:]
    Y_all[sv_count:high_idx, :] = Y_tmp[subset,:]
    MC_all[sv_count:high_idx] = MC_tmp[subset]

    # full arrays
    high_idx2 = num_full + sv_count2
    X_full[sv_count2:high_idx2, :] = X_tmp
    Y_full[sv_count2:high_idx2, :] = Y_tmp
    MC_full[sv_count2:high_idx2] = MC_tmp * SF_adj
    
    # Downsampled arrays
    if not Downsample is None:
        # get probabilities somehow
        mc_sum = norm_vals['adj_sum_mcEventWeight']
        mc_prob = MC_tmp * SF_adj / mc_sum
        high_idx3 = num_ds + sv_count3
        
        if Downsample == 'replacement':
            choices = accept_reject(mc_prob, num_ds, replacement=True)
        if Downsample == 'no-replacement':
            choices = accept_reject(mc_prob, num_ds, replacement=False)

        # random array choice
        if Debug:
            print('num random choices: {}'.format(len(choices)))
        X_alld[sv_count3:high_idx3, :] = X_tmp[choices,:]
        Y_alld[sv_count3:high_idx3, :] = Y_tmp[choices,:]
    
    # update counter
    sv_count += num
    sv_count2 += num_full
    sv_count3 += num_ds
    
if Verbose:
    print('\n..Saving arrays..')
# Save regular arrays here
np.save(OutDir+'X_all', X_all)
np.save(OutDir+'Y_all', Y_all)
np.save(OutDir+'MC_all', MC_all)

# Save full random output here
np.save(OutDir+'X_allf', X_full)
np.save(OutDir+'Y_allf', Y_full)
np.save(OutDir+'MC_allf', MC_full)

# Save random choices here
if not Downsample is None:
    np.save(OutDir+'X_alld', X_alld)
    np.save(OutDir+'Y_alld', Y_alld)
    
if Verbose:
    print('\n..Done!..\n')

    