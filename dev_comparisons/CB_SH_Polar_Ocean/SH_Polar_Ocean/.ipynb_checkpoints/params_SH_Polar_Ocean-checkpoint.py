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
from custom_plot_params import dict_plot_params as custom_plot_params

# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'debug' #was 'error' before
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = False
#clog('debug')
# -- Set to True to clean the CliMAF cache
clean_cache = True
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20'), dict(pattern='oneVar')]
# -- Parallel and memory instructions
do_parallel = False
nprocs = 12
memory = 40  # in gb; 30 for ocean atlasas
# queue = 'days3' # onCiclad: h12, days3
# time = 480 # minutes
# QOS = 'test'

# -- Thumbnail sizes
# ---------------------------------------------------------------------------- >
thumbnail_size = '300*175'
thumbnail_polar_size = '250*250'
thumbnail_size_3d = '250*250'
thumbsize_zonalmean = '450*250'
thumbsize_TS = '450*250'
thumbsize_MOC_slice = '475*250'
thumbsize_MAXMOC_profile = '325*250'
thumbsize_MOC_TS = '325*250'
thumbsize_VertProf = '250*250'

# -- Set the reference against which we plot the diagnostics
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
# reference = 'default'

     
# -- Create project my_ts_obs
pattern='/home/cburgard/SCRIPTS/C-ESM-EP/REF_OBS/eORCA1.4.2_ref-${variable}_${product}_monthly.nc'
cproject('my_ice_obs', 'product', ('period','fx'), separator='%') # we set period to fx and frequency to seasonal for the climatologies
dataloc(project='my_ice_obs', url=pattern) 

pattern='/home/cburgard/SCRIPTS/C-ESM-EP/REF_OBS/${variable}_${product}_1991_2020_annualmean.nc'
cproject('my_bottom_obs', 'product', ('period','fx'), separator='%')
dataloc(project='my_bottom_obs', url=pattern)

custom_obs_dict = {
                    'iceshelf':dict(project='my_ice_obs', variable='iceshelf', product='DaiTrenberth_Davison', frequency='seasonal'),
                    'iceberg':dict(project='my_ice_obs', variable='iceberg', product='DaiTrenberth_Davison', frequency='seasonal'),
                    'T_bottom':dict(project='my_bottom_obs', variable='T_bottom', product='WOA23', period='fx', frequency='yr'),
                    'S_bottom':dict(project='my_bottom_obs', variable='S_bottom', product='WOA23', period='fx', frequency='yr'),
                    'rhopot_bottom':dict(project='my_bottom_obs', variable='rhopot_bottom', product='WOA23', period='fx', frequency='yr')}   

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "SH Polar St. - Ocean"
# With libIGCM, the user may have provided an additional title
if AtlasTitle != "NONE":
    atlas_head_title += " - " + AtlasTitle
    


# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
# -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
season = 'ANM'
# -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
proj = 'SH55'
# -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)
# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = dict(lonmin=0, lonmax=360, latmin=-90, latmax=-55)

# ---------------------------------------------------------------------------- >
# -- SH Polar Ocean variables
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
#atlas_explorer_variables_list = ['tas', 'tos', 'sos', ]
#period_manager_test_variable = 'tas'

do_ocean_2D_maps = True                                                                                                           
liste_seasons_ocean = ['ANM', 'DJF', 'JAS']        
liste_seasons_seaice = ['ANM', 'September', 'February']                                                                                             
                                                                                     
ocean_2D_variables = []                                                                                                           
for var in ['tos']:      #      , 'sos', 'iceshelf', 'iceberg'                                                                                   
    for my_season in liste_seasons_ocean:                                                                                               
        ocean_2D_variables.append(dict(variable=var, season=my_season, table='Omon', grid='gn',                                   
                                       project_specs=dict(                                                                        
                                           IGCM_OUT=dict(DIR='OCE')                                                            
                                       )                                                                                          
                                       ))
                                       
#for var in ['iceshelf', 'iceberg']:                                                                                              
#    for my_season in liste_seasons_ocean:                                                                                               
#        ocean_2D_variables.append(dict(variable=var, season=my_season, table='Omon', grid='gn',                                   
#                                       project_specs=dict(                                                                        
#                                           IGCM_OUT=dict(DIR='OCE',OUT='Output'),                                                            
#                                       )                                                                                          
#                                       ))

# -- Mixed Layer Depth
do_MLD_maps = False  # -> [NEMO Atlas] Maps of Mixed Layer Depth

# ---------------------------------------------------------------------------- >
# -- White Ocean : Sea Ice diagnostics
# ---------------------------------------------------------------------------- >
# -> [NEMO Atlas] Sea ice plots: sea ice concentration and thickness, relative to obs
do_seaice_maps = False
# do_seaice_annual_cycle = True    # -> [NEMO Atlas] Annual cycle of the sea ice volume in both hemispheres
# ---------------------------------------------------------------------------- >

# ---------------------------------------------------------------------------- >
# -- Blue Ocean : Bottom ocean diagnostics
# ---------------------------------------------------------------------------- >

do_bottomTS_maps = True

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
# Load an auxiliary file custom_plot_params (from the working directory)
# of plot params (like atmos_plot_params.py)
# -> Check $CLIMAF/climaf/plot/atmos_plot_params.py or ocean_plot_params.py
#    for an example/
  

# -- Empty params_${component}.py file! everything is done from diagnostics_${component}.py


# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #

