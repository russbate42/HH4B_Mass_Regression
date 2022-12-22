#!/bin/bash
# -*- coding: utf-8 -*-

'''
Script to create histograms for a given branch of a root file
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca

Notes: 

TO-DO:
'''

import sys, os, argparse, subprocess, ROOT
import numpy as np
# cwd = os.getcwd()
# path_head, path_tail = os.path.split(cwd)
# sys.path.append(path_head+'/utils')
from plotting_module import XhhMNT_phys_dict


def open_rfile(rfilename):
    success = True
    try:
        f = ROOT.TFile.Open(rfilename)
        return f
    except OSError as ose:
        print('Caught OSError: \n{} \n'.format(ose))
        return None


branches = ['weight_pileup', 'correctedAverageMu',
	'correctedAndScaledAverageMu', 'correctedActualMu',
	'correctedAndScaledActualMu', 'weight_pileup_up',
	'weight_pileup_down']
pssbl_key_names = ['XhhMiniNtuple', 'tree']


## ARGPARSING ##
parser = argparse.ArgumentParser(
                    prog = 'hist_from_branches',
                    description = 'Creates histograms from the combined root '\
                    'files in the given folder.',
                    epilog = 'This code should be used after all histograms'\
                    +'have been combined.')
parser.add_argument('folder', # positional argument
                    help='Folder where the combined root files live.')
parser.add_argument('--physics_process', dest='physics_process',
                   action='store', nargs='?', default=None)
parser.add_argument('--list_branches', dest='list_branches', action='store_true',
                    help='Lists branches in either an XhhMiniNTuple or tree.')
parser.add_argument('--list_keys', dest='list_keys',
                    action='store_true',
                    help='Show available keys in first root file given.')
parser.add_argument('--list_files', dest='list_files',
                    action='store_true',
                    help='List all available root files in provided folder.')
parser.add_argument('--verbose', dest='verbose',
                    action='store_true',
                    help='Print relevant information to terminal.')
parser.add_argument('--save_tfile', dest='save_tfile',
                    action='store_true',
                    help='Save histograms to a TFile.')

args = parser.parse_intermixed_args()
rfile_dir = args.folder
Verbose = args.verbose
ListBranches = args.list_branches
ListKeys = args.list_keys
ListFiles = args.list_files
PhysicsProcess = args.physics_process
SaveTFile = args.save_tfile

# make sure root file directory is formatted correctly
if rfile_dir[-1] != '/':
    rfile_dir = rfile_dir+'/'

# check for existence of directory
if not os.path.isdir(rfile_dir):
    raise ValueError('\nDirectory does not exist!\n{}\n'.format(rfile_dir))

if PhysicsProcess is None:
    # we have to do -2 because for some weird reason .split() adds empty
    # values on either end
    PhysicsProcess = rfile_dir.split('/')[-2]


## ROOT FILE CHECKS ##
#------------------------------------------------------------------------------
cmd='ls {}'.format(rfile_dir)
ls_dir_path = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
grep_root = subprocess.run('grep .root'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)
file_list_raw = grep_root.stdout.decode('utf-8').split()

if len(file_list_raw) == 0:
    raise ValueError('No root files found in {}'.format(rfile_dir))

if ListFiles:
    print('\n -- Listing Files --')
    print('-'*40)
    for file in file_list_raw:
        print(file)
    
    print('-'*40)

if ListKeys:
    print('\n -- Printing Keys --')
    print('-'*40)
    RFile = open_rfile(rfile_dir+file_list_raw[0])
    if RFile is not None:
        keys = RFile.GetListOfKeys()
        for key in keys:
            print('  - {}'.format(key))
    else:
        raise OSError('Could not open root file {}'.format(
            rfile_dir+file_list_raw[0]))
    print('-'*40)

if ListBranches:
    print('\n -- Printing Branches --')
    print('-'*40)
    RFile = open_rfile(rfile_dir+file_list_raw[0])
    if RFile is not None:
        keys = RFile.GetListOfKeys()
        if 'XhhMiniNtuple' in RFile.GetListOfKeys():
            XhhMiniNtuple_key = RFile.GetKey('XhhMiniNtuple')
            XhhMiniNtuple = XhhMiniNtuple_key.ReadObj()
        else:
            raise ValueError('\nNo XhhMiniNtuple in file.\n')
        branches = XhhMiniNtuple.GetListOfBranches()
        for branch in branches:
            print('  - {}'.format(branch))
            
    else:
        raise IOError('Could not open root file {}'.format(
            rfile_dir+file_list_raw[0]))
    print('-'*40)


## MAIN HIST ##
#------------------------------------------------------------------------------
## Define some data
branches = ['weight_pileup', 'correctedAverageMu',
	'correctedAndScaledAverageMu', 'correctedActualMu',
	'correctedAndScaledActualMu', 'weight_pileup_up',
	'weight_pileup_down']

# Define dicts
th1_dict = dict()
rf_dict = dict()
entry_tracker = {'weight_pileup' : 0, 'correctedAverageMu' : 0,
	'correctedAndScaledAverageMu' : 0, 'correctedActualMu' : 0,
	'correctedAndScaledActualMu' : 0, 'weight_pileup_up' : 0,
	'weight_pileup_down' : 0}

## Make histograms from first file in list
Test = False
if Test:
    print('\n\nWorking on test file: {}\n'.format(
        rfile_dir+file_list_raw[0]))

    rfile_0 = open_rfile(rfile_dir+file_list_raw[0])
    XhhMiniNtuple_key_0 = rfile_0.GetKey('XhhMiniNtuple')
    XhhMiniNtuple_0 = XhhMiniNtuple_key_0.ReadObj()

    for branch in branches:
        print(' - {}'.format(branch))
        branchMax = XhhMiniNtuple_0.GetMaximum(branch)
        branchMin = XhhMiniNtuple_0.GetMinimum(branch)
        nEntries = XhhMiniNtuple_0.GetEntries(branch)
        print(' - Entries: {}'.format(nEntries))

        th1_dict[branch] = ROOT.TH1D(branch, "", 100, branchMin, branchMax)
        print(' - Created TH1D. Drawing to hist Name: {}'.format(branch))
        XhhMiniNtuple_0.Draw('{}>>{}'.format(branch, branch), '', 'goff')
        print(' - Finished.\n')

    rfile_0.Close()

    
## loop through the remainder of the files and add these
if Verbose:
    print('creating histograms\n')
    
for i, file in enumerate(file_list_raw):
    rf_dict[i] = open_rfile(rfile_dir+file)
    
    if rf_dict[i] is None:
        raise OSError('Cant open file {}'.format(rfile_dir+file))
        
    if Verbose:
        print('\n   ** Working on file:\n{}\n'.format(rfile_dir+file))

    XhhMiniNtuple_key = rf_dict[i].GetKey('XhhMiniNtuple')
    XhhMiniNtuple = XhhMiniNtuple_key.ReadObj()

    for branch in branches:
        nEntries = XhhMiniNtuple.GetEntries(branch)
        entry_tracker[branch] += nEntries
        
        if Verbose:
            print(' - {}'.format(branch))
            print(' - Entries: {}'.format(nEntries))

        if i == 0:
            branchMax = XhhMiniNtuple.GetMaximum(branch)
            branchMin = XhhMiniNtuple.GetMinimum(branch)

            th1_dict[branch] = ROOT.TH1D(branch, "", 100, branchMin, branchMax)
            if Verbose:
                print(' - Created TH1D with name: {}'.format(branch))

        if Verbose:
            print(' - Drawing to hist name: {}\n'.format(branch))
        XhhMiniNtuple.Draw('{}>>{}'.format(branch, branch), '', 'goff')


## Save the hristrograms
if Verbose:
    print('\nSaving histogram images\n')

for branch in branches:
    canv = ROOT.TCanvas()
    th1_dict[branch].Draw('HIST')
    
    # Fancy plotting
    TH1_Title = XhhMNT_phys_dict[PhysicsProcess]['title']
    XAxis_Title = branch
    
    th1_dict[branch].GetXaxis().SetTitle(XAxis_Title)
    th1_dict[branch].SetTitle(TH1_Title)
    
    canv.SaveAs('histograms/{}-{}.png'.format(PhysicsProcess, branch))
    if Verbose:
        print('Entries in {}: {}'.format(branch, entry_tracker[branch]))
        

## save into a TFile
if not SaveTFile:
    sys.exit('\n .. peace ..\n')

if Verbose:
    print('\nSaving histograms to TFile\n')

tfile_str = '{}-pileup_histograms.root'.format(PhysicsProcess)
tfile_hists = ROOT.TFile(tfile_str, 'recreate')

## loop through branches
for branch in branches:
    tfile_hists.WriteObject(th1_dict[branch],
        '{}-{}'.format(PhysicsProcess, branch))

tfile_hists.Close()

if Verbose:
    print('Finished creating root file {}'.format(tfile_str))


sys.exit('\n .. peace ..\n')
