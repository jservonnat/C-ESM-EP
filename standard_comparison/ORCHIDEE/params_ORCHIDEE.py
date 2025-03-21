# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: ORCHIDEE                                                           - |
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
verbose = 'error'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to True to clean the CliMAF cache
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False
# nprocs = 32
# memory = 30 # in gb; 30 for ocean atlasas
# queue = 'zen4' # onCiclad: h12, days3
# time = 480 # minutes
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
atlas_head_title = "ORCHIDEE"
# When driven by libIGCM, an additional title may be provided by config.card
if AtlasTitle != "NONE":
    atlas_head_title += " - " + AtlasTitle


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
# -- ORCHIDEE Energy Budget
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
# variables_energy_budget = ['fluxlat','fluxsens','albvis','albnir','tair','swdown','lwdown']
tmp_variables_energy_budget = ['hfls', 'hfss', 'tas', 'rsds', 'rlds']
variables_energy_budget = []
for variable in tmp_variables_energy_budget:
    variables_energy_budget.append(dict(variable=variable, focus='land', mpCenterLonF=0,
                                        project_specs=dict(CMIP6=dict(table='Amon'),
                                                           IGCM_OUT=dict(
                                                               DIR='SRF')
                                                           )
                                        )
                                   )
# -> climato + bias map + difference with the first simulation
# do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas
# -> climato + bias maps
do_ORCHIDEE_Energy_Budget_climobs_bias_maps = True  # -> [ORCHIDEE Atlas
# -> climato ref simu (first) + differences with the first simulation
# do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas

calias("IGCM_OUT", 'tas', 'tair', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rsds', 'swdown', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rlds', 'lwdown', filenameVar='sechiba_history')

calias('IGCM_OUT', 'hfls', 'fluxlat', filenameVar='sechiba_history')
calias('IGCM_OUT', 'hfss', 'fluxsens', filenameVar='sechiba_history')
calias('IGCM_OUT', 'mrros', filenameVar='sechiba_history')
calias('IGCM_OUT', 'mrrob', 'drainage', filenameVar='sechiba_history')
calias('IGCM_OUT', 'et', 'evspsblveg', filenameVar='sechiba_history')
calias('IGCM_OUT', 'snw', 'frac_snow', filenameVar='sechiba_history')

calias('IGCM_OUT', 'cLitter', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'cSoil', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'cVeg', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'npp', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'gpp', filenameVar='stomate_ipcc_history')

calias('ref_climatos', 'hfls', 'fluxlat')
calias('ref_climatos', 'hfss', 'fluxsens')

custom_obs_dict = dict(
    hfls=dict(project='ref_climatos', product='EnsembleLEcor',
              frequency='annual_cycle'),
    hfss=dict(project='ref_climatos', product='EnsembleHcor',
              frequency='annual_cycle'),
)

# ---------------------------------------------------------------------------- >

period_manager_test_variable = 'hfls'

# ---------------------------------------------------------------------------- >
# -- ORCHIDEE Water Budget
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
# variables_water_budget  = ['transpir_PFT_2','inter_PFT_2_3_10','evapnu','subli','evap','runoff','drainage','snow']
variables_water_budget = ['es', 'et', 'mrros', 'mrrob', 'snw']
tmp_vars = []
for var in variables_water_budget:
    if var in ['snw']:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='LImon'))
    elif var in ['mrrob', 'es']:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='*mon'))
    elif var in ['et']:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='Nonemon'))
    else:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='Lmon'))
variables_water_budget = tmp_vars
# -> climato + bias map + difference with the first simulation
# do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas
# -> climato + bias maps
# do_ORCHIDEE_Water_Budget_climobs_bias_maps   = True     # -> [ORCHIDEE Atlas
# -> climato ref simu (first) + differences with the first simulation
# do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas
do_ORCHIDEE_Water_Budget_climatology_maps = True  # -> [ORCHIDEE Atlas
# ---------------------------------------------------------------------------- >


# ---------------------------------------------------------------------------- >
# -- ORCHIDEE Carbon Budget
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
# variables_carbon_budget = ['gpptot', 'lai', 'GPP_treeFracPrimDec', 'GPP_treeFracPrimEver', 'GPP_c3PftFrac',
#                            'GPP_c4PftFrac', 'total_soil_carb_PFT_tot',
#                            'maint_resp_PFT_2','growth_resp_PFT_2','hetero_resp_PFT_2','auto_resp_PFT_2']
variables_carbon_budget = ['cLitter', 'cSoil', 'cVeg', 'lai', 'gpp', 'npp']
# variables_carbon_budget = [ 'cSoil', 'cVeg', 'nbp']
tmp_vars = []
for var in variables_carbon_budget:
    if var in ['cSoil']:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='Emon'))
    else:
        tmp_vars.append(dict(variable=var, 
                        focus='land', table='Lmon'))
variables_carbon_budget = tmp_vars

# calias('CMIP6', 'gpptot')
# cLitter, cSoil, cVeg, lai, gpptot, nbp
# --> c = stocks ; *1000 PgC/m2
# --> autres = flux ; *1000*86400*365 gC/an/m2
# -> climato + bias map + difference with the first simulation
# do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas
# -> climato + bias maps
# do_ORCHIDEE_Carbon_Budget_climobs_bias_maps   = True     # -> [ORCHIDEE Atlas
# -> climato ref simu (first) + differences with the first simulation
# do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps   = True     # -> [ORCHIDEE Atlas
# -> climatotologies simulations
do_ORCHIDEE_Carbon_Budget_climatology_maps = True  # -> [ORCHIDEE Atlas
# ---------------------------------------------------------------------------- >


# ----------#------------------------------------------------------------------ >
# -- Some variable settings
# -- In this section we show how to add variables definitions 'on the fly'
# -- to a project (with calias() )
# -- It is also possible to create derived variables with derive().
# ---------------------------------------------------------------------------- >
# --> !!! This will not stay in the param file
cscript('select_veget_types', 'ncks ${selection} -v ${var} ${in} ${out}')

# -- GPP total ready for comparison with obs
calias("IGCM_CMIP6", 'gpptot', 'gpp')
calias("IGCM_OUT", 'cfracgpp', 'gpp', filenameVar='stomate_ipcc_history')
derive("IGCM_OUT", 'gpptot', 'divide', 'cfracgpp', 'Contfrac')
# -> alias for the obs
calias("ref_climatos", 'gpptot', 'gpp')

# -- GPP on all PFTs
calias("IGCM_OUT", 'GPP', 'gpp', scale=0.001, filenameVar='sechiba_history')

calias("IGCM_OUT", 'Contfrac', filenameVar='sechiba_history')
calias("IGCM_OUT", 'maxvegetfrac', filenameVar='sechiba_history')

# GPP * maxvegetfrac * Contfrac
derive("IGCM_OUT", 'GPPmaxvegetfrac', 'multiply', 'GPP', 'maxvegetfrac')
derive("IGCM_OUT", 'GPPmaxvegetfracContfrac',
       'multiply', 'GPPmaxvegetfrac', 'Contfrac')

# GPP treeFracPrimDec
derive('IGCM_OUT', 'GPP3689', 'select_veget_types', 'GPPmaxvegetfracContfrac',
       selection='-d veget,2 -d veget,5 -d veget,7 -d veget,8')
derive("IGCM_OUT", 'GPP_treeFracPrimDec', 'ccdo',
       'GPP3689', operator='vertsum -selname,GPP3689')

# GPP treeFracPrimEver
derive('IGCM_OUT', 'GPP2457', 'select_veget_types', 'GPPmaxvegetfracContfrac',
       selection='-d veget,1 -d veget,3 -d veget,4 -d veget,6')
derive("IGCM_OUT", 'GPP_treeFracPrimEver', 'ccdo',
       'GPP2457', operator='vertsum -selname,GPP2457')

# GPP c3PftFrac
derive('IGCM_OUT', 'GPP1012', 'select_veget_types',
       'GPPmaxvegetfracContfrac', selection='-d veget,9 -d veget,11')
derive("IGCM_OUT", 'GPP_c3PftFrac', 'ccdo',
       'GPP1012', operator='vertsum -selname,GPP1012')

# GPP c4PftFrac" (PFTs 11, 13)
derive('IGCM_OUT', 'GPP1113', 'select_veget_types',
       'GPPmaxvegetfracContfrac', selection='-d veget,10 -d veget,12')
derive("IGCM_OUT", 'GPP_c4PftFrac', 'ccdo',
       'GPP1113', operator='vertsum -selname,GPP1113')

thumbnail_size = '300*175'
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
