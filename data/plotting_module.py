
##========================================================##
## Helper file for some of the long plotting dictionaries ##
##========================================================##

# For Xhh histogram production
XhhMNT_phys_dict = {
    'nonresonant_vbf_pythia' : {
        'title' : 'Xhh Nonresonant VBF Pythia',
        'color' : 1,
        'style' : 'HIST'
    },
    'resonant_vbf_hh' : {
        'title' : 'Resonant VBF Pythia',
        'color' : 2,
        'style' : 'HISTSAME'
    },
    'dijet_b_filtered_bkgd' : {
        'title' : 'Di-Jet b Filtered Background',
        'color' : 3,
        'style' : 'HISTSAME'
    },
    'dijet_bkgd' : {
        'title' : 'Di-Jet Background',
        'color' : 8,
        'style' : 'HISTSAME'
    },
    'ttbar_ht_filtered_bkgd' : {
        'title' : 'ttbar ht Filtered Background',
        'color' : 4,
        'style' : 'HISTSAME'
    },
    'ttbar_inclusive_bkgd' : {
        'title' : 'ttbar Inclusive Background',
        'color' : 7,
        'style' : 'HISTSAME'
    },
    'vbf_ggf_H_bkgd' : {
        'title' : 'VBF ggF h Background',
        'color' : 6,
        'style' : 'HISTSAME'
    },
    'vbf_h_bkgd' : {
        'title' : 'VBF h Background',
        'color' : 9,
        'style' : 'HISTSAME'
    },
    'vbf_ttH_bkgd' : {
        'title' : 'VBF tth Background',
        'color' : 46,
        'style' : 'HISTSAME'
    },
    'vbf_VH_bkgd' : {
        'title' : 'VBF VH Background',
        'color' : 41,
        'style' : 'HISTSAME'
    }
}

## Legend location dictionary
leg_loc_dict = dict([
    ('upper right', [0.5, 0.55, 0.875, 0.875]),
    ('upper middle', [0.3, 0.6, 0.7, 0.875]),
    ('upper left', [0.15, 0.5, 0.55, 0.875]),
    ('lower middle', [0.35, 0.15, 0.65, 0.45])    
    ])

XhhMNT_pu_branch_dict = {
    'weight_pileup' : {
        'title' : 'Pileup Weight',
        'xlim' : (0., 1.6),
        'ylim' : (0., 9.),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper left'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
    'weight_pileup_up' : {
        'title' : 'Pileup Weight Up',
        'xlim' : (.85, 1.3),
        'ylim' : (0., 18.5),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
	'weight_pileup_down' : {
        'title' : 'Pileup Weight Down',
        'xlim' : (0., 2.75),
        'ylim' : (0., 6.),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
    'correctedAverageMu' : {
        'title' : 'Corrected Average mu',
        'xlim' : (0., 60.),
        'ylim' : (0., .13),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
	'correctedAndScaledAverageMu' : {
        'title' : 'Corrected and Scaled Average mu',
        'xlim' : (0., 60.),
        'ylim' : (0., .13),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
    'correctedActualMu' : {
        'title' : 'Corrected Actual Mu',
        'xlim' : (0., 60.),
        'ylim' : (0., .13),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    },
	'correctedAndScaledActualMu' : {
        'title' : 'Corrected and Scaled Actual Mu',
        'xlim' : (0., 60.),
        'ylim' : (0., .13),
        'nbins' : 100,
        'default' : False,
        'legend_loc' : leg_loc_dict['upper right'],
        'logscale' : False,
        'xaxislabel' : ' ',
        'legend_title' : None
    }
}

