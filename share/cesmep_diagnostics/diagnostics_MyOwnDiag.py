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

from os import getcwd

# ----------------------------------------------
# --                                             \
# --  My very own diagnostics                     \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
if 'atlas_head_title' not in locals():
    atlas_head_title = "My own diagnostics"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)

# - 1. Make climatology maps by hand (not even using datasets_setup.py)

# - 2. Time series plot of the global tas of all available CMIP5 models

# - 3. Maps of the datasets specified in datasets_setup.py


# ---------------------------------------------------------------------------------------- #
# -- Your own diagnostic script                                                         -- #
# -- This section is a copy of the previous section; it is a good example               -- #
# -- of how to add your own script/diagnostic                                           -- #
# -- The section starting with comments with ==> at the beginning are mandatory to      -- #
# -- build a section in the C-ESM-EP. The comments starting with /// identify code that -- #
# -- is specific to the diagnostic presented here.                                      -- #
if do_my_own_climaf_diag:
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("My own CliMAF diagnostic", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
        thumbN_size = thumbnail_size
    else:
        thumbN_size = thumbnail_size_global
    #
    # ==> -- Open the html line with the title
    # -----------------------------------------------------------------------------------------
    index += open_table()
    line_title = 'Diag #1 = amplitude of the annual cycle'
    index += start_line(line_title)
    #
    # ==> -- Apply the period_for_diag_manager (not actually needed here)
    # -----------------------------------------------------------------------------------------
    Wmodels = copy.deepcopy(models)
    #
    # -- Define plot parameters per variable -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_plot_params = dict(
       tas=dict(contours=1, min=0, max=60, delta=5, color='precip3_16lev'),
       pr=dict(contours=1, min=0, max=30, delta=2, color='precip_11lev', scale=86400.),

    )
    #
    # -- Loop on the variables defined in my_own_climaf_diag_variables -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_variables = ['tas', 'pr']
    for variable in my_own_climaf_diag_variables:
        #
        # -- Loop on the models
        # -----------------------------------------------------------------------------------------
        for model in Wmodels:
            #
            # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
            # -- in the list models, and add the variable
            # -----------------------------------------------------------------------------------------
            wmodel = model.copy()  # - copy the dictionary to avoid modifying the original dictionary
            wmodel.update(dict(variable=variable))  # - add a variable to the dictionary with update
            #
            # ==> -- Apply frequency and period manager
            # -----------------------------------------------------------------------------------------
            # ==> -- They aim at finding the last SE or last XX years available when the user provides
            # ==> -- clim_period='last_SE' or clim_period='last_XXY'...
            # ==> -- and get_period_manager scans the existing files and find the requested period
            # ==> -- !!! Both functions modify the wmodel so that it will point to the requested period
            wmodel = get_period_manager(wmodel, diag='clim')
            #
            # /// -- Get the dataset and compute the annual cycle
            # -----------------------------------------------------------------------------------------
            dat = annual_cycle(ds(**wmodel))
            #
            # -- Compute the amplitude of the annual cycle (max - min)
            # -----------------------------------------------------------------------------------------
            amp = minus(ccdo(dat, operator='timmax'), ccdo(dat, operator='timmin'))
            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            title = build_plot_title(wmodel, None)  # > returns the model name if project=='CMIP5'
            #                                           otherwise it returns the simulation name
            #                                           It returns the name of the reference if you provide
            #                                           a second argument ('dat1 - dat2')
            LeftString = variable
            RightString = build_str_period(wmodel)  # -> finds the right key for the period (period of clim_period)
            CenterString = 'Seas cyc. amplitude'
            #
            # -- Plot the amplitude of the annual cycle
            # -----------------------------------------------------------------------------------------
            plot_amp = plot(amp, title=title, gsnLeftString=LeftString, gsnRightString=RightString,
                            gsnCenterString=CenterString, **my_own_climaf_diag_plot_params[variable])
            #
            # ==> -- Add the plot to the line
            # -----------------------------------------------------------------------------------------
            index += cell("", safe_mode_cfile_plot(plot_amp, safe_mode=safe_mode),
                          thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # ==> -- Close the line and the table for this section
        # -----------------------------------------------------------------------------------------
        index += close_line() + close_table()

# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose = 'debug'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to True to clean the CliMAF cache
clean_cache = False
# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]
# -- Parallel and memory instructions
do_parallel = False

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


