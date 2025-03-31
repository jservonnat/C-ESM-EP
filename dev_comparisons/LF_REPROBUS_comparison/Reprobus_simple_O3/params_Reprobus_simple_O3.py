#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: AtlasExplorer                                                 - |
# --                                                                                             - |
# --      Developed within the ANR Convergence Project                                           - |
# --      CNRM GAME, IPSL, CERFACS                                                               - |
# --      Contributions from CNRM, LMD, LSCE, NEMO Group, ORCHIDEE team.                         - |
# --      Based on CliMAF: WP5 ANR Convergence, S. Senesi (CNRM) and J. Servonnat (LSCE - IPSL)  - |
# --                                                                                             - |
# --      J. Servonnat, S. Senesi, L. Vignon, MP. Moine, O. Marti, E. Sanchez, F. Hourdin,       - |
# --      I. Musat, M. Chevallier, J. Mignot, M. Van Coppenolle, J. Deshayes, R. Msadek,         - |
# --      P. Peylin, N. Vuichard, J. Ghattas, F. Maignan, A. Ducharne, P. Cadule,                - |
# --      P. Brockmann, C. Rousset                                                               - |
# --                                                                                             - |
# --      Contact: jerome.servonnat@lsce.ipsl.fr                                                 - |
# --                                                                                             - |
# --                                                                                            - /
# --                                                                                           - /
# --------------------------------------------------------------------------------------------- /

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division

from climaf.api import *
###from custom_plot_params import dict_plot_params as custom_plot_params
###from custom_obs_dict import custom_obs_dict

# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
###from os import getcwd
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'warning'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to True to clean the CliMAF cache
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False
# nprocs = 32
# memory = 20 # in gb
# -- Job header parameters 
queue = 'xlarge'
time = 15 # minutes
QOS = 'test'


thumbnail_size = "340*300"

# -- Set the reference against which we plot the diagnostics
# -- If you set it in the parameter file, it will overrule
# -- the reference set in datasets_setup.py
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
# reference = 'default'


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Reprobus simple O3"


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'GLOB'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
domain = dict()


# ---------------------------------------------------------------------------- >
# -- Atlas Explorer diagnostics
# -- Atlas Explorer is meant to be a simple and flexible way to produce an atlas
# -- on demand.
# -- atlas_explorer_variables is a list of variables, and/or python dictionaries
# -- that allow to pass custom specifs with the variable, like:
# --   - season
# --   - region
# --   - domain
# --   - and various plot parameters taken as argument by plot() (CliMAF operator)
# ---------------------------------------------------------------------------- >
do_my_own_diag = True


atmos_variable_dict = {'Oxygene': ['O3']}


# no_post_proc = True  # pas nécessaire pour test simple
with_obs = True       # only set for simple test

# Pour subdiviser la période en plusieurs slices de 10 ans 
# Code à améliorer
atmos_period = [models[-1]['clim_period']]
if '-' in atmos_period[0]:
    atmos_period_min_max = atmos_period[0].split('-')
elif '_' in atmos_period[0]:
    atmos_period_min_max = atmos_period[0].split('_')
atmos_period_min = int(atmos_period_min_max[0])
atmos_period_max = int(atmos_period_min_max[1])
print(atmos_period_min_max, atmos_period_min, atmos_period_max)

atmos_periods = []
a_min = atmos_period_min
a_diff = a_min+9
while a_diff<=atmos_period_max:
    atmos_periods.append('{}-{}'.format(a_min, a_diff))
    a_min = a_min+10
    a_diff = a_min+9
else:
    atmos_periods.append('{}-{}'.format(a_min, atmos_period_max))


# Choix des saisons et des mois à calculer
#atmos_seasons = ['DJF', 'MAM', 'JJA', 'SON']
atmos_seasons = ['DJF']

#atmos_months = range(1, 13)
atmos_months = range(1,2)


# Ajout des variables dans atlas_explorer_variables
atlas_explorer_variables = []
for fam in atmos_variable_dict.values():
    for var in fam:
        print("VARIABLE")
        print(var)
        calias('IGCM_OUT',var,filenameVar='reprobus_speciesm')
        atlas_explorer_variables.append(dict(variable=var,
                                             project_specs=dict(
                                                 IGCM_OUT=dict(DIR='CHM'),
                                                 ),
                                             ))



# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
#regridding = 'model_on_ref' # 'ref_on_model', 'no_regridding'

# atlas_explorer_variables = ['tas','pr',
#                            'tos','sos',
#                            dict(variable='ua', season='DJF', add_climato_contours=True),
#                            dict(variable='ua', season='JJA', add_climato_contours=True),
#                            dict(variable='tos',domain=dict(lonmin=-80,lonmax=40,latmin=10,latmax=85)),
#                            dict(variable='sic', proj='NH50', season='March'),
#                            dict(variable='lai', season='MAM'),
#                           ]

# -- Activate the parallel execution of the plots
do_parallel = False

period_manager_test_variable = 'tas'

# -- Display full climatology maps =
# -- Use this variable as atlas_explorer_variables to activate the climatology maps
atlas_explorer_climato_variables = None

# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True


# -- Name of the html file
# -- if index_name is set to None, it will be build as atlas_component_comparison.html
# ---------------------------------------------------------------------------- >
index_name = None


# -- Custom plot params
# -- Changing the plot parameters of the plots
# ---------------------------------------------------------------------------- >
# Load an auxilliary file custom_plot_params (from the working directory)
# of plot params (like atmos_plot_params.py)
# -> Check $CLIMAF/climaf/plot/atmos_plot_params.py or ocean_plot_params.py
#    for an example/


# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #

