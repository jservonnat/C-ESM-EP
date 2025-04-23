
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
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# routine_cache_cleaning = 'figures_only'

# -- Parallel and memory instructions
do_parallel = False
nprocs = 32
# memory = 20 # in gb
# queue = 'days3'
time = 360 # minutes
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
atlas_head_title = "INCA - Atmosphere Upper Troposphere"


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'Robinson' #'GLOB'
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
atlas_explorer_variables_list = ['vmro3_ut', 'vmrnox_ut', 'vmrh2o_ut', 'vmrco_ut']

my_title = {'vmro3_ut':'Volume Mixing Ratio of O3 at 200 hPa',
        'vmrnox_ut':'Volume Mixing Ratio of NOx at 200 hPa',
        'vmrh2o_ut':'Volume Mixing Ratio of H2O at 200 hPa',
        'vmrco_ut':'Volume Mixing Ratio of CO at 200 hPa'}

atlas_explorer_variables = []
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, color='BlueYellowRed',line_title=my_title[var],
                                             project_specs=dict(
                                                 IGCM_OUT=dict(DIR='CHM'),
                                             ),
        ##                                     ))
        ##atlas_explorer_variables.append(dict(variable=var, season=seas
                                             ))

# -- Project Specs
##for var in atlas_explorer_variables:
##    var.update(dict(
##        table='Amon', project_specs=dict(
##            IGCM_OUT=dict(DIR='CHM'),
##        ),
##    ))

calias("IGCM_OUT", 'area', filenameVar='inca_emi')

calias("IGCM_OUT", 'vmrh2o', scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrco',  scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmro3',  scale=1e6, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno2', scale=1e9, filenameVar='inca_species')

# -- Atmospheric Variables on vertical levels
for tmpvar in ['vmrh2o', 'vmrnox', 'vmrco', 'vmro3']:
    derive('*', tmpvar + '_ut', 'ccdo', tmpvar, operator='intlevel,20000')

derive("*", "vmrnox", "plus", "vmrno", "vmrno2")

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
