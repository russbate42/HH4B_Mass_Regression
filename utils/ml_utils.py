#!/bin/bash

''' All of our ml utilities can go here.. '''
import numpy as np
import tensorflow as tf
from tensorflow import keras


def DeltaR(coords, ref):
    ''' Straight forward function, expects Nx2 inputs for coords, 1x2 input for ref. '''
    
    DeltaCoords = np.subtract(coords, ref)
    
    ## Mirroring ##
    gt_pi_mask = DeltaCoords > np.pi
    lt_pi_mask = DeltaCoords < - np.pi
    DeltaCoords[lt_pi_mask] = DeltaCoords[lt_pi_mask] + 2*np.pi
    DeltaCoords[gt_pi_mask] = DeltaCoords[gt_pi_mask] - 2*np.pi
    
    rank = DeltaCoords.ndim
    retVal = None
    
    if rank == 1:
        retVal = np.sqrt(DeltaCoords[0]**2 + DeltaCoords[1]**2)
    elif rank == 2:
        retVal = np.sqrt(DeltaCoords[:,0]**2 + DeltaCoords[:,1]**2)
    else:
        raise ValueError('Too many dimensions for DeltaR')
    return retVal


def dict_from_tree(tree, branches=None, np_branches=None):
    ''' Loads branches as default awkward arrays and np_branches as numpy arrays. '''
    dictionary = dict()
    if branches is not None:
        for key in branches:
            branch = tree.arrays(filter_name=key)[key]
            dictionary[key] = branch
            
    if np_branches is not None:
        for np_key in np_branches:
            np_branch = np.ndarray.flatten(tree.arrays(filter_name=np_key)\
                                           [np_key].to_numpy())
            dictionary[np_key] = np_branch
    
    if branches is None and np_branches is None:
        raise ValueError("No branches passed to function.")
        
    return dictionary

def tvt_num(data, tvt=(75, 10, 15)):
    ''' Function designed to output appropriate numbers for traning validation and testing given
    a variable length input. TVT expressed as ratios and do not need to add to 100. '''
    tot = len(data)
    train, val, test = tvt
    tvt_sum = train + val + test
    
    train_rtrn = round(train*tot/tvt_sum)
    val_rtrn = round(val*tot/tvt_sum)
    test_rtrn = tot - train_rtrn - val_rtrn
    
    return train_rtrn, val_rtrn, test_rtrn

def round_to_sigfigs(value, sigfig=3):
    ''' Function to round to significant figures.  '''
    # isntantiate array with same dimensions, return zero where values
    # are zero!
    value = np.array(value)
    returnval = np.zeros(value.shape)
    
    # only do operations on nonzero as we deal with log
    nz_bool = value != 0.0
    exp = np.floor(np.log10(np.abs(value[nz_bool]))).astype(int)
    mantissa = value[nz_bool]/10.0**exp
    new_mantissa = np.round(mantissa, decimals=sigfig-1)

    # return the mantissa back to the appropriate exponential
    returnval[nz_bool] = np.multiply(new_mantissa, 10.0**exp)
    return returnval
