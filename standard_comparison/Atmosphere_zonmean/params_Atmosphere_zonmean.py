# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: Atmosphere_zonmean                                                 - |
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
nprocs = 32
#memory = 20 # in gb
#queue = 'days3'



# -- Set the reference against which we plot the diagnostics 
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
proj = 'GLOB' # -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
#domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30) # -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2) 
domain = {}




# ---------------------------------------------------------------------------- >
# -- Atmosphere diagnostics
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
do_atmos_maps   = True    # -> [LMDZ_SE Atlas] builds a section with a list of standard atmospheric variables (2D maps and zonal means)
atmos_variables_list = [
                   'ua','va','ta','hus','hur',
                   dict(variable='ua',season='DJF'),dict(variable='va',season='DJF'),dict(variable='ta',season='DJF'),
                   dict(variable='hus',season='DJF'),dict(variable='hur',season='DJF'),
                   dict(variable='ua',season='JJA'),dict(variable='va',season='JJA'),dict(variable='ta',season='JJA'),
                   dict(variable='hus',season='JJA'),dict(variable='hur',season='JJA'),
                   dict(variable='ua',y='log'),dict(variable='va',y='log'),dict(variable='ta',y='log'),
                   dict(variable='hus',y='log'),dict(variable='hur',y='log'),
                   dict(variable='ua',y='log',season='DJF'),dict(variable='va',y='log',season='DJF'),dict(variable='ta',y='log',season='DJF'),
                   dict(variable='hus',y='log',season='DJF'),dict(variable='hur',y='log',season='DJF'),
                   dict(variable='ua',y='log',season='JJA'),dict(variable='va',y='log',season='JJA'),dict(variable='ta',y='log',season='JJA'),
                   dict(variable='hus',y='log',season='JJA'),dict(variable='hur',y='log',season='JJA'),
]
atmos_variables = []
for var in atmos_variables_list:
    if isinstance(var,dict):
       tmpvar = var.copy()
       tmpvar.update(dict(add_climato_contours=True))
       atmos_variables.append(tmpvar)
    else:
       atmos_variables.append(dict(variable=var, add_climato_contours=True))

# -- Project Specs
for var in atmos_variables:
    var.update(dict(project_specs = dict(
                                         CMIP5      = dict(table = 'Amon'),
                                         CMIP6      = dict(table = 'Amon'),
                                         IGCM_OUT   = dict(DIR   = 'ATM'),
                                         IGCM_CMIP6 = dict(table = 'Amon'),
                                        ),
              ))


# -- Activate the parallel execution of the plots
do_parallel=False


period_manager_test_variable = 'ua'

# ---------------------------------------------------------------------------- >





# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

thumbnail_size="250*250"

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Atmosphere Zonal mean - seasonal"

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

