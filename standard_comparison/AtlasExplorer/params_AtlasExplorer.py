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




# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose='debug'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to 'True' (string) to clean the CliMAF cache
clean_cache = 'False'
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False
#nprocs = 32
#memory = 20 # in gb
#queue = 'days3'



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
#reference = 'default'




# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
season = 'ANM'  # -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
proj = 'GLOB'   # -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
domain = dict() # -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)



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
from climaf.api import *
do_atlas_explorer        = True    # -> use atlas_explorer_variables to set your own selection of variables
atlas_explorer_variables = [dict(variable='tas',
                                 project_specs = dict(
                                     IGCM_OUT=dict(DIR='ATM'),
                                     IGCM_CMIP6=dict(table='Amon'),
                                     CMIP5      = dict(table = 'Amon'),
                                     CMIP6      = dict(table = 'Amon'),
                                )),
                            dict(variable='tos',
                                 project_specs = dict(
                                     IGCM_OUT=dict(DIR='OCE'),
                                     IGCM_CMIP6=dict(table='Omon'),
                                     CMIP5      = dict(table = 'Omon'),
                                     CMIP6      = dict(table = 'Omon', grid='gn'),
                                )),
                            dict(variable='ua', season='DJF',
                                 project_specs = dict(
                                     IGCM_OUT=dict(DIR='ATM'),
                                     IGCM_CMIP6=dict(table='Amon'),
                                     CMIP5      = dict(table = 'Amon'),
                                     CMIP6      = dict(table = 'Amon'),
                                 ))
                          ]

#atlas_explorer_variables = ['tas','pr',
#                            'tos','sos',
#                            dict(variable='ua', season='DJF', add_climato_contours=True),
#                            dict(variable='ua', season='JJA', add_climato_contours=True),
#                            dict(variable='tos',domain=dict(lonmin=-80,lonmax=40,latmin=10,latmax=85)),
#                            dict(variable='sic', proj='NH50', season='March'),
#                            dict(variable='lai', season='MAM'),
#                           ]

# -- Activate the parallel execution of the plots
do_parallel=False

period_manager_test_variable = 'tas'
# ---------------------------------------------------------------------------- >




# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Atlas Explorer"

# -- Setup a custom css style file
# ---------------------------------------------------------------------------- >
style_file = '/share/fp_template/cesmep_atlas_style_css'
i=1
while not os.path.isfile(os.getcwd()+style_file):
    print i
    style_file = '/..'+style_file
    if i==3:
       break
    i=i+1
style_file = os.getcwd()+style_file


# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True

# -- Automatically zoom on the plot when the mouse is on it
# ---------------------------------------------------------------------------- >
hover = False

# -- Add the compareCompanion (P. Brockmann)
# --> Works as a 'basket' on the html page to select some figures and
# --> display only this selection on a new page
# ---------------------------------------------------------------------------- >
add_compareCompanion = True


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
from custom_plot_params import dict_plot_params as custom_plot_params
# -> Check $CLIMAF/climaf/plot/atmos_plot_params.py or ocean_plot_params.py
#    for an example/



# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #

