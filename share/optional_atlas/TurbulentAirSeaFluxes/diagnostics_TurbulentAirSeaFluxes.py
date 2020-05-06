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
# --  Turbulent Air Sea Fluxes (GB2015)           \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Turbulent Air Sea Fluxes (GB2015)"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print '---------------------------------'
print '-- Running Atlas Explorer      --'
print '-- atlas_explorer_variables =  --'
print '-> ', atlas_explorer_variables
print '--                             --'


# ---------------------------------------------------------------------------------------- #
# -- Global plot Turbulent fluxes                                                       -- #
if do_GLB_SFlux_maps:
    # -- Open the section and an html table
    index += section("Turbulent Fluxes Annual Mean", level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    # -- Loop on the turbulent fluxes variables
    for variable in TurbFluxes_variables:
        #
        # -- we copy the dictionary to midfy it inside the loop
        wmodel = Wmodels[0].copy()
        #
        # -- Here, we add table='Amon' for the CMIP5 outputs
        wmodel.update(dict(variable=variable,table='Amon'))
        # -- Use the project specs
        if wmodel['project'] in TurbFluxes_project_specs:
           wmodel.update(TurbFluxes_project_specs[wmodel['project']])
        #
        # -- Plot using plot_climato_TurbFlux_GB2015
        # --> Global Annual Mean
        # --> For the simulation
        GLB_plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
        # --> And for the reference
        GLB_plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
        #
        # -- Open the html line with the title
        line_title = 'GLOBAL Annual Mean '+varlongname(variable)+' ('+variable+')'
        index += start_line(line_title)
        #
        # -- Add the plots at the beginning line
        # --> First, the climatology of the reference
        index += cell("", GLB_plot_climato_ref_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
        # --> Then, the climatology of the first model
        index += cell("", GLB_plot_climato_sim_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
        #
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            wmodel = model.copy()
            wmodel.update(dict(variable=variable,table='Amon'))
            GLB_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, climatology='ANM', region='Global', custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
            index=index+cell("", GLB_bias_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
            #
        # -- Close the line
        index+=close_line()+close_table()
        #



# ---------------------------------------------------------------------------------------- #
# -- Tropical (GB2015) Heat Fluxes and Wind stress
if do_Tropics_SFlux_maps:
    # -- Open the section and an html table
    index += section("Turbulent Air-Sea Fluxes Tropics = Gainusa-Bogdan et al. 2015", level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    for variable in TurbFluxes_variables:
        # -- Second Line: Climatos seasons REF + models
        # -- Third line: bias maps
        # -- First line: Climato ANM -----------------------------------------------------
        line_title = varlongname(variable)+' ('+variable+') => Annual Mean Climatology - GB2015, Model and bias map'
        index+=start_line(line_title)
        # -- Plot the reference
        plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        #
        # -- We apply the frequency and time manager once per variable
        # -- For this we create a Wmodels_var per variable
        from copy import deepcopy
        Wmodels_var = deepcopy(Wmodels)
        for model in Wmodels_var:
            model.update(dict(variable=variable))
            # -- Use the project specs
            if model['project'] in TurbFluxes_project_specs:
               model.update(TurbFluxes_project_specs[model['project']])
            if not use_available_period_set:
               frequency_manager_for_diag(model, diag='clim')
               get_period_manager(model)

        # And loop over the models
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable, wmodel, climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_ANM = cpage(fig_lines=[[plot_climato_sim_ANM],[plot_climato_ref_ANM],[plot_bias_ANM]], fig_trim=True, page_trim=True,
                             title=sim.model+' '+sim.simulation+' (vs GB2015)',
                             gravity='NorthWest',
                             ybox=80, pt=30,
                             x=30, y=40,
                             font='Waree-Bold'
                             )
            index+=cell("", safe_mode_cfile_plot(plot_ANM, safe_mode=safe_mode, do_cfile=True), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()
        index+=close_table()
        #
        # -- First line: Climato ANM -----------------------------------------------------
        line_title = varlongname(variable)+' ('+variable+') => Seasonal climatologies (top line) and bias maps (bottom line)'
        index+=start_line(line_title)
        # -- Plot the reference
        plot_climato_ref_DJF = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_MAM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_JJA = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_SON = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        seas_ref_clim_plot = cpage(fig_lines=[[plot_climato_ref_DJF],[plot_climato_ref_MAM],[plot_climato_ref_JJA],[plot_climato_ref_SON]],
                                   fig_trim=True,page_trim=True,
                                   title='Climatology GB2015',
                                   gravity='NorthWest',
                                   ybox=80, pt=30,
                                   x=30, y=40,
                                   font='Waree-Bold'
                                  )
        index+=cell("", safe_mode_cfile_plot(seas_ref_clim_plot, safe_mode=safe_mode, do_cfile=True), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        # And loop over the models
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_DJF = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_MAM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_JJA = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_SON = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            seas_sim_clim_plot = cpage(fig_lines=[[plot_climato_sim_DJF],[plot_climato_sim_MAM],[plot_climato_sim_JJA],[plot_climato_sim_SON]],
                                       fig_trim=True,page_trim=True,
                                       title='Climatology '+sim.model+' '+sim.simulation,
                                       gravity='NorthWest',
                                       ybox=80, pt=30,
                                       x=30, y=40,
                                       font='Waree-Bold'
                                      )
            index+=cell("", safe_mode_cfile_plot(seas_sim_clim_plot, safe_mode=safe_mode), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()

        # -- Third line: Bias maps -----------------------------------------------------
        index+=open_line('')
        # Add a blank space
        index+=cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        # And loop over the models
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_bias_DJF = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_MAM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_JJA = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_SON = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            seas_bias_plot= cpage(fig_lines=[[plot_bias_DJF],[plot_bias_MAM],[plot_bias_JJA],[plot_bias_SON]],fig_trim=True,page_trim=True,
                                  title=sim.model+' '+sim.simulation+' (vs GB2015)',
                                  gravity='NorthWest',
                                  ybox=80, pt=30,
                                  x=30, y=40,
                                  font='Waree-Bold'
                                 )
            if safe_mode==True:
               try:
                  index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
               except:
                  index+=cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            else:
               index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()
        index+=close_table()
        #





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


