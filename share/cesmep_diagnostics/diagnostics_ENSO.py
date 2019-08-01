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


# ----------------------------------------------
# --                                             \
# --  ENSO - CLIVAR                               \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "ENSO CLIVAR Diagnostics"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- ENSO - CLIVAR diagnostics                                                          -- #
if do_ENSO_CLIVAR:
    print '----------------------------------------------'
    print '-- ENSO - CLIVAR diagnostics                --'
    print '-- do_ENSO_CLIVAR = True                    --'
    print '----------------------------------------------'
    # -- Open the section ---------------------------------------------------------------
    index += section("ENSO - CLIVAR diagnostics", level=4)
    #
    # -- Period Manager
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    print 'Wmodels in ENSO: '
    for wmodel in Wmodels:
        print wmodel
    print '--'
    print '--'
    #
    if do_ENSO_CLIVAR_sstanino3_timeseries:
        # -- Time series of SST anomalies (departures from annual cycle ---------------
        line_title = 'Time Series of Nino3 SST anomalies (departures from annual cycle)'
        index += start_line(line_title)
        # -- Plot the reference
        ref_ENSO_tos = dict(project='ref_ts', period='1870-2010', product='HadISST', frequency='monthly')
        plot_ref_ENSO_ts_ssta = ENSO_ts_ssta(ref_ENSO_tos, safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
        # And loop over the models
        WWmodels = copy.deepcopy(Wmodels)
        for dataset_dict in WWmodels:
            # -- Add table
            dataset_dict.update(dict(variable='tos', table='Omon', grid='gn'))
            dataset_dict = get_period_manager(dataset_dict, diag='ts')
            dataset_dict.pop('variable')
        #
        for model in WWmodels:
            plot_model_ENSO_ts_ssta = ENSO_ts_ssta(model, safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_SSTA_std_maps:
        # -- Standard deviation of SST anomalies (departures from annual cycle ---------------
        # -- Upper band at the top of the section
        line_title = 'Standard Deviation of SST anomalies (deviations from annual cycle)'
        index += start_line(line_title)
        # -- Plot the reference
        plot_ref_ENSO_std_ssta = ENSO_std_ssta(ref_ENSO_tos, safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        # And loop over the models
        for model in WWmodels:
            plot_model_ENSO_std_ssta = ENSO_std_ssta(model, safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_pr_climatology_maps:
        # -- Precipitation climatology over 'ENSO' domain ------------------------------------
        line_title = 'Annual Mean Climatology of Precipitation'
        index += start_line(line_title)
        # -- Plot the reference
        ref_ENSO_pr = variable2reference('pr')  # ; ref_ENSO_pr.update(dict(frequency='seasonal'))
        plot_ref_ENSO_pr_clim = ENSO_pr_clim(ref_ENSO_pr, safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        # And loop over the models
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            model.update(dict(table='Amon', grid='gr'))
            plot_model_ENSO_pr_clim = ENSO_pr_clim(model, safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_tauu_climatology_maps:
        # -- Zonal Wind stress climatology over 'ENSO' domain -------------------------------
        line_title = 'Annual Mean Climatology of Zonal Wind Stress'
        index += start_line(line_title)
        # -- Plot the reference
        ref_ENSO_tauu = variable2reference('tauu')  # ; ref_ENSO_tauu.update(dict(frequency='seasonal'))
        plot_ref_ENSO_tauu_clim = ENSO_tauu_clim(ref_ENSO_tauu, safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        # And loop over the models
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            plot_model_ENSO_tauu_clim = ENSO_tauu_clim(model, safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_linearRegression_dtauu_dsstanino3_maps:
        # -- Map of linear regression coefficients = d(Zonal Wind Stress) / d(SSTA Nino3) ----
        line_title = 'Linear Regression = d(Zonal Wind Stress) / d(SSTA Nino3)'
        index += start_line(line_title)
        # -- Plot the reference
        ref_ENSO_tauu = dict(project='ref_ts', product='ERAInterim', period='2001-2010', variable='tauu',
                             frequency='monthly')
        ref_ENSO_tos = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010',
                            frequency='monthly')
        plot_ref_ENSO_tauuA_on_SSTANino3 = ENSO_linreg_tauuA_on_SSTANino3(ref_ENSO_tauu, ref_ENSO_tos,
                                                                          safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover,
                      **alternative_dir)
        # And loop over the models
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            print 'model in do_ENSO_CLIVAR_linearRegression_dtauu_dsstanino3_maps = ', model
            tos_model = model.copy()
            tos_model.update(variable='tos', table='Omon', grid='gn')
            tauu_model = model.copy()
            tauu_model.update(variable='tauu', table='Amon', grid='gr')
            plot_model_ENSO_tauuA_on_SSTANino3 = ENSO_linreg_tauuA_on_SSTANino3(tauu_model, tos_model,
                                                                                safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover,
                          **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_linearRegression_drsds_dsstanino3_maps:
        # -- Map of linear regression coefficients = d(ShortWave) / d(SSTA Nino3) ----------
        line_title = 'Linear Regression = d(ShortWave) / d(SSTA Nino3)'
        index += start_line(line_title)
        # -- Plot the reference
        ref_ENSO_rsds = dict(project='ref_ts', product='CERES-EBAF-Ed2-7', period='2001-2010', variable='rsds',
                             frequency='monthly')
        ref_ENSO_tos = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010',
                            frequency='monthly')
        plot_ref_ENSO_rsds_on_SSTANino3 = ENSO_linreg_rsds_on_SSTANino3(ref_ENSO_rsds, ref_ENSO_tos,
                                                                        safe_mode=safe_mode)
        index += cell("", plot_ref_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover,
                      **alternative_dir)
        # And loop over the models
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            tos_model = model.copy()
            tos_model.update(variable='tos', table='Omon', grid='gn')
            rsds_model = model.copy()
            rsds_model.update(variable='rsds', table='Amon', grid='gr')
            plot_model_ENSO_rsds_on_SSTANino3 = ENSO_linreg_rsds_on_SSTANino3(rsds_model, tos_model,
                                                                              safe_mode=safe_mode)
            index += cell("", plot_model_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover,
                          **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_SSTA_annualcycles:
        # -- Annual Cycles -----------------------------------------------------------------
        line_title = 'Annual cycles Nino3 (SST, SSTA, Std.dev)'
        index += start_line(line_title)
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            model.update(dict(table='Omon', grid='gn'))
        plot_annual_cycles = plot_ENSO_annual_cycles(WWmodels, safe_mode=safe_mode)
        thumbN_size = "600*350"
        index += cell("", plot_annual_cycles, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        close_line()
        index += start_line('')
        for model in WWmodels:
            one_model_plot_annual_cycles = plot_ENSO_annual_cycles([model], safe_mode=safe_mode)
            index += cell("", one_model_plot_annual_cycles, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        close_line()
        index += close_table()
        #
    if do_ENSO_CLIVAR_longitudinal_profile_tauu:
        # -- Longitudinal profile of Zonal Wind Stress --------------------------------------
        line_title = 'Annual Mean Climatology of Zonal Wind Stress (-5/5N profile)'
        index += start_line(line_title)
        WWmodels = copy.deepcopy(Wmodels)
        for model in WWmodels:
            model.update(dict(table='Amon', grid='gr'))
        plot_tauu_profile = plot_ZonalWindStress_long_profile(WWmodels, safe_mode=safe_mode)
        thumbN_size = "450*400"
        index += cell("", plot_tauu_profile, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        close_line()
        index += start_line('')
        for model in WWmodels:
            one_model_plot_tauu_profile = plot_ZonalWindStress_long_profile([model], safe_mode=safe_mode)
            index += cell("", one_model_plot_tauu_profile, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        close_line()
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


