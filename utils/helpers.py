#!/bin/bash
# -*- coding: utf-8 -*-

'''
Helper functions and extra data for the mass regression that does not belong to
plotting or ML related tools.
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca
'''

## After inspecting the variables these are the variables which we want to log scale
log_vars = ['boostedJets_ECF1', 'boostedJets_ECF2', 'boostedJets_ECF3']

truthJet_vars = ['truth_mHH', 'truthjet_antikt10_pt', 'truthjet_antikt10_eta',
           'truthjet_antikt10_phi', 'truthjet_antikt10_m']

boostedJets_keys = ['boostedJets_m', 'boostedJets_pt', 'boostedJets_phi',
    'boostedJets_eta', 'boostedJets_Split12', 'boostedJets_Split23',
    'boostedJets_tau1_wta', 'boostedJets_tau2_wta', 'boostedJets_tau3_wta',
    'boostedJets_tau21_wta', 'boostedJets_tau32_wta', 'boostedJets_ECF1',
    'boostedJets_ECF2', 'boostedJets_ECF3', 'boostedJets_C2',
    'boostedJets_D2', 'boostedJets_NTrimSubjets', 'boostedJets_nTracks',
    'boostedJets_ungrtrk500', 'boostedJets_numConstituents']

## These are produced in the notebook Mass_Regression_New.ipynb
boostedJets_mean_std_dict = {
    'boostedJets_m' : [110.5, 27.06],
    'boostedJets_pt' : [587.8, 267.7],
    'boostedJets_phi' : [0.0, 1.813],
    'boostedJets_eta' : [0.0, 0.8431],
    'boostedJets_Split12' : [61.93, 27.15],
    'boostedJets_Split23' : [12.15, 8.905],
    'boostedJets_tau1_wta' : [.1601, 8.122e-2],
    'boostedJets_tau2_wta' : [4.805e-2, 3.098e-2],
    'boostedJets_tau3_wta' : [3.055e-2, 1.959e-2],
    'boostedJets_tau21_wta' : [3.221e-1, 1.528e-1],
    'boostedJets_tau32_wta' : [6.322e-1, 1.451e-1],
    'boostedJets_ECF1' : [6.260, 4.069e-1],
    'boostedJets_ECF2' : [17.10, 5.691e-1],
    'boostedJets_ECF3' : [25.74, 9.006e-1],
    'boostedJets_C2' : [1.247e-1, 5.655e-2],
    'boostedJets_D2' : [1.301, 1.220],
    'boostedJets_NTrimSubjets' : [2, 1],
    'boostedJets_nTracks' : [34, 10],
    'boostedJets_ungrtrk500' : [26, 10],
    'boostedJets_numConstituents' : [18.62, 7.585]
}

