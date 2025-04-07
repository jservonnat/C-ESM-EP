#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------------------ \
# --                                                                                                    - \
# --                                                                                                     - \
# --      Scientific diagnostics for the                                                                  - \
# --          CliMAF Earth System Model Evaluation Platform                                               - |
# --                                                                                                      - |
# --      diagnostics_${component}.py                                                                     - |
# --        ==> add html code to 'index' (initialized with 'header')                                      - |
# --            using the CliMAF html toolbox (start_line, cell, close_table... )                         - |
# --            to create your own atlas page                                                             - |
# --                                                                                                      - |
# --      Developed within the ANR Convergence Project                                                    - |
# --      CNRM GAME, IPSL, CERFACS                                                                        - |
# --      Contributions from CNRM, LMD, LSCE, NEMO Group, ORCHIDEE team.                                  - |
# --      Based on CliMAF: WP5 ANR Convergence, S. Senesi (CNRM) and J. Servonnat (LSCE - IPSL)           - |
# --                                                                                                      - |
# --      J. Servonnat, S. Senesi, L. Vignon, MP. Moine, O. Marti, E. Sanchez, F. Hourdin,                - |
# --      I. Musat, M. Chevallier, J. Mignot, M. Van Coppenolle, J. Deshayes, R. Msadek,                  - |
# --      P. Peylin, N. Vuichard, J. Ghattas, F. Maignan, A. Ducharne, P. Cadule,                         - |
# --      P. Brockmann, C. Rousset, J.Y. Perterschmitt                                                    - |
# --                                                                                                      - |
# --      Contact: jerome.servonnat@lsce.ipsl.fr                                                          - |
# --                                                                                                      - |
# --  See the documentation at: https://github.com/jservonnat/C-ESM-EP/wiki                               - |
# --                                                                                                      - |
# --                                                                                                      - /
# --  Note: you can actually use an empty datasets_setup                                                 - /
# --  and an empty params_${component}.py, and set everything from here                                 - /
# --                                                                                                   - /
# --                                                                                                  - /
# ---------------------------------------------------------------------------------------------------- /

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division


# ----------------------------------------------
# --                                             \
# --  Atlas Explorer                              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
if atlas_head_title is None:
    atlas_head_title = "AtlasExplorer"
    # When driven by libIGCM, an additional title may be provided by config.card
    if AtlasTitle != "NONE":
        atlas_head_title += " - " + AtlasTitle


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)



# -- PLOTTING
# ---------------------------------------------------------------------------------------- #
## -- Period Manager
#if not use_available_period_set:
#    Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
#else:
#    Wmodels = copy.deepcopy(Wmodels_clim)

#if thumbnail_size:
#    thumbN_size = thumbnail_size
#else:
#    thumbN_size = None

if thumbnail_size:
    figure_size = thumbnail_size  # possibly defined in params_xx.py
else:
    figure_size = thumbnail_size_global # defined in share/default/default_atlas_settings.py

## -- diff with obs
## ---------------------------------------------------------------------------------------- #
## -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
#kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
#              section_title='Atlas Explorer', domain=domain, custom_plot_params=custom_plot_params,
#              add_product_in_title=add_product_in_title, safe_mode=safe_mode,
#              add_line_of_climato_plots=add_line_of_climato_plots,
#              alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
#              regridding=regridding,
#              thumbnail_size=thumbN_size)
#if do_parallel:
#    index += parallel_section(section_2D_maps, **kwargs)
#else:
#    index += section_2D_maps(**kwargs)


# SWARMPLOTS + METRICS BY REGION
# ---------------------------------------------------------------------------------------- #
# retrieve data objects
# compute  
# + for each observation, its annual cycle (regridded into mapper's regional grid reference) and
#   * simulation's annual cycle (regridded into mapper's regional grid reference)
#     - branch my code and return the png
#     - add the png to index cell 
#   * build the index line
# ---------------------------------------------------------------------------------------- #
index += open_table()  # This allows to have all figures nicely aligned across figure lines

# Create a first table line with a single element : some sub-title
index += line(['Diag #1 = diff by hand'])

# preliminary step = copy the models dictionary to avoid modifying the 
# entries in the (global) models dict. `models` is usually set by datasets_setup.py
Wmodels = copy.deepcopy(models)

my_own_climaf_diag_plot_params = dict(
    tas=dict(contours=1, min=0, max=60, delta=5, color='precip3_16lev'),
    pr=dict(contours=1, min=0, max=30, delta=2, color='precip_11lev', scale=86400.),
)

for var in atlas_explorer_variables:

    index += open_line()  # all figures for one variable will lay on a single line
    #
    # -- Loop on the models 
    # -----------------------------------------------------------------------------------------
    for model in Wmodels:
        #
        # -----------------------------------------------------------------------------------------
        wmodel = model.copy()  # - copy the dictionary to avoid modifying the original dictionary
        if isinstance(var, str):
            wmodel["variable"] = var  # - add a variable to the dictionary
            variable = var
        if isinstance(var, dict):
            wmodel.update(var)
            variable = var["variable"]
        
        # Avoid ambiguity on some attributes (depends on datasets_setup.py content and variable)
#        if wmodel["project"] == "CMIP6" :
#            wmodel["table"] = "Amon"
#            wmodel["grid"] = "gr"
#        if wmodel["project"] == "CMIP5" :
#            wmodel["realm"] = "atmos"
        #
        # ==> -- Apply period manager
        # -----------------------------------------------------------------------------------------
        # ==> -- It aims at finding the last SE or last XX years available when the user provides
        # ==> -- clim_period='last_SE' or clim_period='last_XXY'... in model attributes.
        # ==> -- get_period_manager scans the existing files and find the requested period
        # ==> -- !!! This modifies wmodel so that it will point to the requested period

        wmodel = get_period_manager(wmodel, diag='clim')
        #
        if True : #using_climaf :
            # /// -- Get the dataset and compute the annual cycle using CliMAF functions
            # -----------------------------------------------------------------------------------------
            dat = clim_average(ds(**wmodel), season)
            #
            # /// -- Get the references
            # -----------------------------------------------------------------------------------------
            print('variable2reference(variable)',variable2reference(variable))
            ref = clim_average(ds(**variable2reference(variable, my_obs=custom_obs_dict)), season)
            #
            # -- Regrid model on ref
            # -----------------------------------------------------------------------------------------
           # # 1. Get path/filename of the destination grid file
           # grid_file = './grid_file.nc'

           # # 2. Quick regrid (a tester!!)
           # rgrd_dat = ccdo(dat, operator='remapbil,'+grid_file)
           # # Syntaxe cdo:
           # # cdo remapbil,gridfile.nc in.nc out.nc
           # # cdo operator in.nc out.nc
           # # cscript(...)

           # # 3. Avec fds
           # grid = fds(grid_file, variable='vargrid', period='fx')
           # rgrd_dat = regrid(dat, grid)

           # # 4. Avec grille CDO
           # rgrd_dat = regridn(dat, cdogrid='r720x360', option='remapdis')

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
                             gsnCenterString=CenterString)#,
                             #**my_own_climaf_diag_plot_params[variable])
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


# -----------------------------------------------------------------------------------
# --   End
# --
# -----------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------ \
# --                                                                                                    - \
# --                                                                                                     - \
# -- main_C-ESM-EP.py will provide you with:                                                              - |
# --   - the list 'models' defined in datasets_setup.py, as well as 'reference'                           - |
# --     if use_available_period_set == True, it means that you also have Wmodels_clim and Wmodels_ts     - |
# --     that correspond to 'models' with periods for climatologies and time series (respectively)        - |
# --     that have already been found (if you used arguments like 'last_10Y', 'first_30Y', 'full' or '*') - |
# --   - alternative_dir: to be used as an argument to cell(..., altdir=alternative_dir)                  - |
# --   - the parameters from params_${component}.py (safe_mode,                                           - |
# --   - the cesmep modules in share/cesmep_modules                                                       - |
# --   - the default values from share/default/default_atlas_settings.py                                  - |
# --                                                                                                      - /
# -- Note: you can actually use an empty datasets_setup                                                  - /
# -- and an empty params_${component}.py, and set everything from here                                  - /
# --                                                                                                   - /
# --                                                                                                  - /
# ---------------------------------------------------------------------------------------------------- /
