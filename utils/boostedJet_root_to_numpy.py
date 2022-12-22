#!/bin/bash
# -*- coding: utf-8 -*-

'''
Script to create data pipeline for the signal and background
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes: For now there is several iteration steps which could potentially be
conglomerated into fewer steps. For now this doesn't present itself as a
significant time bottleneck for processing data. In the future however if
time becomes a factor for array production, this algorithm could be
improved.


*A note about the variable naming scheme..
boostedJets contains all the information about boosted jet substructure.
boostedJets_keys are ONLY the keys which we care about (other entries have null information)
boostedJets_normalized will contain all the normalized arrays WITH EVENT SELECTION APPLIED!!!
boostedJets_norm_mean will contain all the mean and standard deviations

* TO-DO: We need to fix the normalized variable dictionary somewhere else and load it here.
Currently it is implemented as-is in the jupyter notebook because we just want to get the
script running
'''


import numpy as np
import matplotlib.pyplot as plt
import uproot as ur
import awkward as ak
import argparse, sys, os, subprocess

## LOAD UTILS ##
cwd = os.getcwd()
path_head, path_tail = os.path.split(cwd)
sys.path.append(path_head+'/utils')
from ml_utils import dict_from_tree, DeltaR, tvt_num, round_to_sigfigs
from time import perf_counter as cput


print('\n===========================')
print('==  HH4B MASS REGRESSION ==')
print('===========================\n')
print('Numpy version: {}'.format(np.__version__))
print('Uproot version: {}'.format(ur.__version__))
print('Awkward version: {}\n'.format(ak.__version__))

# this is for nfiles
int_str_dict = dict()
for x in range(1000):
    int_str_dict[str(x)] = x

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
parser.add_argument('--outfolder', dest='outfolder',
    action='store', type=str, default=None,
    help='Output folder for the *.npy files. This will place *.npy files \
        inside separate folder inside the file_directory. If --outfolder \
        is provided this will be ignored.')
parser.add_argument('-f', dest='force', action='store_true',
    help='Will force the creation of input and output files.',
    default=False)
parser.add_argument('--nfiles', dest='nfiles',
    action='store', type=str, default='1',
    help='Input files including the parent directories.')
parser.add_argument('--debug', dest='debug', action='store_true',
    help='Run this script with debugging enabled.')
parser.add_argument('--verbose', dest='verbose', action='store_true',
    help='Print out as much information into the terminal as possible.',
    default=False)
args = parser.parse_args()

InDir = args.file_directory
OutDir = args.outdir
Debug = args.debug
Verbose = args.verbose
NFiles = args.nfiles

if InDir[-1] != '/':
    InDir = InDir + '/'
if OutDir is None:
    OutDir = InDir
if OutDir[-1] != '/':
    OutDir = OutDir + '/'

## TO-DO
# 5) run cuts and make the dictionary
# 6) Create the arrys from the dictionary and follow the naming convention

## DONE
# 1) take the input file and split it based on '/'
# 2) take the last parent directory, so -1 with the index
# 3) use this parent directory as the name for the output
# 4) we need to list the files contained in the parent directory to know how many
# to make and the naming convention


try:
    NFiles = int_str_dict[NFiles]
except KeyError as kerr:
    raise KeyError('Requested files exceeds hard coded limit of 1000. Change this '\
        'or reduce the file number using hadd.')

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

    
#=================================#
## DEFINE SUBSTRUCTURE VARIABLES ##
#=================================#
## 1) Define keys we care about (it's okay to hard code these)
kitchen_sink = ['m', 'pt', 'phi', 'eta', 'Split12', 'Split23', 'Split34',
            'tau1_wta', 'tau2_wta', 'tau3_wta', 'tau21_wta', 'tau32_wta',
            'ECF1', 'ECF2', 'ECF3', 'C2', 'D2', 'NTrimSubjets', 'Nclusters',
            'nTracks', 'ungrtrk500', 'EMFrac', 'nChargedParticles',
            'numConstituents']
truthJet_vars = ['truth_mHH', 'truthjet_antikt10_pt', 'truthjet_antikt10_eta',
           'truthjet_antikt10_phi', 'truthjet_antikt10_m']

# These are the substructure variables for which we have no information about
no_info = ['Split34', 'Nclusters', 'EMFrac', 'nChargedParticles']

for i, suffix in enumerate(kitchen_sink):
    kitchen_sink[i] = 'boostedJets_'+suffix
    
for i, suffix in enumerate(no_info):
    no_info[i] = 'boostedJets_'+suffix

if Verbose:
    print('\nNo information about the following:')
    print('-'*40)
    for name in no_info:
        print(name)
    
# This is the completed list for which we have all information
if Verbose:
    boostedJets_keys = []
    print('\nRelevant substructure variables:')
    print('-'*40)
    for cutlery in kitchen_sink:
        print(cutlery)
        if not cutlery in no_info:
            boostedJets_keys.append(cutlery)


#===========================================#
## LOOK FOR ROOT FILES IN OUTPUT DIRECTORY ##
#===========================================#
cmd='ls {}'.format(InDir)
if Verbose or Debug:
    print('cmd = {}'.format(cmd))

ls_dir_path = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
grep_root = subprocess.run('grep .root'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)

file_list_raw = grep_root.stdout.decode('utf-8').split()

NAvailableFiles = len(file_list_raw)
if NFiles > NAvailableFiles:
    raise ValueError('Not enough files in file directory for --nfile'+\
        'Requested {} but have {}.'.format(NFiles, NAvailableFiles))
elif NAvailableFiles == 0:
    raise FileNotFoundError('No root files exist in this directory!')

file_list = []
for filename in file_list_raw:
    file_list.append(filename.rstrip())

if Verbose or Debug:
    print('\nPrinting files in file list.')
    print('--'*20+'\n')
    for file in file_list:
        print(file)
    print()

    
temp_file = file_list[0]

## 2) UPROOT FILE and LOAD DICTIONARIES
#------------------------------------------------------------------------------
t0 = cput()
uprooted = ur.open(InDir+temp_file)
MNTuple = uprooted['XhhMiniNtuple']
boostedJets_dict = dict_from_tree(MNTuple, kitchen_sink, np_branches=None)
truthJets_dict = dict_from_tree(MNTuple, truthJet_vars, np_branches=None)
t1 = cput()
load_time = t1 - t0

nEvents = len(boostedJets_dict['boostedJets_m'])
if Verbose:
    print('Time to load arrays: {:8.4f} (s)'.format(load_time))
    print('{} Events'.format(nEvents))


## 3) MAKE CUTS ON JETS
## Find greater than two jets
gt_twoJets = np.zeros(nEvents, dtype=bool)
t0 = cput()
for i in range(nEvents):
    # just use jet pt as an arbitrary variable to look at how many jets
    boostedJets_pt = ak.to_numpy(boostedJets_dict['boostedJets_pt'][i])
    
    if len(boostedJets_pt) >=2:
        gt_twoJets[i] = True

n2jets = np.count_nonzero(gt_twoJets)
t1 = cput()
if Verbose:
    print('Number of events with > 2 jets: {}'.format(n2jets))
    print('Number of events total:         {}'.format(nEvents))
    print('                                {:5.2f} %'.format(n2jets*100/nEvents))
    print('time: {:8.2f} (s)'.format(t1 - t0))


## Match jets
#------------------------------------------------------------------------------
t0 = cput()
# Track the DR between truth jets for leading and subleading
# use -1 as an arbitrary flag
LeadingJet_DR2 = np.full((n2jets,), -1, dtype=np.float64)
subLeadingJet_DR2 = np.full((n2jets,), -1, dtype=np.float64)
matched_jet_bool = np.zeros((n2jets,), dtype=bool)

# int of events with more than two jets
list_indices = np.arange(nEvents)
evt_idx = np.ndarray.copy(list_indices[gt_twoJets])

matched_jets = []
for i, evt in enumerate(evt_idx):
    
    nTruthJets = ak.to_numpy(truthJets_dict['truthjet_antikt10_m'][evt]).shape[0]
    truthJet_coords = np.empty((nTruthJets, 2))
    # this can be vectorized easily (too tired)
    for j in range(nTruthJets):
        truthJet_coords[j,0] = truthJets_dict['truthjet_antikt10_eta'][evt][j]
        truthJet_coords[j,1] = truthJets_dict['truthjet_antikt10_phi'][evt][j]
    
    ## Leading Jet
    BoostedJet0_eta = boostedJets_dict['boostedJets_eta'][evt][0]
    BoostedJet0_phi = boostedJets_dict['boostedJets_phi'][evt][0]
    BoostedJet0_coords = np.array([BoostedJet0_eta, BoostedJet0_phi])
    LeadingJet_DR_arr = DeltaR(truthJet_coords, BoostedJet0_coords)
    
    # Find the deltaR for the leading jet
    LJ_DR = np.min(LeadingJet_DR_arr)
    LJ_DR_idx = np.argmin(LeadingJet_DR_arr)
    LJ_idx_bool = np.ones(LeadingJet_DR_arr.shape, dtype=bool)
    LJ_idx_bool[LJ_DR_idx] = False
    
    # Find the next closest delta R for the next jet ordered in pt
    LJ_DR2 = np.min(LeadingJet_DR_arr[LJ_idx_bool])
    
    ## Subleading Jet
    BoostedJet1_eta = boostedJets_dict['boostedJets_eta'][evt][1]
    BoostedJet1_phi = boostedJets_dict['boostedJets_phi'][evt][1]
    BoostedJet1_coords = np.array([BoostedJet1_eta, BoostedJet1_phi])
    subLeadingJet_DR_arr = DeltaR(truthJet_coords, BoostedJet1_coords)
    
    SLJ_DR = np.min(subLeadingJet_DR_arr)
    SLJ_DR_idx = np.argmin(subLeadingJet_DR_arr)
    SLJ_idx_bool = np.ones(subLeadingJet_DR_arr.shape, dtype=bool)
    SLJ_idx_bool[SLJ_DR_idx] = False
    
    SLJ_DR2 = np.min(subLeadingJet_DR_arr[SLJ_idx_bool])
    
    if SLJ_DR_idx != LJ_DR_idx:
        if LJ_DR < .1 and SLJ_DR < .1:
            matched_jets.append([evt, LJ_DR_idx, SLJ_DR_idx])
            matched_jet_bool[i] = True
            LeadingJet_DR2[i] = LJ_DR2
            subLeadingJet_DR2[i] = SLJ_DR2

matched_jets = np.array(matched_jets)
t1 = cput()
if Verbose:
    print('Time to complete jet matching: {:6.3f} (m)'.format((t1 - t0)/60))
    print('Shape:                         {}'.format(matched_jets.shape))


## FIND NAN VALUES
#------------------------------------------------------------------------------
boostedJets_norm_info = np.empty((len(boostedJets_keys), 2), dtype=np.float64)

matched_evt_indices = np.ndarray.copy(matched_jets[:,0])
matched_jet_indices = np.ndarray.copy(matched_jets[:,1:3])

''' We can iteratively figure out what events have substructure variables which
contain nan values by searching leading and subleading jets '''
# start assuming all events are fine so nan boolean is all False
# this is the length of the matched indices
evt_nan_bool = np.full((matched_evt_indices.shape[0],), False, dtype=bool)
t0 = cput()
for jetVar in boostedJets_keys:
    np_slice = ak.to_numpy(boostedJets_dict[jetVar]
                           [matched_evt_indices,:2])
    
    lead_jet_bool = np.isnan(np_slice[:,0])
    sublead_jet_bool = np.isnan(np_slice[:,1])
    
    # condense this to either jet having a nan in the substructure variable
    jets_bool = np.logical_or(lead_jet_bool, sublead_jet_bool)
    # update the event bool - sort of a memory for each substructure
    evt_nan_bool = np.logical_or(evt_nan_bool, jets_bool)
t1 = cput()

# we have an array which points to events which have nans. Invert this
# to find the good values for matched jets
evt_notNan_bool = np.invert(evt_nan_bool)
old_matched_evt_indices = np.ndarray.copy(matched_evt_indices)
matched_evt_indices = np.ndarray.copy(matched_evt_indices[evt_notNan_bool])

## Update Matched Jets!!! ##
matched_jets = np.ndarray.copy(matched_jets[evt_notNan_bool,:])

old_evt_num = old_matched_evt_indices.shape[0]
new_evt_num = matched_evt_indices.shape[0]
if Verbose:
    print(' {:6.2f} (s)'.format(t1 - t0))
    print('Before NaN test: {}'.format(old_evt_num))
    print('After NaN test: {}'.format(new_evt_num))
    print('Efficiency: {:5.2f} %'.format(new_evt_num*100/old_evt_num))

    print('\nPeek at matched jets info')
    print('Matched jets arary shape: {}'.format(matched_jets.shape))
    print('First five elements:\n{}'.format(matched_jets[:5,:]))

    
## Create a Mean and Standard Deviation dictionary!
#------------------------------------------------------------------------------
## SIGNIFICANT FIGURES HERE FOR NORMALIZATION
SIG_FIGS = 4

# boostedJets_mean_dict is a dictionary with an array containing the mean and
# standard deviation of all the relevant substructure variables
boostedJets_mean_dict = dict()
matched_evt_indices = matched_jets[:,0]
matched_jet_indices = matched_jets[:,1:3]

t0 = cput()
for var in boostedJets_keys:
    
    np_slice = ak.to_numpy(boostedJets_dict[var]
                           [matched_evt_indices,:2])
    
    flat_arr = np_slice.flatten()
    nan_bool = np.isnan(flat_arr)
    if np.any(nan_bool):
        raise ValueError('found nans')
        
    jetVar_mean = np.mean(flat_arr)
    jetVar_std = np.std(flat_arr)
    
    boostedJets_mean_dict[var] = round_to_sigfigs([jetVar_mean, jetVar_std],
                                                  sigfig=SIG_FIGS)
t1 = cput()

if Verbose:
    print(' {:6.2f} (s)'.format(t1 - t0))

    np.set_printoptions(precision=SIG_FIGS, suppress=True)
    for key, item in boostedJets_mean_dict.items():
        snstring = [np.format_float_scientific(x, precision=3, sign=True) for x in item]
        print('{:30s}-  {}'.format(key, snstring))


## Build Normalized Dictionary with Relevant Values Only
#------------------------------------------------------------------------------

## After inspecting the variables these are the variables which we want to log scale
log_vars = ['boostedJets_ECF1', 'boostedJets_ECF2', 'boostedJets_ECF3']

## just input these manually because we have seen the distributions
special_case_vars = ['boostedJets_NTrimSubjets', 'boostedJets_nTracks', 'boostedJets_ungrtrk500']
special_case_std = [1, 10, 10]
special_case_std_dict = dict(zip(special_case_vars, special_case_std))

boostedJets_normalized = dict()
boostedJets_norm_mean = dict()

if Verbose:
    print('\nConstructing normalized dictionary!\n')

for key in boostedJets_keys:
    var_mean = boostedJets_mean_dict[key][0]
    var_std = boostedJets_mean_dict[key][1]
    
    # for the slicing: first we take the leading and subleading jet so we have a
    # "rectangular" shape for the array slice, as well as the matched event
    # indices that we found prior
    np_slice = ak.to_numpy(boostedJets_dict[key][matched_evt_indices,:2])

    # Handle log scale variables separately
    if key in log_vars:
        nz_mask = np_slice == 0
        if np.any(nz_mask):
            if Verbose:
                print('Found zero values in ECF functions!!')
                print('Variable: {}\n'.format(key))
            raise ValueError('Found zero values in ECF functions!!')

        log_slice = np.log(np_slice)
        log_mean = np.mean(log_slice.flatten())
        log_std = np.std(log_slice.flatten())
        
        # need to make a small array for mean and std with same rounding scheme
        mean_sl = round_to_sigfigs([log_mean, log_std], sigfig=SIG_FIGS)
        boostedJets_norm_mean[key] = np.ndarray.copy(mean_sl)

        # set values in the dictionaries
        boostedJets_normalized[key] = (log_slice - log_mean) / log_std

    # discrete variables
    elif key in special_case_vars:
        ''' For now these seem to be the discrete variables, so we
        can get away with dealing with integers '''
        mean_spc = int(np.mean(np_slice))
        std_spc  = special_case_std_dict[key]

        # change these values in the dictionary
        boostedJets_norm_mean[key] = np.array([mean_spc, std_spc])

        # set values in the dictionaries
        boostedJets_normalized[key] = (np_slice - mean_spc) / std_spc

    # normalization procedure for 'normal' continuous variables 
    else:
        # nothing to modify about mean/std, so just make a copy
        boostedJets_norm_mean[key] = np.ndarray.copy(
            boostedJets_mean_dict[key])  
        
        # standard normalization procedure
        boostedJets_normalized[key] = (np_slice - var_mean) / var_std
                       
        
    if Verbose:
        print('-- {} --'.format(key))
        print('-'*40)
        print('mean: {}'.format(boostedJets_norm_mean[key][0]))
        print('std: {}'.format(boostedJets_norm_mean[key][1]))
        print(np_slice.shape)
        print()

if Verbose:
    print('\nFinished constructing normalized dictionary!\n')

    
## Fill truth arrays with relevant variables
#------------------------------------------------------------------------------

## TRUTH
Y = np.empty((matched_jets.shape[0],2))
t0 = cput()
for i in range(matched_jets.shape[0]):
    evt, ld_idx, sld_idx = matched_jets[i,:]
    
    # Truth Jet
    ''' in rare circumstances these can be mismatched with reco
    jets so we need to be consistent with this! '''
    Y[i,0] = truthJets_dict['truthjet_antikt10_m'][evt][ld_idx]
    Y[i,1] = truthJets_dict['truthjet_antikt10_m'][evt][sld_idx]
t1 = cput()

if Verbose:
    print(' {:6.2f} (s)'.format(t1 - t0))

## Normalize Target:
Yn = (Y - 1e5) / 1e5 #this is in MeV


## RECO JETS
Nvars = len(boostedJets_keys)
nEvts_new = boostedJets_normalized[boostedJets_keys[0]].shape[0]

if Verbose:
    print(Nvars)
    print(nEvts_new)

t0 = cput()
# Inputs
#-------------------------------------#
X_all = np.empty((nEvts_new, 2*Nvars))

X_nomass_list, X_nomasspt_list = [], []
for j, key in enumerate(boostedJets_keys):
    # leading jet, take the 0th index
    X_all[:,j] = boostedJets_normalized[key][:,0]
    # subleading jet
    X_all[:,j+Nvars-1] = boostedJets_normalized[key][:,1]
    
    # these lists control variables to train on!
    if not key == 'boostedJets_m':
        X_nomass_list.append(key)
    if not key in ['boostedJets_m', 'boostedJets_pt']:
        X_nomasspt_list.append(key)
        
# # create an X array which has the same number of features as the list
# X_nomass = np.empty((nEvts_new, 2*(Nvars -1 )))
# skip = int(np.floor(len(X_nomass_list)))
# for j, key in enumerate(X_nomass_list):
#     j2 = j + skip
#     X_nomass[:,j] = boostedJets_normalized[key][:,0]
#     X_nomass[:,j2] = boostedJets_normalized[key][:,1]

# # similarly, xnomass_pt does not have mass or pt for the jets
# X_nomasspt = np.empty((nEvts_new, 2*(Nvars -2 )))
# skip = int(np.floor(len(X_nomasspt_list)))
# for j, key in enumerate(X_nomasspt_list):
#     j2 = j + skip
#     X_nomasspt[:,j] = boostedJets_normalized[key][:,0]
#     X_nomasspt[:,j2] = boostedJets_normalized[key][:,1]
#-------------------------------------#
t1 - cput()

if Verbose:
    print('Time to fill input array')
    print(' {:6.2f} (s)'.format(t1 - t0))

    
## Save these arrays!
if Verbose:
    print('X shape: {}'.format(X_all.shape))
    print('Y shape: {}'.format(Y.shape))
    
print('\n .. le fin .. \n\n')

