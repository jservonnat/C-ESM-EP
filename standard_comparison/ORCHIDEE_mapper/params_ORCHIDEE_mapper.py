# Parameters file for driving an atlas showing maps and time series,
# with an 'interactive' html page (i.e. allowing selection of what is
# displayed)

# It is applicable to any component.

# Here, we apply it to Orchidee variables, and using Orchidee variable
# names rather than CMIP names. We make use of data and functions
# from module orchidee_definitions

from ORCHIDEE_mapper import orchidee_definitions

# Warning : we may supersede some values from root custom_obs_dict
custom_obs_dict.update(orchidee_definitions.orchidee_custom_obs_dict )

# -- Head title of the atlas
diag_name = "Orchidee"
atlas_head_title = "ORCHIDEE Mapper"

# What type of figures should we plot
# ---------------------------------------------------------------------------- 
case_toggles = {
    'maps'       : True,       # Plain climatology maps
    'anomalies'  : True,       # Maps of differences with climatology 
    'diffs'      : True,        # Maps of differences with first simulation
    'time_series': True,       # Time series of basin-integrated variables
}
# For test purposes
tcase_toggles = {
    'anomalies'  : True,       # Maps of differences with climatology 
}
# Which variables to plot, grouped by category. 
# ---------------------------------------------------------------------------- 
# Entry 'specs' allows to provide project-specific attributes for each category
variables_setup = {
    "Energy Budget": {
        'variables' : ['fluxlat', 'fluxsens', 'albedo', 'alb_nir', 'alb_vis',
                       'temp_sol', 'swdown', 'lwdown'],
        'specs' : { 'CMIP6' : {'table' : 'Amon'}, }},
    "Water Budget" : {
        'variables' : ['mrso', 'humrel', 'transpir', 'inter', 'evap',
                       'evapnu', 'snow', 'ratio_ie', 'ratio_te', 'twbr'], },
    "Carbon Budget": {
        'variables' : ['lai', 'LAI_MEAN_GS', 'gpp_srf', 'gpp_ipcc',
                       'npp', 'nbp', 'ra', 'rh', 'fLuc', 'fHarvest',
                       'fWoodharvest', 'cSoil', 'cVeg', 'cProduct', 'ratio_ng'],},
    #"Per PFT"      : {
    #    'variables' : ['maxvegetfrac', 'vegetfrac1', ]},
    # "Meteorology": {
    #     'variables' : ['Tair', 'Rainf', 'Snowf', 'SWdown', 'LWdown', 'snow'], 
    #     'specs' : { 'IGCM_OUT' : { 'DIR' : '*'}}},
    }

# For test purposes
tvariables_setup = {
    "Test_category": {
        'variables' : [ 'fluxlat', ],
    }
}

# We can provide further specifications, both for maps and time
# series, on a per-variabe basis, in dict 'variables_specifics', which
# keys are variable names and values are corresponding dicts

# There, keys can be : units, longname, global_sum_scale, ratio, ratio_threshold
#  - units is used in map plot title 
#  - longname supersedes the value provided by climaf function varlongame
#    when building maps line titles 
#  - global_sum_scale is a pair (scaling_factor, units) driving the display of the
#    spatial integration on maps (when display_field_stats is True)
#  - ratio is used to define a variable as the ratio of two other variables,
#    computed AFTER time averaging. ratio_threshold then applies to the
#    numerator for defining missing values of the ratio

# Keys can also be any argument to the map plot or time series plot operators,
# but for that, it is wiser to use dedicated dicts defined further below
# (plots_setup and time_series_setup)

variables_specifics = {
    # Here, mainly fed by init_orchidee_variables(), see below
    
    # Some examples :
    # "fluxlat" : { "units" : "W/m**2"},
    # "cLitter" : { "global_sum_scale" : ("1E-12" , "PgC")},
    
    # "ratio_ep" : { "ratio": "evap/precip", "ratio_threshold": "1E-3" ,
    #                "longname": "Evapotranspiration-Precipitation Ratio" }
    
    # An advanced definition of a ratio, for providing additional info
    # for the denominator variable :
    #  ratio_ng" : { "ratio": [ ("npp",{}), ("gpp_srf",{"DIR":"SRF"})] ,
    #                "ratio_threshold": "1E-8" , "longname": "NPP-GPP Ratio" },

}

# We can provide further project-specific attributes on a per variable basis
# For IGCM_OUT, we can e.g. include values for DIR and OUT (albeit, for Orchidee,
# this is done by init_orchidee_variables() )
special_project_specs = {
    # Here, mainly fed by init_orchidee_variables(), see below
    'nbp'   : {'IGCM_OUT' : { 'OUT' : '*'}},
    }


# domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30)
domain = {}

# ---------------------------------------------------------------------------- >
# Settings for maps plot
# ---------------------------------------------------------------------------- >

seasons = ['ANM' , 'DJF' ] # see help(clim_average)) examples: JFM, December,...
#seasons = ['ANM' ]

# Map projection
proj = 'GLOB' # see help(climaf.plot). Examples: GLOB, NH, SH, NH20, SH30...  

# We can provide specifications for maps, which apply to all variables
# This includes arguments for operator 'plot'
# (see https://climaf.readthedocs.io/en/master/scripts/plot.html)
common_plot_params = {
    'focus' : 'land',
    'mpCenterLonF' : 0 ,
    'display_field_stats': True,
}

# We can provide further specifications for maps, on a per-variable basis.
plots_setup = {
    # Here, mainly fed by init_orchidee_variables(), see below
    # "rain" : { "bounds": "0 0.1 0.5 1 2 3 5 8 10 15 20" }
}

# Size of the images in map arrays
thumbnail_size = '300*175'

#---------------------------------------------------------------------------------------
# Settings for time series plot (the list of variables is shared with map plots)
#---------------------------------------------------------------------------------------
            
# Providing a region file. It can be None (if useless).
# It will be remapped to the grid of data files using a nearest neighbour scheme
ts_regions_file = main_cesmep_path + "/data/regs_360720.nc"

# The structure is based on MAPPER regions files. HOWEVER,
# you have to add attributes standard_name and units to lat & lon

# Providing the list of short names (reg_id in ts_regions_file) for regions
# on which to integrate.
# As a special, built-in case, "G" means full globe. None and [] translate to ['G']
# Default value is None
ts_regions = [ 'G', 'g', 't'  ] 
ts_regions = None

# For reference, the list of reg_id and region names for a MAPPER file
# g (global), n (northern land), t (tropical land), s (southern land), amnbo (america north boreal), amnte (america north temperate), amstr (america south tropical), amste (america south temperate), eu (europe), asbo (asia boreal), aste (asia temperate), astr (asia tropical), afn (africa north), afs (africa south), auzea (australia & new zealand)

# frequencies on which to integrate. Can be monthly, yearly, and annual_cycle
ts_frequencies = [ 'yearly', 'annual_cycle']

# Size for the time series images in image arrays
ts_thumbnail_size = '220*200'

# 
# These parameters are mainly parameters for CliMAF operator ensemble_ts_plot
# (see https://climaf.readthedocs.io/en/master/scripts/ensemble_ts_plot.html)
common_ts_plot_params = dict(
    title="Title",
    # year_delta=1, # Interval between x labels
    tick_size=12, # Size of x labels
    lw=1,
    highlight_period='clim_period', highlight_period_lw=4,
    right_margin=0.95, left_margin=0.17, bottom_margin=0.1, top_margin=0.86,
    draw_grid=False,
    right_string=" ", # Needed to overwrite default title
    
    fig_size='10*8',
    legend_fontsize=15,
    text_fontsize=10,        
    xlabel_fontsize=18,
    ylabel_fontsize=21,
    left_string_fontsize=21,
    right_string_fontsize=21,
    title_fontsize=25,

    #legend_labels=['simulation', 'climato period'],
    legend_ncol=1,
    legend_lw=[2],
    legend_xy_pos=[0.1, 0.9],
    #legend_colors='black,black',
    append_custom_legend_to_default=False,
)

# We can also provide specifications for time series on a per-variable
# basis.
# As a default, all variables are averaged over the regions defined
# above, but one can set
# {"operation" : CM_atlas.spatial_integration.integral_over_region }
# for changing that to a sum rather than an average
time_series_setup = {
    # Here, this dict is mainly fed by init_orchidee_variables(), see below
    "lai_sbg": dict(title="the lai from SBG dir"),
    }

#------------------------------------------------------------------------------------
# Orchidee specific : we use a dedicated module for feeding all dictionnaries above
#------------------------------------------------------------------------------------
# Module 'orchidee_definitions' include dedicated data and function for that 
orchidee_definitions.init_orchidee_variables(
    variables_setup, plots_setup, time_series_setup,
    variables_specifics, special_project_specs)

# Similar for observations
orchidee_definitions.declare_orchidee_alias_for_observations()


#------------------------------------------------------------------------------------
# Technical settings
#------------------------------------------------------------------------------------
mdebug = False
#mdebug = True

# -- Safe Mode 
safe_mode = not mdebug

# -- Set the verbosity of CliMAF (debug < info < warning < error <  critical)
if mdebug :
    verbose = 'debug'
else:
    verbose = 'error' 
    
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

# Should we activate interactive selection (a la Mapper) in html pages
interactive_selection = True
