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


# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd
from custom_plot_params import dict_plot_params as custom_plot_params
from climaf.utils import ranges_to_string

# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'error'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = False
# -- Set to True to clean the CliMAF cache
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False
nprocs = 4
# memory = 30 # in gb; 30 for ocean atlasas
# queue = 'days3' # onCiclad: h12, days3
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
# reference = 'default'


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "INCA - South Pole"
# With libIGCM, the user may have provided an additional title
if AtlasTitle != "NONE":
    atlas_head_title += " - " + AtlasTitle


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'SH50'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = {}

# ---------------------------------------------------------------------------- >
# -- Atmosphere diagnostics
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
my_seasons = ['SON', 'October']
atlas_explorer_variables_list = ['colo3tot', 'vmro3_south', 'vmrhno3_south', 'vmrclo_south', 'vmrhcl_south', 'vmrclono2_south']

period_manager_test_variable = 'tas'

my_title = {'colo3tot':'Total Column of O3',
        'vmro3_south': 'Volume Mixing Ratio of O3 at 200 hPa',
        'vmrhno3_south':'Volume Mixing Ratio of HNO_3 at 200 hPa',
        'vmrclo_south':'Volume Mixing Ratio of ClO at 200 hPa',
        'vmrhcl_south':'Volume Mixing Ratio of HCl at 200 hPa',
        'vmrclono2_south':'Volume Mixing Ratio of ClONO_2 at 200 hPa'}

atlas_explorer_variables = []
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, color='WhiteBlueGreenYellowRed',line_title=my_title[var],
                                             project_specs=dict(
                                                 IGCM_OUT=dict(DIR='CHM'),
                                             ),
                                             ))


my_dict_plot_params = {
        'colo3tot': {'default':{'gsnCenterString':'DU', 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: DU', 'colors': ranges_to_string(ranges=[220, 460, 20])},
            'bias': {'colors': ranges_to_string(ranges=[-100, 100, 20], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-10, 100, 20], sym=True)},
                    },
        'vmro3_south': {'default':{'gsnCenterString':'ppbv', 'scale':1e9, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: ppbv', 'colors': ranges_to_string(ranges=[0, 700, 25])},
            'bias': {'colors': ranges_to_string(ranges=[-0.25, 0.25, 0.02], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-0.25, 0.25, 0.02], sym=True)},
                    },
        'vmrhno3_south': {'default':{'gsnCenterString':'ppbv', 'scale':1e9, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: ppbv', 'colors': ranges_to_string(ranges=[0, 2.2, 0.2])},
            'bias': {'colors': ranges_to_string(ranges=[-0.5, 0.5, 0.05], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-0.5, 0.5, 0.05], sym=True)},
                    },
        'vmrclo_south': {'default':{'gsnCenterString':'pptv', 'scale':1e12, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: pptv', 'colors': ranges_to_string(ranges=[0, 15, 1])},
            'bias': {'colors': ranges_to_string(ranges=[-7, 3, 0.5], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-7, 3, 0.5], sym=True)},
                    },
        'vmrhcl_south': {'default':{'gsnCenterString':'ppbv', 'scale':1e9, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: ppbv', 'colors': ranges_to_string(ranges=[0, 0.24, 0.02])},
            'bias': {'colors': ranges_to_string(ranges=[-0.12, 0.12, 0.01], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-0.12, 0.12, 0.01], sym=True)},
                    },
        'vmrclono2_south': {'default':{'gsnCenterString':'pptv', 'scale':1e12, 'color': 'WhiteBlueGreenYellowRed'},
            'full_field': {'gsnCenterString':'units: pptv', 'colors': ranges_to_string(ranges=[0, 70, 10])},
            'bias': {'colors': ranges_to_string(ranges=[-40, 40, 4], sym=True), 'color': 'BlueWhiteOrangeRed'},
            'model_model': {'colors': ranges_to_string(ranges=[-40, 40, 4], sym=True)},
                    },
        }

calias("IGCM_OUT", 'colo3tot', filenameVar='inca_chem')
calias("IGCM_OUT", 'vmro3',     filenameVar='inca_species')
calias("IGCM_OUT", 'vmrhno3',   filenameVar='inca_species')
calias("IGCM_OUT", 'vmrhcl',    filenameVar='inca_species')
calias("IGCM_OUT", 'vmrclono2', filenameVar='inca_species')
calias("IGCM_OUT", 'vmrclo',    filenameVar='inca_species')

for tmpvar in ['vmrhcl', 'vmrclo', 'vmro3', 'vmrclono2', 'vmrhno3']:
    derive('*', tmpvar + '_south', 'ccdo', tmpvar, operator='intlevel,20000')

# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'


# -- Display full climatology maps =
# -- Use this variable as atlas_explorer_variables to activate the climatology maps
atlas_explorer_climato_variables = False #atlas_explorer_variables #True
add_line_of_climato_plots=True

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

thumbnail_size = "300*300"

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
