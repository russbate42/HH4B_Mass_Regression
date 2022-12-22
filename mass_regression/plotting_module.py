
import numpy as np

## This list is for all the raw input variables
plot_dict_list = []
num_bin_edges = 30
plot_dict_list.append( # mass
    {'bins' : np.linspace(20,160,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # pt
    {'bins' : np.linspace(100,2000,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # phi
    {'bins' : np.linspace(-np.pi,np.pi,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # eta
    {'bins' : np.linspace(-2.2,2.2,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # Split12
    {'bins' : np.linspace(0,200,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # Split23
    {'bins' : np.linspace(0,50,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # Split34
    {'bins' : np.arange(-1000.5,-996.5,1),
        'semilogy' : False})
plot_dict_list.append( # tau1_wta
    {'bins' : np.linspace(0,.6,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # tau2_wta
    {'bins' : np.linspace(0,.25,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # tau3_wta
    {'bins' : np.linspace(0,.15,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # tau21_wta
    {'bins' : np.linspace(0,1.0,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # tau32_wta
    {'bins' : np.linspace(0,1.0,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # ECF_1
    {'bins' : np.linspace(200,3500,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_dict_list.append( # ECF_2
    {'bins' : np.linspace(1.0e7,7.5e8,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_dict_list.append( # ECF_3
    {'bins' : np.linspace(1.0e12,5.0e13,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_dict_list.append( # C2
    {'bins' : np.linspace(0,.4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # D2
    {'bins' : np.linspace(0,6,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_dict_list.append( # NTrimSubjets
    {'bins' : np.arange(-.5,6.5,1),
        'semilogy' : False})
plot_dict_list.append( # NClusters
    {'bins' : np.arange(-1000.5,-996.5,1),
        'semilogy' : False})
plot_dict_list.append( # Ntracks
    {'bins' : np.arange(-.5,80.5,1),
        'semilogy' : False})
plot_dict_list.append( # ungrtrk500
    {'bins' : np.arange(-.5,60.5,1),
        'semilogy' : False})
plot_dict_list.append( # EMFrac
    {'bins' : np.arange(-2.5,2.5,1),
        'semilogy' : False})
plot_dict_list.append( # nChargedParticles
    {'bins' : np.arange(-1000.5,-996.5,1),
        'semilogy' : False})
plot_dict_list.append( # numConstituents
    {'bins' : np.arange(-.5,60.5,1),
        'semilogy' : False})


## This is for the normalized variables
num_bin_edges=50
plot_norm_list = []

plot_norm_list.append( # mass
    {'bins' : np.linspace(-4,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # pt
    {'bins' : np.linspace(-1.5,6,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # phi
    {'bins' : np.linspace(-np.pi/2,np.pi/2,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # eta
    {'bins' : np.linspace(-2.5,2.5,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # Split12
    {'bins' : np.linspace(-3,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # Split23
    {'bins' : np.linspace(-2,4.5,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # tau1_wta
    {'bins' : np.linspace(-2,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # tau2_wta
    {'bins' : np.linspace(-2,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # tau3_wta
    {'bins' : np.linspace(-2,5,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # tau21_wta
    {'bins' : np.linspace(-2.5,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # tau32_wta
    {'bins' : np.linspace(-4.5,2,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # ECF_1
    {'bins' : np.linspace(-2,4,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_norm_list.append( # ECF_2
    {'bins' : np.linspace(-4,4,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_norm_list.append( # ECF_3
    {'bins' : np.linspace(-4,4,num=num_bin_edges, endpoint=True),
        'semilogy' : True})
plot_norm_list.append( # C2
    {'bins' : np.linspace(-2.5,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # D2
    {'bins' : np.linspace(-1.25,2.5,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # NTrimSubjets
    {'bins' : np.arange(-3.5,5.5,1),
        'semilogy' : False})
plot_norm_list.append( # Ntracks
    {'bins' : np.linspace(-2.5,5,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # ungrtrk500
    {'bins' : np.linspace(-2.5,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})
plot_norm_list.append( # numConstituents
    {'bins' : np.linspace(-2.5,4,num=num_bin_edges, endpoint=True),
        'semilogy' : False})




