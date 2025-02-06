# Parameters file for driving an atlas showing LSM outputs (including
# Orchidee's): maps and time series

import orchidee_variables_and_functions  
import climatology_variables  # Tells which are reference observations

from orchidee_variables_and_functions import space_average_over_region

# -- Head title of the atlas
diag_name = "Orchidee"
atlas_head_title = "Orchidee"
# -- Name of the html file
index_name = None

# What type of figures should we plot
# ---------------------------------------------------------------------------- 
case_toggles = {
    'maps'       : False,       # Plain climatology maps
    'anomalies'  : False,       # Maps of differences with climatology 
    'diff'       : False,      # Maps of differences with first simulation
    'time_series': True,       # Time series of basin-integrated variables
}

# Which variables to plot, grouped by category. 
# ---------------------------------------------------------------------------- 
# Entry 'specs' allows to provide project-specific attributes for each category
variables_setup = {
    "Energy Budget": {
        'variables' : ['hfls', 'hfss', 'alb_nir', 'alb_vis',
                       'ts', 'rsds', 'rlds'], #'albedo'],
        'specs' : { 'CMIP6' : {'table' : 'Amon'}, 'IGCM_OUT' : { 'DIR' : 'SRF'}}},
    "Water Budget" : {
        'variables' : ['mrro', 'evspsbl', 'mrros', 'mrrob', 'snw'],
        'specs' : { 'CMIP6' : {'table' : 'Lmon'}, 'IGCM_OUT' : { 'DIR' : 'SRF'}}},
    "Carbon Budget": {
        'variables' : ['ra', 'rh', 'lai', 'gpp_srf', 'gpp_sbg',
                       'npp', 'nbp', 'cSoil', 'cVeg', 'cProduct'],
        'specs' : { 'CMIP6' : {'table' : 'Lmon'}, 'IGCM_OUT' : { 'DIR' : 'SBG'}}},
    #"Per PFT"      : {
    #    'variables' : ['maxvegetfrac', 'vegetfrac1', ]},
    "Meteorology"  : {
        'variables' : [ 'tair' ], }
    }

# Issues : tas, rss, rsus, albedo, pr, LAI_MEAN_GS, nbp, et en TS : maxvegetfrac
# For test purposes
alt_variables_setup = {
    "Energy Budget": {
        'variables' : ['tair', 'rsds', 'rlds', 'snw', 'alb_nir', 'alb_vis',
                       'drainage', 'evspsbl', 'evspsblsoi', 'hfls', 'hfss',
                       'maxvegetfrac', 'inter', 'mrso', 'mrsos', 'lai',
                       'rain', 'prsn', 'pr', 'runoff', 'snw', 'ts', 'TWBR'
                       ],
        'specs' : { 'CMIP6' : {'table' : 'Amon'}, 'IGCM_OUT' : { 'DIR' : 'SRF'}}},
    "Carbon Budget": {
        'variables' : ['cLitter', 'npp', 'cProduct', 'cSoil', 'cVeg', 'lai_sbg', 
                       'gpp_srf', 'gpp_sbg', 'gpp', 'lai', 'ra', 'rh'],
        'specs' : { 'CMIP6' : {'table' : 'Lmon'}, 'IGCM_OUT' : { 'DIR' : 'SBG'}}},
    }

short_variables_setup = {
    "Energy Budget": {
        'variables' : ['tair'],
        'specs' : { 'CMIP6' : {'table' : 'Amon'}, 'IGCM_OUT' : { 'DIR' : 'SRF'}}},
    "Carbon Budget": {
        'variables' : ['ra'],
        'specs' : { 'CMIP6' : {'table' : 'Lmon'}, 'IGCM_OUT' : { 'DIR' : 'SBG'}}},
    }

variables_setup = short_variables_setup 

# We can provide further project-specific attributes on a per variable basis
special_project_specs = {
    'snw'   : {'CMIP6' : { 'table' : 'LImon'}},
    'mrrob' : {'CMIP6' :{ 'table' : '*mon'}},
    'es'    : {'CMIP6' :{ 'table' : '*mon'}},
    'et'    : {'CMIP6' :{ 'table' : 'Nonemon'}},
    'cSoil' : {'CMIP6' :{ 'table' : 'Emon'}},
    #'gpp_srf': { 'IGCM_OUT' : { 'DIR': 'SRF'}},
    'lai'    : { 'IGCM_OUT' : { 'DIR': 'SRF'}},
    }

# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = {}


# ---------------------------------------------------------------------------- >
# Settings for maps plot
# ---------------------------------------------------------------------------- >

#seasons = ['ANM' , 'DJF' ] # see help(clim_average)) examples: JFM, December,...
seasons = ['ANM' ]

# Map projection
proj = 'GLOB' # see help(climaf.plot). Examples: GLOB, NH, SH, NH20, SH30...  

common_plot_params = { 'focus' : 'land', 'mpCenterLonF' : 0 , 'display_field_stats': True}

# Can define reference observations on a per-variable basis
custom_obs_dict = dict(
    hfls=dict(project='ref_climatos', product='EnsembleLEcor', frequency='annual_cycle'),
    hfss=dict(project='ref_climatos', product='EnsembleHcor', frequency='annual_cycle'),
)

# Size of the images in images arrays
thumbnail_size = '300*175'

#---------------------------------------------------------------------------------------
# Settings for time series plot - The list of variables is shared with map plots
#---------------------------------------------------------------------------------------
            
# Providing a regions file such as used in MAPPER (e.g.
# /data/vbastrik/MAPPER/REGS/regs_360720.nc on spirit)
# HOWEVER, you have to add attributes standard_name and units to lat & lon
# The regions_file will be remapped to the grid of data files
# It can be None (if useless).
ts_regions_file = "/home/ssenesi/cesmep/data/regs_360720.nc"

# Providing the list of short names (reg_id in ts_regions_file) for regions
# on which to integrate. Can be None or []
ts_regions = [ 'g', 'n', 't'  ] 
#ts_regions = None

# For reference, the list of reg_id and region names for a MAPPER file
# g (global), n (northern land), t (tropical land), s (southern land), amnbo (america north boreal), amnte (america north temperate), amstr (america south tropical), amste (america south temperate), eu (europe), asbo (asia boreal), aste (asia temperate), astr (asia tropical), afn (africa north), afs (africa south), auzea (australia & new zealand)

# frequencies on which to integrate. Can be monthly (useless), yearly, and annual_cycle
ts_frequencies = [ 'yearly', 'annual_cycle']
#ts_frequencies = [ 'annual_cycle' ]
#ts_frequencies = [ 'yearly' ]

# Size for the time series images in image arrays
ts_thumbnail_size = '180*180'

# 
# Can provide further specifications for time series, and also on a per-variable basis. 
time_series_setup = {
    # Entry 'default' applies to all variables if present
    'default' : dict(contfrac = "nc"),   
    'hfls' : dict( ylabel = 'hfls [W/m2]', )
    }

# These parameters are mainly parameters for CliMAF operator ensemble_ts_plot
# (see https://climaf.readthedocs.io/en/master/scripts/ensemble_ts_plot.html)
common_ts_plot_params = dict(
    title="Title",
    operation= space_average_over_region,
    #xlabel='years',
    year_delta=1,
    tick_size=12,
    lw=1,
    highlight_period='clim_period',
    highlight_period_lw=4,
    right_margin=0.95, left_margin=0.17, bottom_margin=0.1, top_margin=0.86,
    # xlim=['1800','2800'],
    draw_grid=False,
    right_string=" ", # Needed to overwrite default title
    
    #fig_size='3*3',
    fig_size='11*11',
    legend_fontsize=15,
    text_fontsize=10,        
    xlabel_fontsize=12,
    ylabel_fontsize=12,
    left_string_fontsize=12,
    right_string_fontsize=12,
    title_fontsize=15,

    #legend_labels=['simulation', 'climato period'],
    legend_ncol=1,
    legend_lw=[2, 2, 2],
    legend_xy_pos=[0.1, 0.9],
    #legend_colors='black,black',
    append_custom_legend_to_default=False,
    
)

period_manager_test_variable = 'hfls'


#------------------------------------------------------------------------------------
# Technical settings
#------------------------------------------------------------------------------------

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

