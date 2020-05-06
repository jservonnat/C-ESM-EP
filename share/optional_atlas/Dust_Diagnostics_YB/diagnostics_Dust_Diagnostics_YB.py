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
memory = 20 # in gb

# -- Instructions for the execution of the diagnostics
# ---------------------------------------------------------------------------- >
do_vector_plots = True
do_MSE = True

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Dust Diagnostics (Y. Balkanski)"



# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Wind vectors                                                                       -- #

if do_vector_plots:
    # ==> -- Plug script developed by Yves Balkanski                                       -- #
    # -----------------------------------------------------------------------------------------
    cscript('SurfWindVectorPlotYBalk','ferret -batch -unmapped -script '+main_cesmep_path+'/share/scientific_packages/dust_diags/script_vectors_SurfWinds.jnl ${in_1} ${in_2} ${in_3} ${in_4} ${in_5} "${title}" ; Fprint -o SurfWindsChange.ps metafile.plt ; ps2png SurfWindsChange.ps ; convert SurfWindsChange.png -rotate -90 ${out} ; rm -f SurfWindsChange.ps metafile*.plt SurfWindsChange.png ',
            format='png')
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("Surface Wind Vectors", level=4)
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
    line_title = ''
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
    # -- Reference
    wref = reference.copy()
    wref.update(dict(variable='vitu'))
    wref = get_period_manager(wref, diag='clim')
    wref.pop('variable')
    #
    # -- Get vitu, vitv and pres
    ref_vitu = ds(variable='vitu', **wref).explore('resolve')
    ref_vitv = ds(variable='vitv', **wref).explore('resolve')
    ref_pres = ds(variable='pres', **wref).explore('resolve')

    #
    # -- Loop on the models
    # -----------------------------------------------------------------------------------------
    for model in Wmodels:
            #
            # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
            # -- in the list models, and add the variable
            # -----------------------------------------------------------------------------------------
            wmodel = model.copy()  # - copy the dictionary to avoid modifying the original dictionary
            #
            # ==> -- Apply frequency and period manager
            # -----------------------------------------------------------------------------------------
            # ==> -- They aim at finding the last SE or last XX years available when the user provides
            # ==> -- clim_period='last_SE' or clim_period='last_XXY'...
            # ==> -- and get_period_manager scans the existing files and find the requested period
            # ==> -- !!! Both functions modify the wmodel so that it will point to the requested period
            wmodel.update(dict(variable='vitu'))
            wmodel = get_period_manager(wmodel, diag='clim')
            wmodel.pop('variable')
            #
            # -- Get vitu, vitv and pres
            model_vitu = ds(variable='vitu', **wmodel).explore('resolve')
            model_vitv = ds(variable='vitv', **wmodel).explore('resolve')

            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            title = build_plot_title(wmodel, wref)+' - '+build_period_str(wmodel)  # > returns the model name if project=='CMIP5'
            #                                           otherwise it returns the simulation name
            #                                           It returns the name of the reference if you provide
            #                                           a second argument ('dat1 - dat2')
            #
            # -- Do the plot using SurfWindVectorPlotYBalk
            # -----------------------------------------------------------------------------------------
            tmpplot = SurfWindVectorPlotYBalk(ref_vitu, ref_vitv, ref_pres,
                                              model_vitu, model_vitv,
                                              title=title)
            cdrop(tmpplot)
            #
            # ==> -- Add the plot to the line
            # -----------------------------------------------------------------------------------------
            index += cell("", safe_mode_cfile_plot(tmpplot, safe_mode=safe_mode),
                          thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
    index += close_line() + close_table()



# ---------------------------------------------------------------------------------------- #
# -- MSE diagnostics                                                                    -- #

if do_MSE:
    # ==> -- Plug script developed by Yves Balkanski                                       -- #
    # -----------------------------------------------------------------------------------------
    cscript('compute_MSE','ferret -script '+main_cesmep_path+'/share/scientific_packages/dust_diags/writeMSE_NetCDF.jnl "${in_1}" "${in_2}" "${in_3}" "${in_4}" "${out}" ',
             _var='MSE', format='nc')
    #
    calias('IGCM_OUT', 'ovap', filenameVar='histmth')
    calias('IGCM_OUT', 'temp', filenameVar='histmth')
    calias('IGCM_OUT', 'zhalf', filenameVar='histmth')
    calias('IGCM_OUT', 'zfull', filenameVar='histmth')
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("MSE diagnostics", level=4)
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
    line_title = 'MSE'
    index += start_line(line_title)
    #
    # ==> -- Apply the period_for_diag_manager (not actually needed here)
    # -----------------------------------------------------------------------------------------
    Wmodels = copy.deepcopy(models)
    #
    # -- Reference
    wref = reference.copy()
    wref.update(dict(variable='ovap', OUT='Output'))
    wref = get_period_manager(wref, diag='clim')
    wref.pop('variable')
    #
    # -- Get ovap, temp, zfull, and zhalf
    ref_ovap  = ds(variable='ovap', **wref).explore('resolve')
    ref_temp  = ds(variable='temp', **wref).explore('resolve')
    ref_zfull = ds(variable='zfull', **wref).explore('resolve')
    ref_zhalf = ds(variable='zhalf', **wref).explore('resolve')
    #
    # -- Compute MSE
    #MSE_ref = time_average(compute_MSE(ref_ovap, ref_temp, ref_zfull, ref_zhalf))
    MSE_ref = compute_MSE(ref_ovap, ref_temp, ref_zfull, ref_zhalf)
    #
    # -- Plot MSE reference
    plotref = plot(MSE_ref,
                   color='MPL_Reds',
                   min=200000, max=380000, delta=20000,
                   contours=1,
                   title=build_plot_title(wref, None),
                   gsnLeftString=build_period_str(wref),
                   gsnRightString='MSE (J.kg-1)'
                  )
    #
    # -- Add the plot to the beginning of the line
    index += cell("", safe_mode_cfile_plot(plotref, safe_mode=safe_mode),
                  thumbnail=thumbN_size, hover=hover, **alternative_dir)
    #
    # -- Loop on the models
    # -----------------------------------------------------------------------------------------
    for model in Wmodels:
            #
            # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
            # -- in the list models, and add the variable
            # -----------------------------------------------------------------------------------------
            wmodel = model.copy()  # - copy the dictionary to avoid modifying the original dictionary
            #
            # ==> -- Apply frequency and period manager
            # -----------------------------------------------------------------------------------------
            # ==> -- They aim at finding the last SE or last XX years available when the user provides
            # ==> -- clim_period='last_SE' or clim_period='last_XXY'...
            # ==> -- and get_period_manager scans the existing files and find the requested period
            # ==> -- !!! Both functions modify the wmodel so that it will point to the requested period
            wmodel.update(dict(variable='ovap', OUT='Output'))
            wmodel = get_period_manager(wmodel, diag='clim')
            wmodel.pop('variable')
            #
            # -- Get vitu, vitv and pres
            model_ovap = ds(variable='ovap', **wmodel).explore('resolve')
            model_temp = ds(variable='temp', **wmodel).explore('resolve')
            model_zfull = ds(variable='zfull', **wmodel).explore('resolve')
            model_zhalf = ds(variable='zhalf', **wmodel).explore('resolve')
            #
            # -- Compute MSE
            #MSE_model = time_average( compute_MSE(model_ovap, model_temp, model_zfull, model_zhalf) )
            MSE_model = compute_MSE(model_ovap, model_temp, model_zfull, model_zhalf)
            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            title = build_plot_title(wmodel, wref)      # > returns the model name if project=='CMIP5'
            #                                           otherwise it returns the simulation name
            #                                           It returns the name of the reference if you provide
            #                                           a second argument ('dat1 - dat2')
            #
            # -- Do the plot using SurfWindVectorPlotYBalk
            # -----------------------------------------------------------------------------------------
            tmpplot = plot(minus(MSE_model,MSE_ref),
                           min=-20000, max=20000, delta=2000, color='BlWhRe',
                           title=title,
                           gsnLeftString=build_period_str(wmodel),
                           gsnRightString='MSE (J.kg-1)')
            #
            # ==> -- Add the plot to the line
            # -----------------------------------------------------------------------------------------
            index += cell("", safe_mode_cfile_plot(tmpplot, safe_mode=safe_mode),
                          thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
    index += close_line() + close_table()



# -----------------------------------------------------------------------------------
# --   End
# --
# -----------------------------------------------------------------------------------

