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