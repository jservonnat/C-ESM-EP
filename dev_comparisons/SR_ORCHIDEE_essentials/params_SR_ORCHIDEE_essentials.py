
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
   verbose = 'error'
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

# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'GLOB'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = dict()

# ---------------------------------------------------------------------------- >
## ACCEPTED VARIABLES 
## ratios for water and carbon budgets are excluded ('ratio_ie', 'ratio_te'; 'ratio_ng', resp.)
energy_budget = ['hfls', 'hfss', 'albedo_glob', 'albedo', 'albvis', 'albnir', 'rsds', 'rlds', 'ts']
water_budget = ['mrso', 'humrel', 'transpir', 'inter', 'evspsbl', 'es', 'snow', 'twbr']
carbon_budget = ['lai', 'LAI_MEAN_GS', 'gpp', 'gpp_srf', 'gpp_ipcc', 'npp', 'nbp', 'ra', 'rh', 'fLuc', 'fHarvest', 'fWoodharvest', 'cSoil', 'cVeg', 'cProduct']

## Aliases for ORCHIDEE/C-ESM-EP(CMIP) names
aliases_dict = {'fluxlat':'hfls', 'fluxsens':'hfss', 'alb_vis':'albvis', 'alb_nir':'albnir',
                'swnet':'rss', 'swdown':'rsds', 'lwdown':'rlds',
                'temp_sol':'ts',                 
                #humrel:?, #inter:? 'tran':'transpir'?, 
                'evap':'evspsbl', 'evapnu':'es', #snow:frac_snow?
               } 

for orchidee_alias, cesmep_alias in aliases_dict.items():
    calias('IGCM_OUT', cesmep_alias, orchidee_alias)
    calias('obsMAPPER', cesmep_alias, orchidee_alias)

## DERIVED VARIABLES (partially taken from Stephane's scripts)
calias('IGCM_OUT', 'maxvegetfrac', filenameVar='sechiba_history')
calias('IGCM_OUT', 'read_lai', filenameVar='sechiba_history')
derive("IGCM_OUT", "lai", "ccdo2", "read_lai", "maxvegetfrac", operator="vertsum -mul")

cscript("compute_total_albedo", "cdo mulc,-1. -subc,1 -div ${in_1} ${in_2} ${out}", _var="albedo")
derive("IGCM_OUT", 'albedo', 'compute_total_albedo', 'rss', 'rsds')

cscript("compute_mean_albedo", "cdo mulc,0.5 -add ${in_1} ${in_2} ${out}", _var="albedo_glob")
derive("IGCM_OUT", 'albedo_glob', 'compute_mean_albedo', 'albvis', 'albnir')

## FIX FOR ALBEDO_GLOB REFERENCE
albvis_mapper = ds(project='obsMAPPER', variable='albvis', product='modis')
albnir_mapper = ds(project='obsMAPPER', variable='albnir', product='modis')
cscript("compute_mean_albedo_mapper", "cdo mulc,0.5 -add, -chname,albvis,albedo_glob  ${in_1} ${in_2} ${out}")
albedo_glob = compute_mean_albedo_mapper(albvis_mapper, albnir_mapper)

cproject('derived_obs', ('frequency', 'annual_cycle'), 'product', separator='%')
dataloc(project='derived_obs', organization='generic', url=cfile(albedo_glob))
cdef('variable', '*', project='derived_obs')
cdef('product', '*', project='derived_obs')
cdef('period'      , '1980-2005'    , project='derived_obs')

## OBSERVATIONS
ORCH_Essentials_obs = { 
    'albedo': dict(project='obsMAPPER', product='modis', customname='MODIS (from MAPPER)'),
    'albnir': dict(project='obsMAPPER', product='modis', customname='MODIS (from MAPPER)'),
    'albvis': dict(project='obsMAPPER', product='modis', customname='MODIS (from MAPPER)'),
    'albedo_glob': dict(project='derived_obs', product='modis', customname='MODIS (from MAPPER)'),
    'evspsbl': dict(project='obsMAPPER', product='gleam', customname='GLEAM 3.3b (from MAPPER)'),   
    'hfls': dict(project='obsMAPPER', product='jung', customname='MTE (from MAPPER)'),    
    'hfss': dict(project='obsMAPPER', product='jung', customname='MTE (from MAPPER)'),
    'lai': dict(project='obsMAPPER', product='gimms', customname='GIMMS LAI3g (from MAPPER)'),
}

# ---------------------------------------------------------------------------- >
# -- VARIABLE CESMEP PARAMETERS
# ---------------------------------------------------------------------------- 
variables_list = ['hfls', 'hfss', 'albedo_glob', 'evspsbl', 'lai'] 
atlas_explorer_variables = []

for var in variables_list:
    
    ## set variable name to CMIP (if exists)
    var_name = aliases_dict[var] if var in aliases_dict else var
 
    if (var_name in energy_budget) or (var_name in water_budget) or (var_name in carbon_budget):
        ## define project specs 
        settings = dict(variable=var_name, focus='land', season=season)
        project_specs = {}
    
        ## set dir
        if (var_name in energy_budget) or (var_name in water_budget): 
            project_specs = dict(IGCM_OUT=dict(DIR='SRF'))
    
            if var_name == 'albedo':
                project_specs['IGCM_OUT']['OUT'] = 'Output'
                settings['line_title'] = f'Total Albedo ({var_name}) ; season = {season}'

            if var_name == 'albedo_glob': 
                settings['line_title'] = f'Mean Albedo ({var_name}) ; season = {season}'

            if var_name == 'evspsbl':
                settings['line_title'] = f'Evapotranspiration ({var_name}) ; season = {season}'
        else:
            project_specs = dict(IGCM_OUT=dict(DIR='SBG'))
        
        #used when testing my own python cscript, needs to be checked
        #atlas_explorer_variables.a#ppend(dict(variable=var, focus='land', season=season, DIR='SBG'))
                                   #
        # construct atlas_explorer_variables dict
        settings['project_specs'] = project_specs
        atlas_explorer_variables.append(settings)

        ## add obs from ref_climatos
        if not (var_name in ORCH_Essentials_obs):
            var_ref_climatos = variable2reference(var_name, project='ref_climatos')
            
            if not (var_ref_climatos is None): 
                ORCH_Essentials_obs[var_name] = var_ref_climatos

# ---------------------------------------------------------------------------- >
# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'

# -- Activate the parallel execution of the plots
do_parallel = False

period_manager_test_variable = 'hfls'

# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True

# -- Name of the html file
# -- if index_name is set to None, it will be build as user_comparisonname_season
# -- with comparisonname being the name of the parameter file without 'params_'
# -- (and '.py' of course)
# ---------------------------------------------------------------------------- >
index_name = None

# ---------------------------------------------------------------------------------------- #
# -- END -- #
# ---------------------------------------------------------------------------------------- #
