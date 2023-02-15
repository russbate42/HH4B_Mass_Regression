#!/bin/bash
# -*- coding: utf-8 -*-

'''
Script containing the data processing pipeline as a funtion, which is to be 
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes: For now there is several iteration steps which could potentially be
conglomerated into fewer steps. For now this doesn't present itself as a
significant time bottleneck for processing data. In the future however if
time becomes a factor for array production, this algorithm could be
improved.

The reason why we use dictionaries with keys for the variables is such that we
can create subsets of input arrays should we choose, by creating a list of
subset variables

*A note about the variable naming scheme..
boostedJets_keys are ONLY the keys which we care about (other entries have null information)
boostedJets_normalized will contain all the normalized arrays WITH EVENT SELECTION APPLIED!!!
boostedJets_mean_std_dict will contain all the mean and standard deviations

Note we need to keep track of the **sum of the sum of weights** when we scale to more files

* TO-DO: We need to fix the normalized variable dictionary somewhere else and load it here.
Currently it is implemented as-is in the jupyter notebook because we just want to get the
script running
'''


## Loading Utils
#======================================

import numpy as np
import uproot as ur
import awkward as ak
import sys, os, subprocess, time, traceback, random
from time import perf_counter as cput
import time as t

cwd = os.getcwd()
path_head, path_tail = os.path.split(cwd)
sys.path.append(path_head+'/utils')
from ml_utils import dict_from_tree, DeltaR, tvt_num, round_to_sigfigs
from helpers import boostedJets_mean_std_dict, log_vars, truthJet_vars
from helpers import boostedJets_keys



#=========================================================#
## ------------- The Business -------------------------- ##
#=========================================================#
def process_NTuples(full_fpath, array_prefix, dest, Verbose=False,
                    MCargs=None, lumi=36.20766):
    ''' hard code luminosity from 2015-2016 because that's what we are focusing
    on for now. This number can change later. '''
    
    ## 1)
    ## DEFINE SUBSTRUCTURE VARIABLES ##
    #-------------------------------------------------------------------------#
    ''' Note this step is being cut away using helpers.py module'''
    # nonlocal boostedJets_mean_std_dict, log_vars, truthJet_vars
    # nonlocal boostedJets_keys
    from ml_utils import dict_from_tree, DeltaR, tvt_num, round_to_sigfigs
    from helpers import boostedJets_mean_std_dict, log_vars, truthJet_vars
    from helpers import boostedJets_keys
    #-------------------------------------------------------------------------#

                
    ## 2)
    ## UPROOT FILE and LOAD DICTIONARIES ##
    #-------------------------------------------------------------------------#
    t0 = cput()
    uprooted = ur.open(full_fpath)
    MNTuple = uprooted['XhhMiniNtuple']
    boostedJets_dict = dict_from_tree(MNTuple, boostedJets_keys,
                                      np_branches=None)
    truthJets_dict = dict_from_tree(MNTuple, truthJet_vars, np_branches=None)
    mc_event_weights = ak.to_numpy(MNTuple.arrays(
        filter_name='mcEventWeight')['mcEventWeight'])
    t1 = cput()
    load_time = t1 - t0

    nEvents = len(boostedJets_dict['boostedJets_m'])
    if Verbose:
        print('{} Events'.format(nEvents))
        print('Time to load arrays: {:8.4f} (s)'.format(load_time))
    
    ## 2.1)
    ## UNPACK INFO REGARDING MC DATA and get the sum of weights!
    if not MCargs is None:
        MCN, XS, Eff, kFact = MCargs
        
    # This is hacky?
    MetaData = uprooted['MetaData_EventCount_XhhMiniNtuple']
    sum_of_weights = MetaData.to_numpy()[0][3]
    #-------------------------------------------------------------------------#
    
        
    ## 3)
    ## MAKE CUTS ON JETS ##
    #-------------------------------------------------------------------------#
    # Find greater than two jets
    gt_twoJets = np.zeros(nEvents, dtype=bool)
    t0 = cput()
    # Notes: this for loop could have masking with awkward arrays for psuedo
    # vectorization
    for i in range(nEvents):
        # just use jet pt as an arbitrary variable to look at how many jets
        boostedJets_pt = ak.to_numpy(boostedJets_dict['boostedJets_pt'][i])

        if len(boostedJets_pt) >= 2:
            gt_twoJets[i] = True

    n2jets = np.count_nonzero(gt_twoJets)
    t1 = cput()
    twojets_cut_time = t1 - t0
    if Verbose:
        print('Number of events with >= 2 jets: {}'.format(n2jets))
        print('Number of events total:         {}'.format(nEvents))
        print('                                {:5.2f} %'.format(n2jets*100/nEvents))
        print('time: {:8.2f} (s)'.format(twojets_cut_time))
    #-------------------------------------------------------------------------#
    

    ## 4)
    ## MATCH JETS ##
    #-------------------------------------------------------------------------#
    t0 = cput()
    # Track the DR between truth jets for leading and subleading
    # use -1 as an arbitrary flag
    # We don't need to compare deltaR to next nearest jet here as we are simply
    # processing. These comparisons are done in the notebook
    matched_jet_bool = np.zeros((n2jets,), dtype=bool)

    # int of events with more than two jets
    list_indices = np.arange(nEvents)
    evt_idx = np.ndarray.copy(list_indices[gt_twoJets])

    matched_jets = []
    # use <evt> as marker for greater than two jets matched
    for i, evt in enumerate(evt_idx):

        # create truth jet coordinate array
        nTruthJets = ak.to_numpy(truthJets_dict['truthjet_antikt10_m'][evt]).shape[0]
        nBoostedJets = ak.to_numpy(boostedJets_dict['boostedJets_pt'][evt]).shape[0]
        if nTruthJets < 2 or nBoostedJets < 2:
            continue
        truthJet_coords = np.empty((nTruthJets, 2))
        truthJet_coords[:,0] = ak.to_numpy(truthJets_dict['truthjet_antikt10_eta'][evt])
        truthJet_coords[:,1] = ak.to_numpy(truthJets_dict['truthjet_antikt10_phi'][evt])
        
        ## Leading Jet
        BoostedJet0_coords = np.array([
            boostedJets_dict['boostedJets_eta'][evt][0],
            boostedJets_dict['boostedJets_phi'][evt][0]]
        )
        LeadingJet_DR_arr = DeltaR(truthJet_coords, BoostedJet0_coords)

        # Find the deltaR for the leading jet
        LJ_DR = np.min(LeadingJet_DR_arr)
        LJ_DR_idx = np.argmin(LeadingJet_DR_arr)

        # Find the next closest delta R for the next jet ordered in pt
        # Need to create a boolean mask, to mask out the first search result
        LJ_idx_bool = np.ones(LeadingJet_DR_arr.shape, dtype=bool)
        LJ_idx_bool[LJ_DR_idx] = False
        LJ_DR2 = np.min(LeadingJet_DR_arr[LJ_idx_bool])

        ## Subleading Jet
        BoostedJet1_coords = np.array([
            boostedJets_dict['boostedJets_eta'][evt][1],
            boostedJets_dict['boostedJets_phi'][evt][1]]
        )
        subLeadingJet_DR_arr = DeltaR(truthJet_coords, BoostedJet1_coords)

        SLJ_DR = np.min(subLeadingJet_DR_arr)
        SLJ_DR_idx = np.argmin(subLeadingJet_DR_arr)
        SLJ_idx_bool = np.ones(subLeadingJet_DR_arr.shape, dtype=bool)
        SLJ_idx_bool[SLJ_DR_idx] = False
        SLJ_DR2 = np.min(subLeadingJet_DR_arr[SLJ_idx_bool])

        
        if SLJ_DR_idx == LJ_DR_idx or (LJ_DR > .1 or SLJ_DR > .1):
            # fail the condition
            continue
        else:
            matched_jets.append([evt, LJ_DR_idx, SLJ_DR_idx])
            matched_jet_bool[i] = True

    # try to catch weird bug
    if len(matched_jets) == 0:
        raise ValueError('No matching jets')
    else:
        matched_jets = np.array(matched_jets)
    
    t1 = cput()
    matched_jets_time = t1 - t0
    if Verbose:
        print('Shape:                         {}'.format(matched_jets.shape))
        print('Time to complete jet matching: {:6.3f} (m)'.format(
            matched_jets_time/60))
    #-------------------------------------------------------------------------#
    
    
    ## 5)
    ## FIND NAN VALUES
    #-------------------------------------------------------------------------#
    t0 = cput()
    boostedJets_norm_info = np.empty((len(boostedJets_keys), 2),
                                     dtype=np.float64)
    matched_evt_indices = np.ndarray.copy(matched_jets[:,0])
    matched_jet_indices = np.ndarray.copy(matched_jets[:,1:3])

    ''' We can iteratively figure out what events have substructure variables which
    contain nan values by searching leading and subleading jets '''
    # start assuming all events are fine so nan boolean is all False
    # this is the length of the matched indices
    evt_nan_bool = np.full((matched_evt_indices.shape[0],), False, dtype=bool)
    # loop through all the relevant variables
    for jetVar in boostedJets_keys:
        np_slice = ak.to_numpy(boostedJets_dict[jetVar]
                               [matched_evt_indices,:2])

        lead_jet_bool = np.isnan(np_slice[:,0])
        sublead_jet_bool = np.isnan(np_slice[:,1])

        # condense this to either jet having a nan in the substructure variable
        jets_bool = np.logical_or(lead_jet_bool, sublead_jet_bool)
        # update the event bool - sort of a memory for each substructure
        evt_nan_bool = np.logical_or(evt_nan_bool, jets_bool)

    # we have an array which points to events which have nans. Invert this
    # to find the good values for matched jets
    evt_notNan_bool = np.invert(evt_nan_bool)
    old_matched_evt_indices = matched_evt_indices
    matched_evt_indices = np.ndarray.copy(matched_evt_indices[evt_notNan_bool])

    ## Update Matched Jets!!! ##
    matched_jets = np.ndarray.copy(matched_jets[evt_notNan_bool,:])

    old_evt_num = old_matched_evt_indices.shape[0]
    new_evt_num = matched_evt_indices.shape[0]
    t1 = cput()
    nan_time = t1 - t0
    
    if Verbose:
        print('Before NaN test: {}'.format(old_evt_num))
        print('After NaN test: {}'.format(new_evt_num))
        print('Efficiency: {:5.2f} %'.format(new_evt_num*100/old_evt_num))

        print('\nPeek at matched jets info')
        print('Matched jets arary shape: {}'.format(matched_jets.shape))
        print('First five elements:\n{}'.format(matched_jets[:5,:]))
        print(' {:6.2f} (s)'.format(nan_time))
    #-------------------------------------------------------------------------#

    
    ## TO-DO: COMBINE 6 and 8!
    ## 6) 
    ## LOAD NORMALIZED DICTIONARY AND NORMALIZE VALUES
    #-------------------------------------------------------------------------#
    if Verbose:
        print('\nNormalizing variables')
    t0 = cput()
    
    ## LOAD NORMALIZED DICTIONARY HERE!!!
    # assume we have this for development purposes now
    
    boostedJets_normalized = dict()

    for key in boostedJets_keys:
        var_mean = boostedJets_mean_std_dict[key][0]
        var_std = boostedJets_mean_std_dict[key][1]

        # for the slicing: first we take the leading and subleading jet so we have a
        # "rectangular" shape for the array slice, as well as the matched event
        # indices that we found prior
        np_slice = ak.to_numpy(boostedJets_dict[key][matched_evt_indices,:2])
        
        # take log before standard normalization procedure
        if key in log_vars:
            log_slice = np.log(np_slice)
            boostedJets_normalized[key] = (log_slice - var_mean) / var_std
            
        # standard normalization procedure
        else: 
            boostedJets_normalized[key] = (np_slice - var_mean) / var_std

        # if Verbose:
        #     print('-- {} --'.format(key))
        #     print('-'*40)
        #     print('mean: {}'.format(boostedJets_mean_std_dict[key][0]))
        #     print('std: {}'.format(boostedJets_mean_std_dict[key][1]))
        #     print()

    t1 = cput()
    normalize_time = t1 - t0
    if Verbose:
        print('Finished constructing normalized dictionary!')
        print(' {:6.2f} (s)\n'.format(normalize_time))
    #-------------------------------------------------------------------------#
    
    
    ## 7)
    ## FILL TRUTH ARRAYS WITH RELEVANT VARIABLES
    #-------------------------------------------------------------------------#
    t0 = cput()
    Y = np.empty((matched_jets.shape[0],2))
    # could eliminate this for loop with proper array slicing
    for i in range(matched_jets.shape[0]):
        evt, ld_idx, sld_idx = matched_jets[i,:]

        # Truth Jet
        ''' in rare circumstances these can be mismatched with reco
        jets so we need to be consistent with this! '''
        Y[i,0] = truthJets_dict['truthjet_antikt10_m'][evt][ld_idx]
        Y[i,1] = truthJets_dict['truthjet_antikt10_m'][evt][sld_idx]

    ## Normalize Target:
    Yn = (Y - 1e5) / 1e5 #this is in MeV
    t1 = cput()
    truth_var_time = t1 - t0
    
    if Verbose:
        print('Finished filling truth jets!')
        print(' {:6.2f} (s)\n'.format(truth_var_time))
    #-------------------------------------------------------------------------#


    ## 8)
    ## FILL INPUT ARRAYS
    #-------------------------------------------------------------------------#
    t0 = cput()
    Nvars = len(boostedJets_keys)
    X_all = np.empty((matched_jets.shape[0], 2*Nvars))

    for j, key in enumerate(boostedJets_keys):
        # leading jet, take the 0th index
        X_all[:,j] = boostedJets_normalized[key][:,0]
        # subleading jet
        X_all[:,j+Nvars] = boostedJets_normalized[key][:,1]
    t1 = cput()
    input_array_time = t1 - t0
    
    if Verbose:
        print('Finished filling input arrays!')
        print(' {:6.2f} (s)\n'.format(input_array_time))
    #-------------------------------------------------------------------------#
    
    
    ## 9.0)
    ## DETERMINE SCALE FACTOR
    #-------------------------------------------------------------------------#
    SF = (lumi*XS*kFact*Eff)/sum_of_weights
    if Verbose:
        print('\nComputing SF')
        print('Numerator (lumi*XS*kFact*Eff): {}'.format(lumi*XS*kFact*Eff))
        print('Denominator: {}'.format(sum_of_weights))
    N_mc = X_all.shape[0]
    N_ph = round(SF*N_mc)
    
    ## 9.1)
    ## Scale mc_event_weights by
    mcEventWeight_sel_sc = np.ndarray.copy(
        mc_event_weights[matched_jets[:,0]] * SF)
    
    ## 9.1)
    ## SAVE TRUTH ARRAY AND INPUT
    #-------------------------------------------------------------------------#
    if X_all.shape == 0:
        save_array_time = 0
        if Verbose:
            print('No values in array to save!')
    
    else:
        t0 = cput()
        np.save(dest+array_prefix+'_X', X_all)
        np.save(dest+array_prefix+'_Y', Yn)
        np.save(dest+array_prefix+'_mc', mcEventWeight_sel_sc)
        t1 = cput()
        save_array_time = t1 - t0

        if Verbose:
            print(' {:6.2f} (s)'.format(save_array_time))
    #-------------------------------------------------------------------------#

            
    #==================#
    ## RETURN RESULTS ##
    #==================#
    results_dict = dict()
    time_t = load_time + twojets_cut_time + matched_jets_time + nan_time + \
        normalize_time + truth_var_time + input_array_time + save_array_time
    results_dict['total_time'] = time_t
    results_dict['file'] = full_fpath
    results_dict['status'] = 'completed'
    results_dict['trace'] = None
    results_dict['SF'] = SF
    results_dict['N_mc'] = N_mc
    results_dict['N_ph'] = N_ph
    results_dict['MCN'] = MCN
    results_dict['XS'] = XS
    results_dict['kFact'] = kFact
    results_dict['Eff'] = Eff
    return results_dict


def err_process_NTuples(full_fpath, array_prefix, dest, Verbose=False,
                       MCargs=None):
    ''' Add error handling to process_NTuples '''
    
    results_dict = dict()
    start_time = t.time()
    try:
        t0 = cput()
        if MCargs is None:
            results_dict = process_NTuples(full_fpath, array_prefix, dest, Verbose)
        else:
            results_dict = process_NTuples(full_fpath, array_prefix, dest, Verbose,
                                          MCargs=MCargs)
        results_dict['start_time'] = start_time
        results_dict['end_time'] = t.time()
        
    except Exception as exc:
        t1 = cput()
        
        if not MCargs is None:
            MCN, XS, Eff, kFact = MCargs
        
        results_dict['start_time'] = start_time
        results_dict['total_time'] = t1 - t0
        results_dict['file'] = full_fpath
        results_dict['status'] = 'failed'
        results_dict['trace'] = traceback.format_exc()
        results_dict['SF'] = None
        results_dict['N_mc'] = None
        results_dict['N_ph'] = None
        results_dict['MCN'] = MCN
        results_dict['XS'] = XS
        results_dict['kFact'] = kFact
        results_dict['Eff'] = Eff
        results_dict['end_time'] = t.time()
    
    return results_dict
        
        