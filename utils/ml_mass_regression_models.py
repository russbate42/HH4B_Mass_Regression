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


## Baseline DNN
def DNN_wDropout(num_features, name="dnn_Wdropout", dr_frac=0.1):
    if dr_frac < 0 or dr_frac >=1:
        raise ValueError('Unacceptable dropout fraction passed to model.')

    inputs = keras.Input(shape=(num_features), name='input')
    
    #============== Dumb Layers ==============================================#
    dense_0 = layers.Dense(100, name='dense_0')(inputs)
    activation_0 = layers.Activation('relu', name="activation_0")(dense_0)
    dropout_0 = layers.Dropout(rate=dr_frac, name='dropout_0')(activation_0)
    
    dense_1 = layers.Dense(100, name='dense_1')(dropout_0)
    activation_1 = layers.Activation('relu', name="activation_1")(dense_1)
    dropout_1 = layers.Dropout(rate=dr_frac, name='dropout_1')(activation_1)
    
    dense_2 = layers.Dense(100, name='dense_2')(dropout_1)
    activation_2 = layers.Activation('relu', name="activation_2")(dense_2)
    dropout_2 = layers.Dropout(rate=dr_frac, name='dropout_2')(activation_2)
    #=========================================================================#
    
    ## Output
    #=========================================================================#
    dense_3 = layers.Dense(2, name='output')(dropout_2)
    activation_3 = layers.Activation('linear', name="activation_3")(dense_3)
    #=========================================================================#
    
    return keras.Model(inputs=inputs, outputs=activation_3, name=name)

## Baseline DNN
def Split_Network(num_features, name="Split_Net"):
    ''' This model is designed to take the inputs stacked in such a way that
    the features of the second jet start at N/2'''
    
    if num_features % 2 != 0:
        raise ValueError('num features must me an even number')
    else:
        nFeatures_perJet = int(num_features / 2)
    input1 = keras.Input(shape=(nFeatures_perJet), name='Leading Jet Input')
    input2 = keras.Input(shape=(nFeatures_perJet), name='Subleading Jet Input')
    
    
    #============== Leading Jet ==============================================#
    dense_L0 = layers.Dense(100, name='dense_L0')(input1)
    activation_L0 = layers.Activation('relu', name="activation_L0")(dense_L0)
    
    dense_L1 = layers.Dense(100, name='dense_L1')(activation_L0)
    activation_L1 = layers.Activation('relu', name="activation_L1")(dense_L1)
    
    dense_L2 = layers.Dense(100, name='dense_L2')(activation_L1)
    activation_L2 = layers.Activation('relu', name="activation_L2")(dense_L2)
    #=========================================================================#
    
    
    #============== Subleading Jet ===========================================#
    dense_SL0 = layers.Dense(100, name='dense_SL0')(input2)
    activation_SL0 = layers.Activation('relu', name="activation_SL0")(dense_SL0)
    
    dense_SL1 = layers.Dense(100, name='dense_SL1')(activation_L0)
    activation_SL1 = layers.Activation('relu', name="activation_SL1")(dense_SL1)
    
    dense_SL2 = layers.Dense(100, name='dense_SL2')(activation_L1)
    activation_SL2 = layers.Activation('relu', name="activation_SL2")(dense_SL2)
    #=========================================================================#
    
    
    #============== Mixture ===========================================#
    concatted = layers.Concatenate()([activation_L2, activation_SL2])
    dense_0 = layers.Dense(100, name='dense_0')(concatted)
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
    
    return keras.Model(inputs=[input1, input2], outputs=activation_3, name=name)
