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
from ROOT import gStyle
import numpy as np
# cwd = os.getcwd()
# path_head, path_tail = os.path.split(cwd)
# sys.path.append(path_head+'/utils')
from plotting_module import XhhMNT_phys_dict, XhhMNT_pu_branch_dict
from plotting_module import leg_loc_dict

branches = list(XhhMNT_pu_branch_dict.keys())
physics = list(XhhMNT_phys_dict.keys())

def open_rfile(rfilename):
    success = True
    try:
        f = ROOT.TFile.Open(rfilename)
        return f
    except OSError as ose:
        print('Caught OSError: \n{} \n'.format(ose))
        return None

## ARGPARSING ##
parser = argparse.ArgumentParser(
                    prog = 'hist_from_branches',
                    description = 'Creates histograms from the combined root '\
                    'files in the given folder.',
                    epilog = 'This code should be used after all histograms'\
                    +'have been combined.')
parser.add_argument('--verbose', dest='verbose',
                    action='store_true',
                    help='Print relevant information to terminal.')
parser.add_argument('--save_string', dest='save_string',
                    action='store', type=str, default=None,
                    help='Add string tagged at the end of the file.')
parser.add_argument('--rebin', dest='rebin',
                    action='store_true',
                    help='Rebin histograms over the axis range.')

args = parser.parse_args()
Verbose = args.verbose
SaveString = args.save_string
Rebin = args.rebin


## PULL ROOT FILES ##
#------------------------------------------------------------------------------
ls_dir_path = subprocess.run('ls', stdout=subprocess.PIPE)
grep_root = subprocess.run('grep .root'.split(),
    input=ls_dir_path.stdout, stdout=subprocess.PIPE)
file_list_raw = grep_root.stdout.decode('utf-8').split()


# OPEN ROOT FILE DICTIONARY4
rfile_dict = dict()
for file in file_list_raw:
    for phys in physics:
        if phys in file:
            rfile_dict[phys] = open_rfile(file)
            if rfile_dict[phys] is None:
                raise OSError('\nCouldn\'t open file pertaining to {}'.format(phys))       


## MAIN PHYSICS LOOP ##
#------------------------------------------------------------------------------
gStyle.SetLegendTextSize(.03)

# draw hists
for branch in branches:
    
    print('\nOn Branch: {}\n'.format(branch))

    canv = ROOT.TCanvas()
    ll = XhhMNT_pu_branch_dict[branch]['legend_loc']
    leg = ROOT.TLegend(ll[0], ll[1], ll[2], ll[3])

    # draw lines
    th1_phys_dict = dict()
    for phys in physics:
        print('On Physics: {}'.format(phys))
        
        tfile = rfile_dict[phys]
            
        phys_key = tfile.GetKey('{}-{}'.format(phys, branch))
        phys_obj = phys_key.ReadObj()
        th1_phys_dict[phys] = phys_obj.Clone()
        
        if phys_obj.ClassName() != 'TH1D' and phys_obj.ClassName() != 'TH1F':
            raise ValueError('\nExpected only TH1D or TH1F in file!\n'+\
                            'Found: {}\n'.format(phys_obj.ClassName()))
        
        # potentially rebin histograms
        if Rebin:
            nbins = XhhMNT_pu_branch_dict[branch]['nbins']
            xlim = XhhMNT_pu_branch_dict[branch]['xlim']
            bin_edges = np.linspace(xlim[0], xlim[1], num=nbins+1)
            new_phys_obj = phys_obj.Rebin(nbins, "new_phys_obj", bin_edges)
            del phys_obj
            phys_obj = new_phys_obj.Clone()
            del new_phys_obj
            th1_phys_dict[phys] = phys_obj.Clone()
        
        ## Normalize ##
        th1_phys_dict[phys].Scale(1./phys_obj.Integral(), 'width')
        
        ## Set features
        th1_phys_dict[phys].SetLineColor(XhhMNT_phys_dict[phys]['color'])
        th1_phys_dict[phys].SetStats(False)
        
        ## Modify the first th1 in the list and everything else will follow
        # the same style
        if phys == physics[0]:
            
            if Verbose:
                print('{} First in list, setting ranges'.format(phys))
            # x label
            xlabl_tmp = XhhMNT_pu_branch_dict[branch]['xaxislabel']
            th1_phys_dict[phys].GetXaxis().SetTitle(xlabl_tmp)
            
            # title
            title_tmp = XhhMNT_pu_branch_dict[branch]['title']
            th1_phys_dict[phys].SetTitle(title_tmp)
            
            # check for defaults maybe?
            if XhhMNT_pu_branch_dict[branch]['default'] == False:
                
                # X and Y axis range
                xlim = XhhMNT_pu_branch_dict[branch]['xlim']
                ylim = XhhMNT_pu_branch_dict[branch]['ylim']
                
                th1_phys_dict[phys].GetXaxis().SetRangeUser(xlim[0], xlim[1])
                th1_phys_dict[phys].GetYaxis().SetRangeUser(ylim[0], ylim[1])
            
        ## Draw line
        if Verbose:
            print('Drawing with style {}'.format(XhhMNT_phys_dict[phys]['style']))
        th1_phys_dict[phys].Draw(XhhMNT_phys_dict[phys]['style'])
            
        ## Legend
        leg.AddEntry(th1_phys_dict[phys], XhhMNT_phys_dict[phys]['title'])
        
    ## legend
    legend_title = XhhMNT_pu_branch_dict[branch]['legend_title']
    if not legend_title is None:
        leg.SetHeader(legend_title, 'C')
    else:
        leg.SetHeader('')
    # leg.SetTextSize(20)
    leg.Draw()
    
    ## Save Hists
    if SaveString is not None:
        outputstring = 'overlays-{}_{}.png'.format(branch, SaveString)
    else:
        outputstring = 'overlays-{}.png'.format(branch)
    
    canv.SaveAs(outputstring)
    leg.Delete()
    canv.Delete()
    

print('\n.. le fin ..\n')

## Maybe setting the range as a user is not working because the view is outside of the histogram range?
# https://root-forum.cern.ch/t/setrangeuser-doesnt-work-well/14774


