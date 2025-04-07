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
    atlas_head_title = "My own diff by hand"
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
using_climaf = True

#
# -- Head title of the atlas. Will be used also as link text in the top-level multi-atlas
# -- It is usually set in params_xx.py
if atlas_head_title is None :
    atlas_head_title = "My own diffs"
#
# - Init html index (Note: style_file is seat by main_C-ESM-EP.py)
index = header(atlas_head_title, style_file=style_file)
#
# ==> -- Open the section 
# -----------------------------------------------------------------------------------------
index += section("My own CliMAF diagnostic", level=4)
#
# ==> -- Control the size of the figures
# -----------------------------------------------------------------------------------------
#  
if thumbnail_size:
    figure_size = thumbnail_size  # possibly defined in params_xx.py
else:
    figure_size = thumbnail_size_global # defined in share/default/default_atlas_settings.py
#
# ==> -- Open a html 'table' and the html figures line with a title
# ----------------------------------------------------------------------------------------
index += open_table()  # This allows to have all figures nicely aligned across figure lines

# Create a first table line with a single element : some sub-title
index += line(['Diag #1 = diff by hand'])

#
# preliminary step = copy the models dictionary to avoid modifying the 
# entries in the (global) models dict. `models` is usually set by datasets_setup.py
Wmodels = copy.deepcopy(models)
#
# -- We will loop on some variables list (better define it in the params file)
# -----------------------------------------------------------------------------------------
my_own_climaf_diag_variables = ['tas', 'pr']
#
#
# -- Define plot parameters per variable (better if in the params file)
# -----------------------------------------------------------------------------------------
# Syntax for such settings is driven by arguments to CliMAF's `plot` operator,
# documented at https://climaf.readthedocs.io/en/master/scripts/plot.html.
# Not needed if not using CliMAF `plot`
my_own_climaf_diag_plot_params = dict(
    tas=dict(contours=1), #, min=0, max=60, delta=5, color='precip3_16lev'),
    pr=dict(contours=1, scale=86400.)#min=0, max=30, delta=2, color='precip_11lev', scale=86400.),
)
#
# Loop on variables
#
for variable in my_own_climaf_diag_variables:
    index += open_line()  # all figures for one variable will lay on a single line
    #
    # -- Loop on the models 
    # -----------------------------------------------------------------------------------------
    for model in Wmodels:
        #
        # -----------------------------------------------------------------------------------------
        wmodel = model.copy()  # - copy the dictionary to avoid modifying the original dictionary
        wmodel["variable"] = variable  # - add a variable to the dictionary
        # Avoid ambiguity on some attributes (depends on datasets_setup.py content and variable)
        if wmodel["project"] == "CMIP6" :
            wmodel["table"] = "Amon"
            wmodel["grid"] = "gr"
        if wmodel["project"] == "CMIP5" :
            wmodel["realm"] = "atmos"
        #
        # ==> -- Apply period manager
        # -----------------------------------------------------------------------------------------
        # ==> -- It aims at finding the last SE or last XX years available when the user provides
        # ==> -- clim_period='last_SE' or clim_period='last_XXY'... in model attributes.
        # ==> -- get_period_manager scans the existing files and find the requested period
        # ==> -- !!! This modifies wmodel so that it will point to the requested period
        wmodel = get_period_manager(wmodel, diag='clim')
        #
        if using_climaf :
            #
            # -- Choose season
            season = 'ANM'
            #
            # /// -- Get the dataset and compute the annual cycle using CliMAF functions
            # -----------------------------------------------------------------------------------------
            dat = clim_average(ds(**wmodel), season)
            #
            # /// -- Get the references
            # -----------------------------------------------------------------------------------------
            ref = clim_average(ds(**variable2reference(variable)), season)
            #
            # -- Regrid model on ref
            # -----------------------------------------------------------------------------------------
            rgrd_dat = regrid(dat, ref)
            #
            # -- Compute bias field
            # -----------------------------------------------------------------------------------------
            bias_field = fsub(rgrd_dat, ref)
            # ==> Use bias_field to get your scores!

            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            # build_plot_title returns the model name if project=='CMIP5' otherwise
            # it returns the simulation name. It returns the name of the reference
            # if you provide a second argument ('dat1 - dat2')
            title = build_plot_title(wmodel, None)  
            LeftString = variable
            # As right string, finds the right key for the period (period of clim_period)
            RightString = build_period_str(wmodel)  
            CenterString = 'Bias '+season
            #
            # -- Plot the amplitude of the annual cycle
            # -----------------------------------------------------------------------------------------
            plot_bias = plot(bias_field,
                             title=title,
                             gsnLeftString=LeftString,
                             gsnRightString=RightString,
                             gsnCenterString=CenterString,
                             **my_own_climaf_diag_plot_params[variable])
            #
            # ==> -- Create figure file
            # -----------------------------------------------------------------------
            figure_file = safe_mode_cfile_plot(plot_bias, safe_mode=safe_mode)
            #
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
