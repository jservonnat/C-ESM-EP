
# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: Atmospheric_Chemistry                                              - |
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

from custom_plot_params import dict_plot_params as custom_plot_params
from climaf.operators_derive import derive

# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'debug'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = False
# -- Set to True to clean the CliMAF cache
clean_cache = True
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# routine_cache_cleaning = 'figures_only'

# -- Parallel and memory instructions
do_parallel = False
nprocs = 32
# memory = 20 # in gb
# queue = 'days3'
time = 600 # minutes
# QOS = 'test'


# -- Set the reference against which we plot the diagnostics
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
#reference = 'default'

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "INCA - Atmosphere Surface"


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'GLOB'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = {}


# ---------------------------------------------------------------------------- >
# -- Atmosphere diagnostics
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
my_seasons = ['ANM']
#atlas_explorer_variables_list = ['vmro3_surf', 'vmrch4_surf', 'vmrnox_surf', 'vmrnh3_surf', 'vmrh2_surf', 'vmrco_surf', 'vmrn2o_surf',
#        'emi_n2o', 'emi_ch4', 'emi_nox', 'emi_co', 'emi_h2', 'emi_nh3',
#        'dep_nh3', 'dep_noy', 'dep_h2']

atlas_explorer_variables_list = ['vmro3_surf', 'vmrch4_surf', 'vmrnox_surf', 'vmrnh3_surf', 'vmrh2_surf', 'vmrco_surf', 'vmrn2o_surf']
atlas_explorer_variables = []
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, proj='GLOB',color='BlueWhiteOrangeRed',
                                             project_specs=dict(IGCM_OUT=dict(DIR='CHM'),),
                                             ))

atlas_explorer_variables_list = ['emi_n2o', 'emi_ch4', 'emi_nox', 'emi_co', 'emi_h2', 'emi_nh3',
        'dep_nh3', 'dep_noy', 'dep_h2']
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, proj='Robinson', color='GMT_drywet',
                                             project_specs=dict(IGCM_OUT=dict(DIR='CHM'),),
                                             ))

# -- Project Specs
##for var in atlas_explorer_variables:
##    var.update(dict(
##        table='Amon', project_specs=dict(
##            IGCM_OUT=dict(DIR='CHM'),
##        ),
##    ))

calias("IGCM_OUT", 'area', filenameVar='inca_emi')
calias("IGCM_OUT", 'emin2o', scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emich4', scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emico',  scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emino',  scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emino2', scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emih2',  scale=1e3, filenameVar='inca_emi') 
calias("IGCM_OUT", 'eminh3', scale=1e3, filenameVar='inca_emi') 

derive("*", "eminox", "plus", "emino", "emino2")

derive('*', 'emi_n2o', 'multiply', 'emin2o', 'area')
derive('*', 'emi_ch4', 'multiply', 'emich4', 'area')
derive('*', 'emi_co',  'multiply', 'emico',  'area')
derive('*', 'emi_nox', 'multiply', 'eminox', 'area')
derive('*', 'emi_h2',  'multiply', 'emih2',  'area')
derive('*', 'emi_nh3', 'multiply', 'eminh3', 'area')

calias("IGCM_OUT", 'vmrch4', scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrn2o', scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrco',  scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmro3',  scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrnh3', scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrh2',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno2', scale=1e9, filenameVar='inca_species')

# -- Atmospheric Variables on vertical levels
for tmpvar in ['vmrh2', 'vmrch4', 'vmrn2o', 'vmrnh3', 'vmrno', 'vmrno2', 'vmrco', 'vmro3']:
    derive('*', tmpvar + '_surf', 'ccdo', tmpvar, operator='sellevidx,1')

derive('*', 'vmrnox_surf', 'plus', 'vmrno_surf', 'vmrno2_surf')

calias("IGCM_OUT", 'drynh3', scale=1e3, filenameVar='inca_dep')
calias("IGCM_OUT", 'drynoyN',scale=1e3, filenameVar='inca_dep')
calias("IGCM_OUT", 'dryh2',  scale=1e3, filenameVar='inca_dep')

derive('*', 'dep_nh3', 'multiply', 'drynh3', 'area')
derive('*', 'dep_noy', 'multiply', 'drynoyN', 'area')
derive('*', 'dep_h2',  'multiply', 'dryh2',  'area')


# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'

# -- Display full climatology maps =
# -- Use this variable as atlas_explorer_variables to activate the climatology maps
atlas_explorer_climato_variables = atlas_explorer_variables

# -- Activate the parallel execution of the plots
do_parallel = False

period_manager_test_variable = 'emin2o'
# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

#klaurent
#thumbnail_size = "250*250"

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
