# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: NEMO_main                                                          - |
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
routine_cache_cleaning = [dict(age='+20'), dict(pattern='oneVar')]
# -- Parallel and memory instructions
do_parallel = False
nprocs = 32
#memory = 30 # in gb; 30 for ocean atlasas
#queue = 'days3' # onCiclad: h12, days3



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
# -- Blue Ocean : Physical Ocean diagnostics
# -- The do_ocean_2D_maps section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
# -- 2D Maps
do_ocean_2D_maps       = True    # -> [NEMO Atlas] builds a section with a list of standard oceanic variables (2D maps only)
liste_seasons = ['ANM', 'DJF', 'JJA']
ocean_2D_variables = []
for var in ['tos', 'wfo', 'sos']:
    for my_season in liste_seasons :
        ocean_2D_variables.append(dict(variable=var, season=my_season,
                                       project_specs = dict(
                                                            CMIP5      = dict(table = 'Omon'),
                                                            CMIP6      = dict(table = 'Omon', grid='gn'),
                                                            IGCM_OUT   = dict(DIR   = 'OCE'),
                                                            IGCM_CMIP6 = dict(table = 'Omon'),
                                                           )
                                    ))
for my_season in liste_seasons :
    ocean_2D_variables.append (dict(variable='zos', spatial_anomalies=True, season=my_season,
                                    project_specs = dict(
                                                         CMIP5      = dict(table = 'Omon'),
                                                         CMIP6      = dict(table = 'Omon', grid='gn'),
                                                         IGCM_OUT   = dict(DIR   = 'OCE'),
                                                         IGCM_CMIP6 = dict(table = 'Omon'),
                                                        ),
                                    ))

# -- Activate the parallel execution of the plots
do_parallel=False


#for var in ['to200', 'to1000', 'so200', 'so1000']:
#    ocean_2D_variables.append (dict (variable=var, season='ANM'))
remapping = True

period_manager_test_variable = 'tos'

# -- Mixed Layer Depth
do_MLD_maps            = True    # -> [NEMO Atlas] Maps of Mixed Layer Depth

# -- Wind stress curl
#do_curl_maps = True

# -- Time Series (spatial averages over basins)
#do_ATLAS_TIMESERIES_SPATIAL_INDEXES = True
ts_variables = ["tos","thetao"]#,"sos","so","zos"]
ts_basins    = ["GLO"]#,"ATL","PAC","IND"]

# -- Vertical Climatological profiles over basins
#do_ATLAS_VERTICAL_PROFILES = True
VertProf_variables = ["thetao","so"]
VertProf_obs       = [levitus_ac,woa13_ac]
VertProf_basins    = ["GLO","ATL","PAC","IND"]

# -- Depth/time drift profiles (averages over basins)
#do_ATLAS_DRIFT_PROFILES  = True
drift_profiles_variables = ["thetao","so"]
drift_profiles_basins    = ["GLO","ATL","PAC","IND"]

# -- MOC Diagnostics (over basins)
#do_ATLAS_MOC_DIAGS = True
MOC_basins = ["GLO","ATL","PAC"]

# -- Zonal Mean slices
#do_ATLAS_ZONALMEAN_SLICES = True
zonmean_slices_seas      = ["ANN"]#,"MAM","JJA","SON"]
zonmean_slices_variables = ["thetao","so"]
zonmean_slices_basins    = ["GLO","ATL","PAC","IND"]
y = 'lin' # -> The vertical axis; choose between 'lin' (linear) or 'index' (model index levels)
# ---------------------------------------------------------------------------- >




# ---------------------------------------------------------------------------- >
# -- White Ocean : Sea Ice diagnostics
# ---------------------------------------------------------------------------- >
do_seaice_maps         = True    # -> [NEMO Atlas] Sea ice plots: sea ice concentration and thickness, relative to obs
#do_seaice_annual_cycle = True    # -> [NEMO Atlas] Annual cycle of the sea ice volume in both hemispheres
# ---------------------------------------------------------------------------- >





# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "NEMO - general diagnostics"

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

# -- Thumbnail sizes
# ---------------------------------------------------------------------------- >
thumbnail_size           = '300*175'
thumbnail_polar_size     = '250*250'
thumbnail_size_3d        = '250*250'
thumbsize_zonalmean      = '450*250'
thumbsize_TS             = '450*250'
thumbsize_MOC_slice      = '475*250'
thumbsize_MAXMOC_profile = '325*250'
thumbsize_MOC_TS         = '325*250'
thumbsize_VertProf       = '250*250'

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

