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
# --  Atlas Explorer                              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "NEMO general diagnostics"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Ocean 2D maps                                                         -- #
if do_ocean_2D_maps:
    print '----------------------------------'
    print '-- Processing Oceanic variables --'
    print '-- do_ocean_2D_maps = True      --'
    print '-- ocean_variables =            --'
    print '-> ',ocean_2D_variables
    print '--                              --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_2D_maps')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    for model in Wmodels: model.update(dict(table='Omon'))
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=ocean_2D_variables,
                  section_title='Ocean 2D maps', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  thumbnail_size=thumbN_size,
                  ocean_variables=ocean_variables)
    if do_parallel:
       index += parallel_section(section_2D_maps, **kwargs)
    else:
       index += section_2D_maps(**kwargs)




# ---------------------------------------------------------------------------------------- #
# -- MLD maps: global, polar stereographic and North Atlantic                           -- #
# -- Winter and annual max                                                              -- #
if do_MLD_maps:
    # -- Open the section and an html table
    index += section("Mixed Layer Depth", level=4)
    #
    # -- MLD
    variable = 'mlotst'
    #
    # -- Check which reference will be used:
    #       -> 'default' = the observations that we get from variable2reference()
    #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
    if reference=='default':
       ref = variable2reference(variable, my_obs=custom_obs_dict)
    else:
       ref = reference
    #
    # -- MLD Diags -> Season and proj
    if not MLD_diags: MLD_diags=[('ANM','GLOB'),('JFM','GLOB'),('JAS','GLOB'),('JFM','NH40'),('Annual Max','NH40'),('JAS','SH30'),('Annual Max','SH30')]
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='MLD_maps')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    #
    # -- Loop on the MLD diags
    for MLD_diag in MLD_diags:
        season = MLD_diag[0]
        proj = MLD_diag[1]
        #
        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = (thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size_global)
        #
        # -- Open the html line with the title
        index += open_table()
        line_title = season+' '+proj+' climato '+varlongname(variable)+' ('+variable+')'
        index+=open_line(line_title) + close_line()+ close_table()
        #
            # -- Open the html line for the plots
        index += open_table() + open_line('')
        #
        # --> Plot the climatology vs the reference
        # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
        # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
        wref = ref.copy()
        wref.update(dict(table='Omon', grid='gn'))
        if 'frequency_for_annual_cycle' in wref: wref.update( dict(frequency = wref['frequency_for_annual_cycle']) )
        ref_MLD_climato   = plot_climato(variable, wref, season, proj, custom_plot_params=custom_plot_params,
                                         safe_mode=safe_mode, regrid_option='remapdis')
        #
        # -- Add the climatology to the line
        index += cell("", ref_MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            wmodel.update(dict(table='Omon', grid='gn'))
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            print 'wmodel = '
            MLD_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
            index += cell("",MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()



# ---------------------------------------------------------------------------------------- #
# -- Wind stress curl maps: global, Pacific and North Atlantic                          -- #
# -- Winter and annual max                                                              -- #
if do_curl_maps:
    # -- Open the section and an html table
    index += section("Wind stress Curl", level=4)
    #
    # -- Zonal and meridional components of the wind stress
    tauu_variable = 'tauuo'
    tauv_variable = 'tauvo'
    curl_variable = 'socurl'
    #
    # -- Wind stress curl Diags -> Season and proj
    if not curl_diags:
       curl_diags= [ dict(name='Global, annual mean', season='ANM',proj='GLOB', thumbNsize='400*300'),
                  dict(name='NH, annual mean', season='ANM',proj='NH40', thumbNsize='400*400'),
                  dict(name='North Atlantic, annual mean', season='ANM', domain=dict(lonmin=-80,lonmax=0,latmin=30,latmax=90), thumbNsize='400*300'),
                  dict(name='Tropical Atlantic, annual mean', season='ANM', domain=dict(lonmin=-90,lonmax=0,latmin=-10,latmax=45), thumbNsize='400*300'),
                  dict(name='North Pacific, annual mean', season='ANM', domain=dict(lonmin=120,lonmax=240,latmin=30,latmax=75), thumbNsize='500*250'),
                  dict(name='North Atlantic, JFM', season='JFM', domain=dict(lonmin=-80,lonmax=0,latmin=30,latmax=90), thumbNsize='400*300'),
                 ]
    domains = dict( ATL=dict(lonmin=-80,lonmax=0,latmin=20,latmax=90),
                    PAC=dict(lonmin=-80,lonmax=0,latmin=20,latmax=90),
                  )
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='2D_maps')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    #
    # -- Loop on the wind stress curl diags
    for curl_diag in curl_diags:
        season = curl_diag['season']
        proj = 'GLOB'
        if 'proj' in curl_diag:
           proj = curl_diag['proj']
        domain = {}
        if 'domain' in curl_diag:
           domain = curl_diag['domain']
        #
        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = curl_diag['thumbNsize']
        #
        # -- Open the html line with the title
        index += open_table()
        line_title = 'Wind stress Curl climato '+curl_diag['name']
        index+=start_line(line_title)
        #
        # -- Loop on the models (add the results to the html line)
        if not use_available_period_set:
           Wmodels = period_for_diag_manager(models, diag='2D_maps')
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            #
            # -- Compute the curl with tauu and tauv
            curl_climato = plot_curl(tauu_variable, tauv_variable, curl_variable, wmodel, season, proj, domain=domain, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
            index += cell("",curl_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()




# ---------------------------------------------------------------------------------------- #
# -- Plotting the time series of spatial indexes                                        -- #
if do_ATLAS_TIMESERIES_SPATIAL_INDEXES:

    index+=section("Time-serie of Spatial Indexes",level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TS')
    else:
       Wmodels = copy.deepcopy(Wmodels_ts)
    #
    # Loop on variables,one per line
    for variable in ts_variables:
        # -- Loop on the regions
        for region in ts_basins:
            # -- Open the line with the title
            index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+')')
                #
            # -- Loop on the models
            if not use_available_period_set:
               Wmodels = period_for_diag_manager(models, diag='ocean_basin_timeseries')
            for model in Wmodels:
                if variable=="tos" and region=="GLO":
                   print("=> comparison with HadISST")
                   basin_index=index_timeserie(model, variable, region=region, obs=hadisst_ts, prang=None, safe_mode=safe_mode)
                if variable=="zos" and region=="GLO":
                   print("=> comparisin with AVISO-L4")
                   basin_index=index_timeserie(model, variable, region=region, obs=aviso_ts, prang=None, safe_mode=safe_mode)
                else:
                   basin_index=index_timeserie(model, variable, region=region, obs=None, prang=None, safe_mode=safe_mode)
                index+=cell("", basin_index, thumbnail=thumbsize_TS, hover=hover, **alternative_dir)
            index += close_line() + close_table()


# ---------------------------------------------------------------------------------------- #
# -- Plotting the MOC Diagnostics                                                       -- #
if do_ATLAS_MOC_DIAGS:

    index+=section("MOC Diagnoses",level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TS')
    else:
       Wmodels = copy.deepcopy(Wmodels_ts)
    #
    # List of regions (i.e. basins)
    for region in MOC_basins:
        #
            # -- Loop on models
        # --> Vertical levels
        index+=start_line(title_region(region)+" MOC (Depth)")
        #
        if not use_available_period_set:
           Wmodels = period_for_diag_manager(models, diag='MOC_slice')
        #
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='lin')
            index+=cell("", basin_moc_slice, thumbnail=thumbsize_MOC_slice, hover=hover, **alternative_dir)
        index += close_line() + close_table()
        # -- Model levels
        index+=start_line(title_region(region)+" MOC (model levels)")
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='index')
            index+=cell("", basin_moc_slice, thumbnail=thumbsize_MOC_slice, hover=hover, **alternative_dir)
        index += close_line() + close_table()
    #
    # -- MOC Profile at 26N vs Rapid
    #index+=open_table()
    ## -- Title of the line
    #index+=open_table() + open_line("MOC Profile at 26N vs RAPID") + close_line()+ close_table()
    ## -- Loop on models
    #index += open_table() + open_line('')
    #Wmodels = period_for_diag_manager(models, diag='MOC_profile')
    #for model in Wmodels:
    #    moc_profile_26N_vs_rapid = moc_profile_vs_obs(model, obs=rapid_ac, region='ATL', latitude=26.5,
    #                                                 y=y, safe_mode=safe_mode)
    #    index+=cell("", moc_profile_26N_vs_rapid, thumbnail=thumbsize_MAXMOC_profile, hover=hover, **alternative_dir)
    #index += close_line() + close_table()
    ## -- Close the section
    #
    if do_TS_MOC:
       # List of latitudes
       if not llats: llats=[26.5,40.,-30.]
       for latitude in llats:
           # -- Line title
           index+=start_line("maxMoc at latitude "+str(latitude))
           # -- Loop on models
           if not use_available_period_set:
              Wmodels = period_for_diag_manager(models, diag='MOC_timeseries')
           for model in Wmodels:
               wmodel = model.copy()
               if 'frequency' in wmodel:
                  if wmodel['frequency'] in ['seasonal','annual_cycle']:
                     wmodel.update(dict(frequency = 'monthly', period = model['clim_period']))
               maxmoc_tserie = maxmoc_time_serie(wmodel, region='ATL', latitude=latitude, safe_mode=safe_mode)
               index+=cell("", maxmoc_tserie, thumbnail=thumbsize_MOC_TS, hover=hover, **alternative_dir)
           index+=close_line()+close_table()



# ---------------------------------------------------------------------------------------- #
# -- Plotting the Vertical Profiles of T and S                                          -- #
if do_ATLAS_VERTICAL_PROFILES:

    index+=section("Vertical Profiles",level=4)
    # Loop on variables, one per line
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_vertical_profiles')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    for variable  in VertProf_variables:
        for obs in VertProf_obs:
            for region in VertProf_basins:
                    # -- Line title
                index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
                for model in Wmodels:
                    if region=="GLO":
                       basin_profile = vertical_profile(model, variable, obs=obs, region=region,
                                                        box=None, safe_mode=safe_mode)
                    else:
                       #mpm_to_improve: pour l'instant, pas de comparaison aux obs dans les sous-basins
                       basin_profile = vertical_profile(model, variable, obs=None, region=region,
                                                        box=None, safe_mode=safe_mode)
                    index+=cell("", basin_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
                index+=close_line()+close_table()
        # -- Line title
        index+=start_line('Gibraltar '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
        for model in Wmodels:
            gibr_profile = vertical_profile(model, variable, obs=obs, region='GLO',
                                            box=boxes.get("gibraltar"), safe_mode=safe_mode)
            index+=cell("", gibr_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
        index+=close_line()+close_table()


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Zonal Mean Slices                                                     -- #
if do_ATLAS_ZONALMEAN_SLICES:

    # Loop over variables
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_zonalmean_sections')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels: model.update(dict(table='Omon', grid='gn'))
    kwargs = dict(models=Wmodels,reference=reference,zonmean_slices_variables=zonmean_slices_variables,
                  zonmean_slices_basins=zonmean_slices_basins,zonmean_slices_seas=zonmean_slices_seas,
                  custom_plot_params=custom_plot_params,  custom_obs_dict=custom_obs_dict,
                  safe_mode=safe_mode, y=y, thumbsize_zonalmean=thumbsize_zonalmean, do_parallel=do_parallel,
                  hover=hover, alternative_dir=alternative_dir)
    if do_parallel:
       index += parallel_section(section_zonalmean_slices, **kwargs)
    else:
       index += section_zonalmean_slices(**kwargs)



# ---------------------------------------------------------------------------------------- #
# -- Plotting the Drift Profiles (Hovmoller)                                            -- #
if do_ATLAS_DRIFT_PROFILES:

    index+=section("Drift Profiles (Hovmoller)",level=4)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_drift_profiles')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    Wmodels = period_for_diag_manager(models, diag='ocean_drift_profiles')
    # Loop over variables
    for variable in drift_profiles_variables:
        for region in drift_profiles_basins:
            index+=start_line('Drift vs T0: '+title_region(region)+' '+varlongname(variable)+' ('+variable+')')
            for model in Wmodels:
                basin_drift = hovmoller_drift_profile(model, variable, region=region, y=y, safe_mode=safe_mode)
                index+=cell("", basin_drift, thumbnail=thumbsize_TS, hover=hover, **alternative_dir)
            index+=close_line()+close_table()




# ----------------------------------------------
# --                                             \
# --  White Ocean                                 \
# --  Sea Ice                                     /
# --                                             /
# --                                            /
# ---------------------------------------------




# ---------------------------------------------------------------------------------------- #
# -- Plotting the Sea Ice volume annual cycle of both hemispheres                       -- #
if do_seaice_annual_cycle:
   print '--------------------------------------------------'
   print '-- Computing Sea Ice Volume of both hemispheres --'
   print '-- do_seaice_annual_cycle = True                --'
   print '--------------------------------------------------'
   # -- Open the section and an html table
   index += section("Sea Ice volume - annual cycle", level=4)
   index += open_table()
   #
   # -- Period Manager
   if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='sea_ice_volume_annual_cycle')
   else:
       Wmodels = copy.deepcopy(Wmodels_clim)
   # -- Add table
   for model in Wmodels: model.update(dict(table='SImon', grid='gn'))
   #
   # -- Do the plots and the availability check
   siv_NH = plot_SIV(Wmodels, 'NH', safe_mode=safe_mode)
   siv_SH = plot_SIV(Wmodels, 'SH', safe_mode=safe_mode)
   #
   # -- Gather the figures in an html line
   index+=open_line('Sea Ice Volume (km3))')+\
                     cell("", siv_NH, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)+\
                     cell("", siv_SH, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
   close_line()
   #
   # -- Close this table
   index += close_table()



# ---------------------------------------------------------------------------------------- #
# -- Sea Ice polar stereographic maps (sic and sit)                                     -- #
if do_seaice_maps:
    print '----------------------------------------------'
    print '-- Sea Ice Concentration and Thickness Maps --'
    print '-- do_seaice_maps = True                    --'
    print '----------------------------------------------'
    # -- Open the section and an html table
    index += section("Sea Ice Concentration and Thickness (NH and SH)", level=4)
    #
    # -- Sea Ice Diags -> Season and Pole
    if not sea_ice_diags: sea_ice_diags=[('March','NH'),('September','NH'),('March','SH'),('September','SH')]
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels: model.update(dict(table='SImon', grid='gn'))
    #
    # -- Loop on the sea ice diags: region and season
    for sea_ice_diag in sea_ice_diags:
        season = sea_ice_diag[0]
        proj = sea_ice_diag[1]
            #
        # -- Sea Ice Concentration ---------------------------------------------------
        variable='sic'
        # -- Check which reference will be used:
        #       -> 'default' = the observations that we get from variable2reference()
        #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
        if reference=='default':
           ref = variable2reference(variable, my_obs=custom_obs_dict)
        else:
           ref = reference
           ref.update(dict(table='SImon', grid='gn'))
        # -> Sea Ice climatos
            # -- Line Title
        line_title = proj+' '+season+' climatos '+varlongname(variable)+' ('+variable+')'
        # -- Open the line for the plots
        index+= start_line(line_title)
        #
        # -- Loop on the models (in order to add the results to the html line)
        if not use_available_period_set:
           Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Do the plot
            SI_climato = plot_sic_climato_with_ref(variable, wmodel, ref, season, proj,
                                                   custom_plot_params=custom_plot_params, safe_mode=safe_mode)
            # -- And add to the html line
            index += cell("", SI_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
            #
        index+=close_line()
        #
        # --> Sea Ice thickness climato ----------------------------------------------
        variable='sit'
        # -- Title of the line
        line_title = proj+' '+season+' climato '+varlongname(variable)+' ('+variable+')'
            # -- Open the line for the plots
        index+=start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Add the table
            wmodel['table'] = 'SImon'
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index=index+cell("", SIT_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()+close_table()

        # --> Sea Ice thickness climato ----------------------------------------------
        variable='sivolu'
        # -- Title of the line
        line_title = proj+' '+season+' climato '+varlongname(variable)+' ('+variable+')'
            # -- Open the line for the plots
        index+=start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index=index+cell("", SIT_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()+close_table()




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


