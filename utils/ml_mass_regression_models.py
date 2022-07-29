#!/bin/bash

import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers

## Baseline DNN
def Dumb_Network(num_features, name="dum-dum-net"):
    inputs = keras.Input(shape=(num_features), name='input')
    
    #============== Dumb Layers ==============================================#
    dense_0 = layers.Dense(100, name='dense_0')(inputs)
    activation_0 = layers.Activation('relu', name="activation_0")(dense_0)
    
    dense_1 = layers.Dense(100, name='dense_1')(activation_0)
    activation_1 = layers.Activation('relu', name="activation_1")(dense_1)
    
    dense_2 = layers.Dense(100, name='dense_2')(activation_1)
    activation_2 = layers.Activation('relu', name="activation_2")(dense_2)
    #=========================================================================#
    
    ## Output
    #=========================================================================#
    dense_3 = layers.Dense(2, name='output')(activation_2)
    activation_3 = layers.Activation('linear', name="activation_3")(dense_3)
    #=========================================================================#
    
    return keras.Model(inputs=inputs, outputs=activation_3, name=name)
