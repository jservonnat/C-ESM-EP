# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: TurbulentAirSeaFluxes                                              - |
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
verbose = 'critical'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = False
# -- Set to 'True' (string) to clean the CliMAF cache
clean_cache = 'False'
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

# -- Set the reference against which we plot the diagnostics
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
# reference = 'default'


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
# -- Hotelling Test (Servonnat et al. 2017)
# ---------------------------------------------------------------------------- >
# Parameters
image_size = None
# reference_results = None
reference_results = 'CMIP5'
# common_grid = 'r180x90'
# -- Check the R colors here: http://www.stat.columbia.edu/~tzheng/files/Rcolor.pdf
R_colorpalette = ['dodgerblue3', 'orangered', 'green2', 'yellow3', 'navyblue', 'darkturquoise', 'mediumseagreen',
                  'firebrick3', 'violetred2', 'antiquewhite3', 'darkgoldenrod3', 'coral3', 'lightsalmon1',
                  'lightslateblue', 'darkgreen', 'darkkhaki', 'darkorchid4', 'darksalmon', 'deepink2', 'lightblue4',
                  'cadetblue', 'cadetblue1', 'aquamarine3', 'burlywood1', 'darkmagenta', 'forestgreen', 'khaki3',
                  'greenyellow', 'lightcoral', 'mediumorchid2']

regions_for_spatial_averages = []
# regions_for_spatial_averages = [ dict(region_name='Intertropical_Band', domain=[-20,20,0,360]), ]


# 1.1 Get the list of datasets (python dictionaries) from dataset_setup.py
reference_models = []
if reference_results in ['CMIP5', 'AMIP']:
    common_keys = dict(project='CMIP5',
                       experiment='historical',
                       frequency='monthly',
                       realm='ocean',
                       version='latest',
                       period='1980-2005')
    if reference_results == 'CMIP5':
        common_keys.update(dict(experiment='historical'))
    if reference_results == 'AMIP':
        common_keys.update(dict(experiment='amip'))

    # -- First, scan the CMIP5 archive to find the available models
    dum = ds(variable='tos', model='*', **common_keys)
    cmip5_models = dum.explore('choices')['model']
    cmip5_models.remove('MRI-ESM1')
    cmip5_models.remove('MRI-CGCM3')
    cmip5_models.remove('MIROC5')
    cmip5_models.remove('GFDL-CM2p1')
    cmip5_models.remove('EC-EARTH')
    # cmip5_models.remove('BNU-ESM')
    # cmip5_models.remove('FIO-ESM')

    # -- Add the CMIP5 models to the list...
    for cmip5_model in cmip5_models:
        reference_models.append(dict(model=cmip5_model, customname=cmip5_model, **common_keys))

period_manager_test_variable = 'tos'
# ---------------------------------------------------------------------------- >


# -- Some settings -- customization
# ---------------------------------------------------------------------------- >


# -- Setup a custom css style file
# ---------------------------------------------------------------------------- >
style_file = '/share/fp_template/cesmep_atlas_style_css'
i = 1
while not os.path.isfile(os.getcwd() + style_file):
    print i
    style_file = '/..' + style_file
    if i == 3:
        break
    i = i + 1
style_file = os.getcwd() + style_file

# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True

# -- Add the compareCompanion (P. Brockmann)
# --> Works as a 'basket' on the html page to select some figures and
# --> display only this selection on a new page
# ---------------------------------------------------------------------------- >
add_compareCompanion = True

# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #
