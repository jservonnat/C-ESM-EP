
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
from climaf.utils import ranges_to_string

# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'debug'
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
time = 240 # minutes
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
atlas_head_title = "INCA - Total Column"


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'Robinson'
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
atlas_explorer_variables_list = ['colo3tot', 'colco', 'colo3', 'colno2', 'colnh3', 'colch2o']

my_title= { 'colo3tot': 'Total Column of O_3',
        'colco':'Column of CO',
        'colo3':'Column of Tropospheric O_3',
        'colno2':'Column of NO_2',
        'colnh3':'Column of NH_3',
        'colch2o':'Column of CH_2O'}

# -- Project Specs
atlas_explorer_variables = []
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas,line_title=my_title[var],
                                             project_specs=dict(
                                                 IGCM_OUT=dict(DIR='CHM'),
                                             ),
                                             ))

calias("IGCM_OUT", 'colo3tot', filenameVar='inca_chem')
calias("IGCM_OUT", 'colnh3',  filenameVar='inca_chem')
calias("IGCM_OUT", 'colno2',  filenameVar='inca_chem')
calias("IGCM_OUT", 'colco',   filenameVar='inca_chem')
calias("IGCM_OUT", 'colo3',   filenameVar='inca_chem')
calias("IGCM_OUT", 'colnh3',  scale=1e-3, filenameVar='inca_chem')
calias("IGCM_OUT", 'colch2o', filenameVar='inca_chem')

my_dict_plot_params = {
        'colo3tot': {'default':{'gsnCenterString':'units: DU','contours': 1, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: DU','colors': ranges_to_string(ranges=[220, 460, 20])},
            'bias': {'colors': ranges_to_string(ranges=[-100, 100, 20], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-10, 100, 20], sym=True)},
                    },
        'colco': {'default':{'gsnCenterString':'units: 1e18 mol/cm2', 'contours': 1, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: 1e18 mol/cm2', 'colors': ranges_to_string(ranges=[0, 4, 0.2])},
            'bias': {'colors': ranges_to_string(ranges=[-1, 1, 0.2], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-1, 1, 0.1], sym=True)},
                    },
        'colo3': {'default':{'gsnCenterString':'units: DU', 'contours': 1, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: DU', 'colors': ranges_to_string(ranges=[0, 55, 5])},
            'bias': {'colors': ranges_to_string(ranges=[-20, 20, 4], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-20, 20, 2], sym=True)},
                    },
        'colno2': {'default':{'gsnCenterString':'units: 1e15 mol/cm2', 'contours': 1, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: 1e15 mol/cm2', 'colors': ranges_to_string(ranges=[0, 30, 2])},
            'bias': {'colors': ranges_to_string(ranges=[-14, 14, 2], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-14, 14, 2], sym=True)},
                    },
        'colnh3': {'default':{'gsnCenterString':'units: 1e15 mol/cm2' },
            #'full_field': {'gsnCenterString':'units: 1e15 mol/cm2', 'colors': ranges_to_string(ranges=[0, 4.25, 0.25]), 'color': 'WhiteBlueGreenYellowRed'},
            #'bias': {'colors': ranges_to_string(ranges=[-20, 20, 1], sym=True), 'color': 'BlueWhiteOrangeRed'},
            #'model_model': {'colors': ranges_to_string(ranges=[-20, 20, 1], sym=True)},
                    },
        'colch2o': {'default':{'gsnLeftString':'units: 1e15 mol/cm2', 'contours': 1, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: 1e15 mol/cm2', 'colors': ranges_to_string(ranges=[0, 34, 2])},
            'bias': {'colors': ranges_to_string(ranges=[-20, 20, 4], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-20, 20, 2], sym=True)},
                    },
        }

# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'

# -- Display full climatology maps =
# -- Use this variable as atlas_explorer_variables to activate the climatology maps
atlas_explorer_climato_variables = False #atlas_explorer_variables
add_line_of_climato_plots=True

period_manager_test_variable = 'emin2o'
# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

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
