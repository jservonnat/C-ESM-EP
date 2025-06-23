#
# Example of a diagnostic module in C-ESM-EP ( CliMAF Earth System Model Evaluation Platform )
#

# The principles :

# Such a module is 'loaded'(using exec()) by the C-ESM-EP driver,
# i.e. main_C-ESM-EP.py, That driver imports various functions
# (including CliMAF's), which defines a series of variables. See
# details at file end.

# It is loaded after file ../datasets_setup.py, which should define
# the list of models to work on: 'models'. A 'model' is here are
# dictionnary of key/value pairs defining the data (except the
# vairable name), where keys are the facet names for the data's
# 'project' (e.g. CMIP5, IGCM_OUT)

# It is also loaded after file ./params_xxx.py, which should set all
# parameters driving the diagnostic computation that are more prone to
# change than the code here.

# -- Head title of the atlas. Should normally be set in params_xx.py
# ---------------------------------------------------------------------------- >
if atlas_head_title is None:
    atlas_head_title = "My own diagnostics"
    # When driven by libIGCM, an additional title may be provided by config.card
    if AtlasTitle != "NONE":
        atlas_head_title += " - " + AtlasTitle

# You may have empty datasets_setup.py and params_xxx.py files, and
# set everything here. But the idea is that the diagnostics_xx.py code
# is ultimately part of C-ESM-EP shared code (and lies in shared/
# dir), while params_xx.py can be modified by each user, and lies in
# the comparison dir

# In this example, we include here params_xx.py material ; see near file end. 

# This module's tasks are:
# - create figures, possibly using CliMAF. If not, you have to find the data using
#   the attributes for each model in dict `models`. You may use CliMAF for easing
#   that part, see section 'Finding data files with CliMAF' below
#
# - define and populate variable 'index', which is the html code for the atlas, by using
#   a few CliMAF functions and providing them with the figures paths
#   See example below and doc for such functions at
#   https://climaf.readthedocs.io/en/master/functions_results_viewing.html#module-climaf.chtml

# The figures should rather be organized in lines of figures, with one line per
# combination of variable + season

# The section starting with comment ==> are mandatory to build a section in the atlas.
# The comments starting with /// identify code that is specific to the diagnostic
# presented here.

# --  See full documentation at: https://github.com/jservonnat/C-ESM-EP/wiki                               - |
#
# -----------------------------------------------------------------------------------------

# This code can run with or without using CliMAF for computation. 
using_climaf = False

#
# -- Head title of the atlas. Will be used also as link text in the top-level multi-atlas
# -- It is usually set in params_xx.py
if atlas_head_title is None :
    atlas_head_title = "My own diagnostics"
#
# - Init html index (Note: style_file is set by main_C-ESM-EP.py)
index = header(atlas_head_title, style_file=style_file)
#
# ==> -- Control the size of the figures
# -----------------------------------------------------------------------------------------
if thumbnail_size:
    figure_size = thumbnail_size  # possibly defined in params_xx.py
else:
    figure_size = thumbnail_size_global # defined in share/default/default_atlas_settings.py
#

for hem in ['n','s']:
    index += open_table()  # This allows to have all figures nicely aligned across figure lines
    if hem == 'n':
        index += line(['Diagnostics in the Northern Hemisphere'])
    elif hem == 's':
        index += line(['Diagnostics in the Southern Hemisphere'])

    # create line
    Wmodels = copy.deepcopy(models)
    #my_own_climaf_diag_variables = [''siconc'']
    index += open_line()  # the figures for all models will lay on a single line
    for model in Wmodels:
        #
        # /// -- Get the dataset and compute the annual cycle using CliMAF functions
        # -----------------------------------------------------------------------------------------
        #dat = annual_cycle(ds(**wmodel))
        wmodel = model.copy()  # - avoid modifying the original dictionary

        ### Sea ice extent
        wmodel["variable"] = 'siconc'
        wmodel = get_period_manager(wmodel, diag='clim')
        wmodel.pop('variable')
        var_group = 'siconc'
        calias("IGCM_OUT", 'siconc', filenameVar="icemod")
        dat_siconc = ds(variable='siconc', **wmodel)
        dat_siconc_crop = ccdo(dat_siconc,operator='gec,.15') 
        # pour recuperer area dans un gridfile, definit dans dataset_setup "common_keys"
        #dat_area = fds(wmodel['gridfile'],period='fx',variable=wmodel['varname_area'])
        dat_area = fds(wmodel['gridfile'],period='fx',variable='AREA')
        dat_lat = fds(wmodel['gridfile'],period='fx',variable='LAT')
        # we select subdomain depending on hemisphere considerded
        if hem == 'n':
            ##sub_dat_siconc = llbox(dat_siconc, latmin=50, latmax=90, lonmin=0, lonmax=360)
            ##sub_dat_area = llbox(dat_area, latmin=50, latmax=90, lonmin=0, lonmax=360)
            dat_lat_hem = ccdo(dat_lat,operator='setrtomiss,-90,0')
        elif hem == 's':
            ##sub_dat_siconc = llbox(dat_siconc, latmin=-90, latmax=-50, lonmin=0, lonmax=360)
            ##sub_dat_area = llbox(dat_area, latmin=-90, latmax=-50, lonmin=0, lonmax=360)
            dat_lat_hem = ccdo(dat_lat,operator='setrtomiss,0,90')
        # JS DEBUG 1: premier truc => changer ccdo en ccdo2 (qui prend deux datasets en arguments)
        #old#dat_area_hem = ccdo(dat_lat_hem,dat_area,operator='ifthen')
        dat_area_hem = ccdo2(dat_lat_hem,dat_area,operator='ifthen')
        # JS DEBUG 2: deuxieme truc => Le script de plot râle parce que l'objet dat_ext (attention, subtile):
        #   - contient une variable qui s'appelle LAT
        #   - alors que le fichier netcdf qui est produit par l'execution de dat_ext contient la variable AREA...
        #old#dat_ext = annual_cycle(ccdo(multiply(fdiv(dat_area_hem,10**12),dat_siconc_crop),operator='fldsum'))
        # ==> Donc pour eviter ça, je propose ça:
        cscript('c_ice_volume','cdo fldsum -mul -mulc,1e12 ${in_1} ${in_2} ${out} ; ncrename -v .AREA,volume -v .LAT,volume ${out}', _var='volume')
        dat_ext = annual_cycle( c_ice_volume(dat_area_hem, dat_siconc_crop) )
        # JS DEBUG 3: enfin, le troisième soucis (subtile aussi...): pour construire la legende de la TS dans le plot, ts_plot utilise par defaut
        # la CRS (genre ça: "ccdo(c_ice_volume(ccdo2(ccdo(ds('file|eORCA1.4.2_grid|LAT|fx|global|no_model|/projets/nemo-rd/IPSLCM/AREA/eORCA1.4.2_grid.nc'),operator='setrtomiss,-90,0'), [...] 1939%*'),operator='gec,.15')),operator='ymonavg')" comme nom de la simu; et apparemment les | posent problème.
        # Donc autant dire à ts_plot quel est le nom du modèle qu'on veut plotter.
        # Pour ça on utilise build_plot_title(wmodel), qui va te renvoyer customname si il y en a un, ou un nom composé du model et de la simulation
        # si il n'y en a pas; on passe le couple nom:objet à ts_plot à l'aide d'un dictionnaire (ça marche aussi avec plusieurs simulations,
        # via un dictionnaire ou un ensemble)
        plot_cycle=ts_plot({build_plot_title(wmodel):dat_ext})

        # /// -- Build the titles
        # -----------------------------------------------------------------------------------------
        # build_plot_title returns the model name if project=='CMIP5' otherwise
        # it returns the simulation name. It returns the name of the reference
        # if you provide a second argument ('dat1 - dat2')
        title = build_plot_title(wmodel, None)  
        LeftString = 'Sea Ice extent'
        # As right string, finds the right key for the period (period of clim_period)
        RightString = build_period_str(wmodel)  
        CenterString = 'Seas cyc. amplitude'
        #
        # ==> -- Create figure file
        # -----------------------------------------------------------------------
        figure_file = safe_mode_cfile_plot(plot_cycle, safe_mode=safe_mode)
        #
        # ==> -- Add the plot to the figures line
        # -----------------------------------------------------------------------------------------
        index += cell("", figure_file, thumbnail=figure_size, hover=False, **alternative_dir)
        #
    # ==> -- Close the line for the variable
    # -----------------------------------------------------------------------------------------
    index += close_line()
    #
# ==> -- Close the table before possibly adding a section
# -----------------------------------------------------------------------------------------
index += close_table()

# --   End

# ------------------------------------------------------------------------------------------------------ \
# --                                                                                                    - \
# --                                                                                                     - \
# -- main_C-ESM-EP.py will provide you with:                                                              - |
# --   - the list 'models' defined in datasets_setup.py, as well as 'reference'                           - |
# --     if use_available_period_set == True, it means that you also have Wmodels_clim and Wmodels_ts     - |
# --     that correspond to 'models' with periods for climatologies and time series (respectively)        - |
# --     that have already been found (if you used arguments like 'last_10Y', 'first_30Y', 'full' or '*') - |
# --   - alternative_dir: to be used as an argument to cell(..., **alternative_dir)                  - |
# --   - the parameters from params_${component}.py (safe_mode,                                           - |
# --   - the cesmep modules in share/cesmep_modules                                                       - |
# --   - the default values from share/default/default_atlas_settings.py                                  - |
# --                                                                                                      - /
# ---------------------------------------------------------------------------------------------------- /
