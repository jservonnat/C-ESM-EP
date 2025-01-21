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
index += line(['Diag #1 = amplitude of the annual cycle'])

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
    tas=dict(contours=1, min=0, max=60, delta=5, color='precip3_16lev'),
    pr=dict(contours=1, min=0, max=30, delta=2, color='precip_11lev', scale=86400.),
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
            # /// -- Get the dataset and compute the annual cycle using CliMAF functions
            # -----------------------------------------------------------------------------------------
            dat = annual_cycle(ds(**wmodel))
            #
            # -- Compute the amplitude of the annual cycle (max - min)
            # -----------------------------------------------------------------------------------------
            amp = minus(ccdo(dat, operator='timmax'),
                        ccdo(dat, operator='timmin'))
            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            # build_plot_title returns the model name if project=='CMIP5' otherwise
            # it returns the simulation name. It returns the name of the reference
            # if you provide a second argument ('dat1 - dat2')
            title = build_plot_title(wmodel, None)  
            LeftString = variable
            # As right string, finds the right key for the period (period of clim_period)
            RightString = build_period_str(wmodel)  
            CenterString = 'Seas cyc. amplitude'
            #
            # -- Plot the amplitude of the annual cycle
            # -----------------------------------------------------------------------------------------
            plot_amp = plot(amp, title=title, gsnLeftString=LeftString, gsnRightString=RightString,
                            gsnCenterString=CenterString, **my_own_climaf_diag_plot_params[variable])
            #
            # ==> -- Create figure file
            # -----------------------------------------------------------------------
            figure_file = safe_mode_cfile_plot(plot_amp, safe_mode=safe_mode)
            #
        else:
            #
            # /// -- Finding data files with CliMAF , and using non-CliMAF code for
            # /// -- generating a simple plot
            #
            print("wmodel=",wmodel)
            #
            # Let CliMAF find datafiles.
            # It will resolve for attributes=*, when there is no amboguity 
            #
            d=ds(**wmodel).explore('resolve')
            datafiles = d.baseFiles()
            # datafiles is a space separated string of filenames, which period
            # intersects the requested period. So, the covered period may be
            # larger or smaller than the requested one.
            #
            # If needed, you may use
            #     d.check(period=True, gap=True)
            # which returns True is there is no gap and that requested
            # period is included
            #
            # Apply a toy code sequence : get and plot first time step
            #
            if datafiles :
                first_file = datafiles.split()[0]
                print("First file=",first_file)
                #
                import xarray as xr
                #
                with xr.open_dataset(first_file) as datas:
                    # You may have to match 'standard' variable name
                    # (as used in datasets_setup.py) with actual
                    # variable name in data file
                    variable_name_in_file = None
                    aliases = {
                        "tas" : ["t2m", "tair"] ,
                        "pr"  : ["precip"]
                    }
                    for varname in [ variable ] + aliases[variable] :
                        if varname in datas.data_vars :
                            variable_name_in_file = varname
                            break
                    if variable_name_in_file is None:
                        print(f"Cannot find variable {variable} in file {filename}")
                        exit
                    #
                    # Get variable for first time step
                    var = datas.data_vars[variable_name_in_file][0] 
                var.plot()
                #
                # ==> -- Create figure file
                # -----------------------------------------------------------------------
                from matplotlib import pyplot as plt
                # Must use a distinct figure file name for each figure
                from random import choices
                from string import ascii_uppercase
                figure_file = ''.join(choices(ascii_uppercase, k=10))+".png"
                print(f"Figure={figure_file} for wmodel=",wmodel)
                plt.savefig(figure_file)
                #
                plt.close()
            else:
                print("Issue accessing datafile for ", wmodel)
                exit
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


# Next settings are usually included in params_xx.py
# ---------------------------------------------------------------------------- >

# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'error'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to True to clean the CliMAF cache before running the diag
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False

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
