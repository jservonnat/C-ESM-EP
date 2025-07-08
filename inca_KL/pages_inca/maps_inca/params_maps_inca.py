
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
from climaf.utils import ranges_to_string
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
#nprocs = 32
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

atlas_explorer_variables_list = ['vmro3_surf', 'vmrch4_surf', 'vmrnox_surf', 'vmrnh3_surf', 'vmrh2_surf', 'vmrco_surf', 'vmrn2o_surf']

my_title = {'vmro3_surf': 'Surface Volume Mixing Ratio of O3',
            'vmrch4_surf':'Surface Volume Mixing Ratio of CH4',
            'vmrnox_surf':'Surface Volume Mixing Ratio of NOx',
            'vmrnh3_surf':'Surface Volume Mixing Ratio of NH3',
            'vmrh2_surf': 'Surface Volume Mixing Ratio of H2',
            'vmrco_surf': 'Surface Volume Mixing Ratio of CO',
            'vmrn2o_surf':'Surface Volume Mixing Ratio of N2O'}

calias("IGCM_OUT", 'vmrch4', scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrn2o', scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrco',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmro3',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrnh3', scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrh2',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno',  scale=1e9, filenameVar='inca_species')
calias("IGCM_OUT", 'vmrno2', scale=1e9, filenameVar='inca_species')

for tmpvar in ['vmrh2', 'vmrch4', 'vmrn2o', 'vmrnh3', 'vmrno', 'vmrno2', 'vmrco', 'vmro3']:
    derive('*', tmpvar + '_surf', 'ccdo', tmpvar, operator='sellevidx,1')

derive('*', 'vmrnox_surf', 'plus', 'vmrno_surf', 'vmrno2_surf')

# -- Project Specs
atlas_explorer_variables = []
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, proj='GLOB',line_title=my_title[var],
                                             project_specs=dict(IGCM_OUT=dict(DIR='CHM'),),
                                             ))

my_dict_plot_params = {}
for var in atlas_explorer_variables_list:
    my_dict_plot_params[var] = {'default': {'color':'BlAqGrYeOrRe'},
            'full_field':{'gsnCenterString':'units: ppb', 'color':'MPL_BuGn'},
            'bias': {'color':'BlueYellowRed'},
            'model_model': {'color':'BlueWhiteOrangeRed'} }

atlas_explorer_variables_list = ['emin2o', 'emich4', 'eminox', 'emico', 'emih2', 'eminh3',
        'totdepnoy', 'drydepnoy', 'wetdepnoy', 'totdepnhx', 'drydepnhx', 'wetdepnhx']

my_title = {'emin2o':'Emissions of N2O',
            'emich4':'Emissions of CH4',
            'eminox':'Emissions of NOx',
            'emico': 'Emissions of CO',
            'emih2': 'Emissions of H2',
            'eminh3':'Emissions of NH3',
            'totdepnoy':'Total deposition of NOy',
            'drydepnoy' : 'Dry deposition of NOy', 
            'wetdepnoy' : 'Wet deposition of NOy', 
            'totdepnhx':'Total deposition of NHx',
            'drydepnhx' : 'Dry deposition of NHx', 
            'wetdepnhx' : 'Wet deposition of NHx',
            }

# -- Project Specs
for var in atlas_explorer_variables_list:
    for seas in my_seasons:
        atlas_explorer_variables.append(dict(variable=var, season=seas, proj='Robinson', line_title=my_title[var],scale=1e6,
                                             project_specs=dict(IGCM_OUT=dict(DIR='CHM'),),
                                             ))

for var in atlas_explorer_variables_list:
    if var[:3]=='emi':
        my_dict_plot_params[var] = {'default': {'gsnCenterString':'units: kg/m2/s', 'color':'drought_severity'},
            'bias': {'color':'BlueWhiteOrangeRed'},
            'model_model': {'color':'BlueYellowRed'} }
    else:
        my_dict_plot_params[var] = {'default': {'color':'prcp_2'},
                'full_field': {'gsnCenterString':'units: kg/m2/s', 'color':'prcp_2', 'colors': ranges_to_string(ranges=[0, 100, 25], add=[250, 400, 600, 900, 3000])},
            'bias': {'color':'BlueWhiteOrangeRed'},
            'model_model': {'color':'BlueYellowRed'} }


calias("IGCM_OUT", 'emin2o', scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emich4', scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emico',  scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emino',  scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emino2', scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'emih2',  scale=1e3*3600*24*365, filenameVar='inca_emi') 
calias("IGCM_OUT", 'eminh3', scale=1e3*3600*24*365, filenameVar='inca_emi') 

derive("*", "eminox", "plus", "emino", "emino2")

derive('*', 'emi_n2o', 'multiply', 'emin2o', 'aire')
derive('*', 'emi_ch4', 'multiply', 'emich4', 'aire')
derive('*', 'emi_co',  'multiply', 'emico',  'aire')
derive('*', 'emi_nox', 'multiply', 'eminox', 'aire')
derive('*', 'emi_h2',  'multiply', 'emih2',  'aire')
derive('*', 'emi_nh3', 'multiply', 'eminh3', 'aire')


## from /ccc/work/cont003/gen2201/p24haug/EXTRACT/prepare_Ndep.job
#inca_dep = ['drynoyN','drynh3N','wet3d_hno3','wet3d_noy','wet3d_nh3','wetno3ci','dryno3ci','sedno3ci','wetno3cs','dryno3cs','sedno3cs','wetno3as','dryno3as','sedno3as','wetnh4as','drynh4as','sednh4as']
#for var in inca_dep :
#    calias("IGCM_OUT", var, filenameVar='inca_dep')

#moyenne 
ncwa = ['drynoyN','drynh3N','wetno3ci','dryno3ci','sedno3ci','wetno3cs','dryno3cs','sedno3cs','wetno3as','dryno3as','sedno3as','wetnh4as','drynh4as','sednh4as']
print(atlas_explorer_variables)
for var in ncwa:
    print('var dans ncwa', var)
    calias("IGCM_OUT", var, filenameVar='inca_dep')
    derive('*', 'ncwa_'+var, 'ccdo', var, operator='vertmean')

int_vert = ['wet3d_hno3','wet3d_noy','wet3d_nh3']
for var in int_vert:
    print('var dans intv', var)
    calias("IGCM_OUT", var, filenameVar='inca_dep')
    derive('*', 'intv_'+var, 'ccdo', var, operator='vertsum -selname,'+var)

derive('*', 'wetnoy', 'rescale', 'intv_wet3d_noy', scale=60*60*24*365*1e6, offset=0)
derive('*', 'wetnh3', 'rescale', 'intv_wet3d_nh3', scale=60*60*24*365*1e6, offset=0)
derive('*', 'drynoy', 'rescale', 'ncwa_drynoyN', scale=60*60*24*365*1e6, offset=0)
derive('*', 'drynh3', 'rescale', 'ncwa_drynh3N', scale=60*60*24*365*1e6, offset=0)

derive('*', 'sum_no3ci', 'plus', 'ncwa_wetno3ci', 'ncwa_sedno3ci')
derive('*', 'no3ciw', 'rescale', 'sum_no3ci', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'no3cid', 'rescale', 'ncwa_dryno3ci', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'sum_no3cs', 'plus', 'ncwa_wetno3cs', 'ncwa_sedno3cs')
derive('*', 'no3csw', 'rescale', 'sum_no3cs', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'no3csd', 'rescale', 'ncwa_dryno3cs', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'sum_no3as', 'plus', 'ncwa_wetno3as', 'ncwa_sedno3as')
derive('*', 'no3asw', 'rescale', 'sum_no3as', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'no3asd', 'rescale', 'ncwa_dryno3as', scale=(60.*60.*24.*365.)/62*14*1e6, offset=0)
derive('*', 'sum_nh4as', 'plus', 'ncwa_wetnh4as', 'ncwa_sednh4as')
derive('*', 'nh4asw', 'rescale', 'sum_nh4as', scale=(60.*60.*24.*365.)/18*14*1e6, offset=0)
derive('*', 'nh4asd', 'rescale', 'ncwa_drynh4as', scale=(60.*60.*24.*365.)/18*14*1e6, offset=0)

derive('*', 'wetdepnoy1', 'plus', 'wetnoy', 'no3ciw')
derive('*', 'wetdepnoy2', 'plus', 'wetdepnoy1', 'no3csw')
derive('*', 'wetdepnoy', 'plus', 'wetdepnoy2', 'no3asw')
derive('*', 'drydepnoy1', 'plus', 'drynoy', 'no3cid')
derive('*', 'drydepnoy', 'plus', 'drydepnoy1', 'no3csd')
derive('*', 'totdepnoy', 'plus', 'wetdepnoy', 'drydepnoy')
derive('*', 'wetdepnhx', 'plus', 'wetnh3', 'nh4asw')
derive('*', 'drydepnhx', 'plus', 'drynh3', 'nh4asd')
derive('*', 'totdepnhx', 'plus', 'wetdepnhx', 'drydepnhx')


# -- Choose the regridding (explicit ; can also be used in the variable dictionary)
regridding = 'model_on_ref'  # 'ref_on_model', 'no_regridding'

# -- Display full climatology maps =
# -- Use this variable as atlas_explorer_variables to activate the climatology maps
atlas_explorer_climato_variables = False #atlas_explorer_variables

period_manager_test_variable = 'emin2o'
# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

#klaurent
#thumbnail_size = "250*250"

# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True
add_line_of_climato_plots=True

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
