
# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: Atmosphere_Surface                                                 - |
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
from custom_plot_params import dict_plot_params as custom_plot_params
from custom_obs_dict import custom_obs_dict

from itertools import chain

# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd

debug = False 

if debug:
     # -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
    verbose = 'debug'
    # -- Safe Mode (set to False and verbose='debug' if you want to debug)
    safe_mode = False
else:
   # -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
    verbose = 'error'
    # -- Safe Mode (set to False and verbose='debug' if you want to debug)
    safe_mode = True

# -- Set to True to clean the CliMAF cache
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# routine_cache_cleaning = 'figures_only'

# -- Parallel and memory instructions
do_parallel = False
nprocs = 32
# memory = 20 # in gb
# queue = 'days3'
# time = 480 # minutes
# QOS = 'test'

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
#atlas_head_title = "ORCHIDEE Essentials"
## When driven by libIGCM, an additional title may be provided by config.card
#if AtlasTitle != "NONE":
#    atlas_head_title += " - " + AtlasTitle
#else:
#    print("No change to title")
#print("head_title=", atlas_head_title)

# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
#my_seasons = ['ANM', 'DJF', 'JJA']
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'GLOB'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = dict()

# ---------------------------------------------------------------------------- >
# -- diagnostics
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- 
variables_energy_budget = ['hfls', 'hfss']#, 'albnir', 'albvis'] #, 'tas', 'rsds', 'rlds'], 
variables_water_budget = ['evspsbl'] #['es', 'et', 'mrros', 'mrrob', 'snw'], 
variables_carbon_budget = ['lai'] #['cLitter', 'cSoil', 'cVeg', 'lai', 'gpp', 'npp'], 

atlas_explorer_variables_list = [variables_energy_budget, variables_water_budget, variables_carbon_budget]
atlas_explorer_variables = []

for var in chain.from_iterable(atlas_explorer_variables_list):

    settings = dict(variable=var, focus='land', season=season)

    # define project specs 
    if var in variables_energy_budget:
        if var in ['hfls', 'hfss']:
            project_specs = dict(CMIP6=dict(table='Amon'),IGCM_OUT=dict(DIR='ATM'))
        else:
            project_specs = dict(CMIP6=dict(table='Amon'),IGCM_OUT=dict(DIR='SRF'))

    elif var in variables_water_budget: 
        if var in ['evspsbl']:
            project_specs = dict(table='Lmon', IGCM_OUT=dict(DIR='SRF'))
        elif var in ['snw']:
            project_specs = dict(table='LImon')
        elif var in ['mrrob', 'es']:
            project_specs = dict(table='*mon')
        elif var in ['et']:
            project_specs = dict(table='Nonemon')
        else:
            project_specs = dict(table='Lmon')
    else:
        if var in ['lai', 'gpp']:
            #atlas_explorer_variables.append(dict(variable=var, focus='land', season=season, DIR='SBG'))
            project_specs = dict(table='Lmon', IGCM_OUT=dict(DIR='SBG'))
        elif var in ['cSoil']:
            project_specs = dict(table='Emon')
        else:
            project_specs = dict(table='Lmon')

    # construct atlas_explorer_variables dict
    settings['project_specs'] = project_specs
    atlas_explorer_variables.append(settings)

#Aliases for non CMIP names
calias('IGCM_OUT', 'albvis', 'alb_vis', filenameVar='sechiba_history')
calias('IGCM_OUT', 'albnir', 'alb_nir', filenameVar='sechiba_history')
calias("IGCM_OUT", 'tas', 'tair', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rsds', 'swdown', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rlds', 'lwdown', filenameVar='sechiba_history')

calias('IGCM_OUT', 'evsp', 'evspsblveg', filenameVar='sechiba_history')
calias('IGCM_OUT', 'evspsbl', 'evap', filenameVar='sechiba_history')
calias('IGCM_OUT', 'mrros', filenameVar='sechiba_history')
calias('IGCM_OUT', 'mrrob', 'drainage', filenameVar='sechiba_history')
calias('IGCM_OUT', 'snw', 'frac_snow', filenameVar='sechiba_history')

calias('IGCM_OUT', 'cLitter', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'cSoil', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'cVeg', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'npp', filenameVar='stomate_ipcc_history')
#calias('IGCM_OUT', 'gpp', filenameVar='stomate_ipcc_history')
#calias('IGCM_OUT', 'lai', filenameVar='stomate_ipcc_history')

## Add observations to custom_obs_dict
calias('ref_climatos', 'hfls', 'fluxlat')
calias('ref_climatos', 'hfss', 'fluxsens')
calias('obsMAPPER', 'hfls', 'fluxlat')
calias('obsMAPPER', 'hfss', 'fluxsens')
calias('obsMAPPER', 'albnir', 'alb_nir')
calias('obsMAPPER', 'albvis', 'alb_vis')
calias('obsMAPPER', 'evspsbl', 'evap')

ORCH_Essential_obs = {
    'albedo': dict(project='obsMAPPER', variable_mapperName='albedo', product='modis', customname='MODIS (MAPPER)'),
    'albnir': dict(project='obsMAPPER', variable_mapperName='alb_nir', product='modis', customname='MODIS (MAPPER)'),
    'albvis': dict(project='obsMAPPER', variable_mapperName='alb_vis', product='modis', customname='MODIS (MAPPER)'),
    'evspsbl': dict(project='obsMAPPER', variable_mapperName='evap', product='gleam', customname='GLEAM (MAPPER)'),   
    'hfls': dict(project='obsMAPPER', variable_mapperName='fluxlat', product='jung', customname='FLUXCOM (MAPPER)'),    
    'hfss': dict(project='obsMAPPER', variable_mapperName='fluxsens', product='jung', customname='FLUXCOM (MAPPER)'),
    'lai': dict(project='obsMAPPER', variable_mapperName='lai', product='gimms', customname='GIMMS (MAPPER)'),
    #
#    'hfls': dict(project='ref_climatos', product='EnsembleLEcor', frequency='annual_cycle'),
#    'hfss': dict(project='ref_climatos', product='EnsembleHcor', frequency='annual_cycle'),
#    'lai': dict(project='ref_climatos', product='GIMM3G', table='Lmon', frequency='annual_cycle'),
#    'albvis': dict(project='ref_climatos', product='MODIS', table='Lmon', frequency='annual_cycle'),
#    'albnir': dict(project='ref_climatos', product='MODIS', table='Lmon', frequency='annual_cycle'),
#    'gpp': dict(project='ref_climatos', product='EnsembleGPP', frequency='annual_cycle'),
#    'lai': dict(project='ref_climatos', product='GLASS'        , frequency='annual_cycle'),
}

# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'

# -- Activate the parallel execution of the plots
do_parallel = False

period_manager_test_variable = 'hfls'
# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >


# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True


# -- Name of the html file
# -- if index_name is set to None, it will be build as user_comparisonname_season
# -- with comparisonname being the name of the parameter file without 'params_'
# -- (and '.py' of course)
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
