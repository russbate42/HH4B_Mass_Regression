#!/bin/bash

import numpy as np
import ROOT

data_prefix = "/fast_scratch_1/atlas_images/XhhNTuple/"
bigfile = "user.zhenw.29137978._000001.MiniNTuple.root"

df1 = ROOT.RDataFrame('XhhMiniNtuple', data_prefix+bigfile)

total_nevents = df1.Count().GetValue()
print(total_nevents)

nFiles = np.floor(822/50).astype(int)
n_in_file = np.floor(total_nevents / nFiles).astype(int)

print('Number of files: {}'.format(nFiles))
print('Number of events in a file of ~50 MB: {}'.format(n_in_file))
print()
print('weoooooo'); print()

df2 = ROOT.RDataFrame('XhhMiniNtuple', data_prefix+'smaller.root')

columns = df1.GetColumnNames()
print(type(columns))
for entry in columns:
    print(entry)
    
    