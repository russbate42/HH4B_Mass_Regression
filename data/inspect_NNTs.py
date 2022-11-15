#! /bin/bash
# -*- coding: utf-8 -*-

'''Code to inspect NNTs, produce histograms,
look at MetaData etc.
Author: Russell Bate
russell.bate@cern.ch
russellbate@phas.ubc.ca
'''

import numpy as np
import sys, os, subprocess
import argparse
import matplotlib.pyplot as plt
import ROOT

def open_rfile(rfilename):
    success = True
    try:
        f = ROOT.TFile.Open(rfilename)
        return f
    except OSError as ose:
        print('Caught OSError:\n{}\n'.format(ose))
        return None

def save_hist_from_keys(keys, savepath, save_format='png'):
	nHist = 0
	histname_list = ['TH1F', 'TH2F', 'TH3F', 'TH1C', 'TH2C', 'TH3C',
		'TH1I', 'TH2I', 'TH3I', 'TH1S', 'TH2S', 'TH3S',
		'TH1D', 'TH2D', 'TH3D']

	for key in keys:
		obj = key.ReadObj()

		if obj.ClassName() in histname_list:
			nHist += 1
			c1 = ROOT.TCanvas()
			obj_name = obj.GetName()
			obj.Draw()
			c1.SaveAs(savepath+obj_name+'.{}'.format(save_format))
	return nHist

histname_list = ['TH1F', 'TH2F', 'TH3F', 'TH1C', 'TH2C', 'TH3C',
	'TH1I', 'TH2I', 'TH3I', 'TH1S', 'TH2S', 'TH3S',
	'TH1D', 'TH2D', 'TH3D']

rootfile_prefix = '/fast_scratch_1/atlas_images/XhhNTuple/'
rf_path = rootfile_prefix + 'user.zhenw.29137978._000001.MiniNTuple.root'

rfile = open_rfile(rf_path)

file_keys = rfile.GetListOfKeys()

save_path = 'histograms/'

os.system('mkdir '+save_path)
nHist = 0
for key in file_keys:
    print('\nkey: {}'.format(key))
    obj = key.ReadObj()
    print('obj: {}'.format(obj))
    print('obj type: {}'.format(type(obj)))
    print('obj Classname(): {}'.format(obj.ClassName()))
    print('obj name: {}\n'.format(obj.GetName()))

    if obj.ClassName() in histname_list:
        nHist += 1
        c1 = ROOT.TCanvas()
        obj_name = obj.GetName()
        obj.Draw()
        c1.SaveAs(save_path+obj_name+'.png')

print('Total number of histograms saved: {}'.format(nHist))
