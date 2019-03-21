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
from climaf.operators import derive

# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose='debug'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to 'True' (string) to clean the CliMAF cache
clean_cache = 'False'
# -- routine_cache_cleaning is a dictionary or list of dictionaries provided
#    to crm() at the end of the atlas (for a routine cache management)
routine_cache_cleaning = [dict(access='+20')]
# -- Parallel and memory instructions
do_parallel = False
nprocs = 32
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
# -- Main Time Series
# -- Main Time Series is built on Time Series Explorer.
# -- It's meant to be a simple and flexible way to produce time series
# -- on demand.
# ---------------------------------------------------------------------------- >
do_main_time_series        = True    # -> use atlas_explorer_variables to set your own selection of variables

def annual_mean_space_average(dat):
    return space_average(ccdo(dat,operator='yearmean'))

def annual_seaice_volume(dat, **kwargs):
    domain=dict(lonmin=0,lonmax=360,latmin=50,latmax=90)
    if 'grid_file' in kwargs:
        ds_grid = fds(kwargs['grid_file'], period='fx', variable='area')
    else:
        print 'No grid file provided'
    return ccdo(
            multiply(
                llbox(ccdo(dat,operator='yearmean'),**domain),
                llbox(ds_grid, **domain)
            ),
            operator='fldsum')

derive('IGCM_OUT','sicsit','multiply','sic','sit')
derive('IGCM_OUT','to_12','ccdo','thetao', operator='intlevel,100')
derive('CMIP6','sicsit','multiply','sic','sit')
derive('CMIP6','to_12','ccdo','thetao', operator='intlevel,100')

time_series_specs = [
    dict(variable='tos',
         project_specs = dict(
                              CMIP5    = dict(table='Omon'),
                              CMIP6    = dict(table='Omon',grid="gn"),
                              IGCM_OUT = dict(DIR='OCE'),
                             ),
         domain=dict(lonmin=0,lonmax=360,latmin=-50,latmax=50),
         operation=annual_mean_space_average,
         offset=-273.15,
         left_string='SST 50S/50N',
         ylabel='SST (degC)', xlabel='Time (years)',
         horizontal_lines_values=22.41, horizontal_lines_colors='gray',
         text=['1800-01-01',22.42,'HadISST 1990-2010'],
         ylim=[20,23],
         text_fontsize=15,
    ),



    dict(variable='tas',
         project_specs = dict(
                              CMIP5    = dict(table='Amon'),
                              CMIP6    = dict(table='Amon'),
                              IGCM_OUT = dict(DIR='ATM'),
                             ),
         operation=annual_mean_space_average,
         offset=-273.15,
         left_string='2m Temperature Global average',
         ylabel='Temperature (degC)', xlabel='Time (years)',
    ),

    #dict(variable='sicsit',
    #     operation=annual_seaice_volume,
    #     operation_kwargs = dict(grid_file='/data/igcmg/database/grids/eORCA1.2_grid.nc'),
    #     scale=1/1e8,
    #     center_string='Arctic Sea Ice Annual Volume',
    #     right_string='-',
    #     ylabel='Sea Ice Volume (km3)', xlabel='Time (years)',
    #     ylabel_fontsize=15, 
    #    )

]

apply_period_manager_once_for_all_diags=False
period_manager_test_variable = 'tos'

common_ts_plot_params = dict(
         fig_size='15*5',
         lw=1,
         highlight_period='clim_period',
         highlight_period_lw=4,
         right_margin=0.95, bottom_margin=0.4,
         legend_fontsize=15,
         legend_labels=['simulation','climato period'],
         legend_lw=[7,2,4],
         legend_xy_pos=[-0.03,-0.3],
         legend_colors='black,black',
         legend_ncol=4,
         append_custom_legend_to_default=True,
         #xlim=['1800','2800']
)

for elt in time_series_specs:
    for common_key in common_ts_plot_params:
        if common_key not in elt:
           elt.update({common_key:common_ts_plot_params[common_key]})


# ---------------------------------------------------------------------------- >




# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "IGCM meetings main time series"

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

