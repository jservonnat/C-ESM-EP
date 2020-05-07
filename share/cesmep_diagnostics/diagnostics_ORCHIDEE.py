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
# --  ORCHIDEE                                    \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Energy Budget                                                             -- #
if do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ', variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_bias = []
    for tmpvar in variables_energy_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_energy_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season,
                                                         wvariables_energy_budget_bias,
                                                         'ORCHIDEE Energy Budget, Climato OBS, Bias and model-model '
                                                         'differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
                                                         custom_plot_params=custom_plot_params, shade_missing=True,
                                                         safe_mode=safe_mode, alternative_dir=alternative_dir,
                                                         custom_obs_dict=custom_obs_dict)


if do_ORCHIDEE_Energy_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climobs_bias_maps = True                 --'
    print '-- variables_energy_budget =                                          --'
    print '-> ', variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_bias = []
    for tmpvar in variables_energy_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_energy_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_energy_budget_bias,
                             'ORCHIDEE Energy Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True,
                             safe_mode=safe_mode, add_line_of_climato_plots=add_line_of_climato_plots,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)


if do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ', variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_modelmodel = []
    for tmpvar in variables_energy_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
            wvariables_energy_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_energy_budget_modelmodel,
                             'ORCHIDEE Energy Budget, difference with first simulation', domain=domain,
                             add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
                             custom_plot_params=custom_plot_params, alternative_dir=alternative_dir,
                             custom_obs_dict=custom_obs_dict)


if do_ORCHIDEE_Energy_Budget_diff_with_ref_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_diff_with_ref_maps  = True               --'
    print '-- variables_energy_budget =                                          --'
    print '-> ', variables_energy_budget
    print '--                                                                    --'
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar:
            derive_var_PFT(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps(Wmodels, refsimulation, proj, season, variables_energy_budget,
                             'ORCHIDEE Energy Budget, difference with a reference (climatological month, season)',
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True,
                             safe_mode=safe_mode, add_line_of_climato_plots=add_line_of_climato_plots,
                             custom_obs_dict=custom_obs_dict, custom_plot_params=custom_plot_params,
                             alternative_dir=alternative_dir)


# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Water Budget                                                             -- #
if do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_water_budget =                                          --'
    print '-> ', variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_bias = []
    for tmpvar in variables_water_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_water_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                                                         'ORCHIDEE Water Budget, Climato OBS, Bias and model-model '
                                                         'differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
                                                         shade_missing=True, safe_mode=safe_mode,
                                                         custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict,
                                                         alternative_dir=alternative_dir)


if do_ORCHIDEE_Water_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climobs_bias_maps = True  --'
    print '-- variables_water_budget =                                          --'
    print '-> ', variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_bias = []
    for tmpvar in variables_water_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_water_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                             'ORCHIDEE Water Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True,
                             safe_mode=safe_mode, add_line_of_climato_plots=add_line_of_climato_plots,
                             custom_obs_dict=custom_obs_dict, alternative_dir=alternative_dir)


if do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                         --'
    print '-- do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps = True   --'
    print '-- variables_water_budget =                                           --'
    print '-> ', variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_modelmodel = []
    for tmpvar in variables_water_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
            wvariables_water_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_water_budget_modelmodel,
                             'ORCHIDEE Water Budget, difference with first simulation', domain=domain,
                             add_product_in_title=add_product_in_title, custom_plot_params=custom_plot_params,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
                             shade_missing=True, safe_mode=safe_mode, alternative_dir=alternative_dir)


if do_ORCHIDEE_Water_Budget_climatology_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climatology_maps = True                  --'
    print '-- variables_water_budget =                                          --'
    print '-> ', variables_water_budget
    print '--                                                                    --'
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
            model.update(dict(DIR='SBG'))
    index += section_climato_2D_maps(Wmodels, None, proj, season, variables_water_budget,
                                     'ORCHIDEE Water Budget, climatologies', domain=domain,
                                     custom_plot_params=custom_plot_params, add_product_in_title=add_product_in_title,
                                     safe_mode=safe_mode, alternative_dir=alternative_dir,
                                     custom_obs_dict=custom_obs_dict, thumbnail_size=thumbnail_size)


# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Carbon Budget                                                             -- #
if do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ', variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_bias = []
    for tmpvar in variables_carbon_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_carbon_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
            model.update(dict(DIR='SBG'))
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season,
                                                         wvariables_carbon_budget_bias,
                                                         'ORCHIDEE Carbon Budget, Climato OBS, Bias and model-model'
                                                         ' differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
                                                         shade_missing=True, safe_mode=safe_mode,
                                                         custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict,
                                                         alternative_dir=alternative_dir)


if do_ORCHIDEE_Carbon_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climobs_bias_maps = True                 --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ', variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_bias = []
    for tmpvar in variables_carbon_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
            wvariables_carbon_budget_bias.append(tmpvar)
        except:
            print 'No obs for ', tmpvar
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
            model.update(dict(DIR='SBG'))
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_carbon_budget_bias,
                             'ORCHIDEE Carbon Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True,
                             safe_mode=safe_mode, add_line_of_climato_plots=add_line_of_climato_plots,
                             custom_obs_dict=custom_obs_dict, alternative_dir=alternative_dir)


if do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ', variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_modelmodel = []
    for tmpvar in variables_carbon_budget:
        if isinstance(tmpvar, dict):
            ttmpvar = tmpvar['variable']
        else:
            ttmpvar = tmpvar
        if 'PFT' in ttmpvar:
            derive_var_PFT(ttmpvar)
        try:
            cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
            wvariables_carbon_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
            model.update(dict(DIR='SBG'))
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_carbon_budget_modelmodel,
                             'ORCHIDEE Carbon Budget, difference with first simulation', domain=domain,
                             add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
                             custom_plot_params=custom_plot_params, alternative_dir=alternative_dir)


if do_ORCHIDEE_Carbon_Budget_climatology_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climatology_maps = True                  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ', variables_carbon_budget
    print '--                                                                    --'
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
            Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
            model.update(dict(DIR='SBG'))
    index += section_climato_2D_maps(Wmodels, None, proj, season, variables_carbon_budget,
                                     'ORCHIDEE Carbon Budget, climatologies', domain=domain,
                                     custom_plot_params=custom_plot_params, add_product_in_title=add_product_in_title,
                                     safe_mode=safe_mode, alternative_dir=alternative_dir,
                                     custom_obs_dict=custom_obs_dict, thumbnail_size=thumbnail_size)


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


