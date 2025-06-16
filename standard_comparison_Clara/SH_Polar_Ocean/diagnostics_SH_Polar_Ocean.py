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

# - Init html index
# -----------------------------------------------------------------------------------
if atlas_head_title is None :
    atlas_head_title = "SH Polar Ocean"
index = header(atlas_head_title, style_file=style_file)
    

calias('IGCM_OUT', 'iceshelf', filenameVar='grid_T')
calias('IGCM_OUT', 'iceberg', filenameVar='grid_T')
calias('IGCM_OUT', 'rhopoto', filenameVar='grid_T')

# ---------------------------------------------------------------------------------------- #
# -- Plotting the Ocean 2D maps                                                         -- #
if do_ocean_2D_maps:
    print('----------------------------------')
    print('-- Processing Oceanic variables --')
    print('-- do_ocean_2D_maps = True      --')
    print('-- ocean_variables =            --')
    print('-> ', ocean_2D_variables)
    print('--                              --')
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='ocean_2D_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    for model in Wmodels:
        model.update(dict(table='Omon'))
    thumbN_size = thumbnail_polar_size
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=ocean_2D_variables,
                  section_title='Ocean 2D maps', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  regridding=regridding,
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
    if reference == 'default':
        ref = variable2reference(variable, my_obs=custom_obs_dict)
    else:
        if type(reference) is list:
            ref = reference[0]
        else:
            ref = reference
    #
    # -- MLD Diags -> Season and proj
    if not MLD_diags:
        MLD_diags = [('JAS', 'SH30'), ('Annual Max', 'SH30')]
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
        thumbN_size = (
            thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size_global)
        #
        # -- Open the html line with the title
        index += open_table()
        line_title = season+' '+proj+' climato ' + \
            varlongname(variable)+' ('+variable+')'
        index += open_line(line_title) + close_line() + close_table()
        #
        # -- Open the html line for the plots
        index += open_table() + open_line('')
        #
        # --> Plot the climatology vs the reference
        # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
        # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
        wref = ref.copy()
        wref.update(dict(table='Omon', grid='gn'))
        if 'frequency_for_annual_cycle' in wref:
            wref.update(dict(frequency=wref['frequency_for_annual_cycle']))
        ref_MLD_climato = plot_climato(variable, wref, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
        #
        # -- Add the climatology to the line
        index += cell("", ref_MLD_climato, thumbnail=thumbN_size,
                      hover=hover, **alternative_dir)
        #
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            wmodel.update(dict(table='Omon', grid='gn'))
            if 'frequency_for_annual_cycle' in wmodel:
                wmodel.update(
                    dict(frequency=wmodel['frequency_for_annual_cycle']))
            print('wmodel = ')
            MLD_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
            index += cell("", MLD_climato, thumbnail=thumbN_size,
                          hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()


# ---------------------------------------------------------------------------------------- #
# -- Sea Ice polar stereographic maps (sic and sit)                                     -- #
if do_seaice_maps:
    print('----------------------------------------------')
    print('-- Sea Ice Concentration and Thickness Maps --')
    print('-- do_seaice_maps = True                    --')
    print('----------------------------------------------')
    # -- Open the section and an html table
    index += section("Sea Ice Concentration and Thickness (SH)", level=4)
    #
    # -- Sea Ice Diags -> Season and Pole
    if not sea_ice_diags:
        sea_ice_diags = [('February', 'SH'), ('September', 'SH')]
    #
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    # -- Add table
    for model in Wmodels:
        model.update(dict(table='SImon', grid='gn'))
    #
    # -- Loop on the sea ice diags: region and season
    for sea_ice_diag in sea_ice_diags:
        season = sea_ice_diag[0]
        proj = sea_ice_diag[1]
        #
        # -- Sea Ice Concentration ---------------------------------------------------
        variable = 'sic'
        # -- Check which reference will be used:
        #       -> 'default' = the observations that we get from variable2reference()
        #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
        if type(reference) is list:
            ref = reference[0]
        else:
            ref = reference
        if reference == 'default':
            ref = variable2reference(variable, my_obs=custom_obs_dict)
        else:
            ref.update(dict(table='SImon', grid='gn'))
        # -> Sea Ice climatos
        # -- Line Title
        line_title = proj+' '+season+' climatos ' + \
            varlongname(variable)+' ('+variable+')'
        # -- Open the line for the plots
        index += start_line(line_title)
        #
        # -- Loop on the models (in order to add the results to the html line)
        if not use_available_period_set:
            Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel:
                wmodel.update(
                    dict(frequency=wmodel['frequency_for_annual_cycle']))
            #
            # -- Do the plot
            SI_climato = plot_sic_climato_with_ref(variable, wmodel, ref, season, proj,
                                                   custom_plot_params=custom_plot_params, safe_mode=safe_mode)
            # -- And add to the html line
            index += cell("", SI_climato, thumbnail=thumbnail_polar_size,
                          hover=hover, **alternative_dir)
            #
            #
        index += close_line()
        #
        # --> Sea Ice thickness climato ----------------------------------------------
        variable = 'sit'
        # -- Title of the line
        line_title = proj+' '+season+' climato ' + \
            varlongname(variable)+' ('+variable+')'
        # -- Open the line for the plots
        index += start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel:
                wmodel.update(
                    dict(frequency=wmodel['frequency_for_annual_cycle']))
            #
            # -- Add the table
            wmodel['table'] = 'SImon'
            wmodel['grid'] = 'gn'
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index = index + \
                cell("", SIT_climato, thumbnail=thumbnail_polar_size,
                     hover=hover, **alternative_dir)
            #
        index += close_line()+close_table()

        # --> Sea Ice thickness climato ----------------------------------------------
        variable = 'sivolu'
        # -- Title of the line
        line_title = proj+' '+season+' climato ' + \
            varlongname(variable)+' ('+variable+')'
        # -- Open the line for the plots
        index += start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            wmodel.update(dict(table='SImon', grid='gn'))
            #
            if 'frequency_for_annual_cycle' in wmodel:
                wmodel.update(
                    dict(frequency=wmodel['frequency_for_annual_cycle']))
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index = index + \
                cell("", SIT_climato, thumbnail=thumbnail_polar_size,
                     hover=hover, **alternative_dir)
            #
        index += close_line()+close_table()
        
        
##############################


if do_bottomTS_maps:
    #
    # -- Declaration des scripts
    cscript('Tbot_script','python script_Tbot.py ${in_1} ${in_2} ${out}', _var='T_bottom')
    cscript('Sbot_script','python script_Sbot.py ${in_1} ${out}', _var='S_bottom')
    #
    print('----------------------------------------------')
    print('-- Bottom ocean properties Maps --')
    print('-- do_bottomTS_maps = True                    --')
    print('----------------------------------------------')
    # -- Open the section and an html table
    index += section("Bottom ocean properties (SH)", level=4)
    #
    # -- Bottom Ocean Diags -> Season and Pole
    #if not bottom_ocean_diags:
    bottom_ocean_diags = [('ANM', 'SH60')] #, ('JAS', 'SH30'), ('DJF', 'SH30')]
    #
    # -- Period Manager
    if not use_available_period_set:
        Wmodels = period_for_diag_manager(models, diag='clim')
    else:
        Wmodels = copy.deepcopy(Wmodels_clim)
    #

    for bottom_ocean_diag in bottom_ocean_diags:
        #
        # start line!
        #
        season = bottom_ocean_diag[0]
        proj = bottom_ocean_diag[1]
        #
        # -- 1. Reference
        # -- Check which reference will be used:
        #       -> 'default' = the observations that we get from variable2reference()
        #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
        variable = 'T_bottom'
        #ref = variable2reference(variable, my_obs=custom_obs_dict)
        #ref = ds(**custom_obs_dict[variable])

        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = (thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size_global)

        # -- Open the html line with the title
        index += open_table()
        line_title = season+' '+proj+' climato ' + varlongname(variable)+' ('+variable+')'
        index += open_line(line_title) + close_line() + close_table()
        #
        # -- Open the html line for the plots
        index += open_table() + open_line('')

        ref = ds(**custom_obs_dict[variable])
        #plot de la reference
        #wref = cfile(ref, deep=True)
        ref_Tbot_plot= plot(ref, proj=proj, color='cmocean_thermal', min=-3, max=2, delta=0.5, offset=-273.15)
        ref_Tbot_plot_file = cfile(ref_Tbot_plot)
        # -- Add the climatology to the line
        #index += cell("", ref_Tbot_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        index += cell("", ref_Tbot_plot_file, thumbnail=thumbN_size, hover=hover, **alternative_dir)


        # -- 2. Boucle models
        for model in Wmodels:
            
            wmodel = model.copy()
    
            wmodel.update(dict(table='Omon', grid='gn'))
            print(wmodel)
            #wmodel.update(dict(mesh_hgr='/data/cburgard/PREPARE_FORCING/PREPARE_CAVITY_MASKS/raw/eORCA1.4.3_OpenSeas_OpenAllCav_ModStraights/eORCA1.4.3_OpenSeas_OpenAllCav_ModStraights_mesh_mask.nc'))
            
            # -- get period manager -> we use thetao to find the available period
            wmodel['variable'] = 'thetao'
            wmodel = get_period_manager(wmodel, diag='clim')
            #
            thetao_wmodel = wmodel.copy()                                                                                            
            thetao_wmodel['variable'] = 'thetao'                                                                                     
            thetao = ds(**thetao_wmodel) 
            
            so_wmodel = wmodel.copy()                                                                                                
            so_wmodel['variable'] = 'so'                                                                                             
            so = ds(**so_wmodel)   
            
            # -- T_bottom
            Tbot = Tbot_script(thetao, so)
            print('file Tbot '+cfile(Tbot))
            Tbot_clim = clim_average(Tbot, 'ANM')
            print('file Tbot_clim '+cfile(Tbot_clim))
            
            #fixed_fields('regrid',('mesh_mask.nc','/data/igcmg/database/grids/eORCA1.2_mesh_mask.nc'))
            
            Tbot_rg = regrid(Tbot_clim, ref, option='remapbil')
            print('file Tbot_rg '+cfile(Tbot_rg))
            diff = fsub(Tbot_rg, ref)
            print('file diff '+cfile(diff))
            
            #Tbot_rg = regrid(Tbot_clim, ref)  # Regrid mod to match obs
            #diff = Tbot_rg - ref
            diff_Tbot_plot= plot(diff, proj=proj, color='MPL_coolwarm', min=-5, max=5, delta=1)
            #diff_Tbot_plot_file = cfile(diff_Tbot_plot)
            index += cell("", safe_mode_cfile_plot(diff_Tbot_plot, safe_mode=safe_mode), thumbnail=thumbN_size, hover=hover, **alternative_dir)                                                                                                              
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()      

#####################



do_old=False
if do_old:
	print('----------------------------------------------')
	print('-- Bottom ocean properties Maps --')
	print('-- do_bottomTS_maps = True                    --')
	print('----------------------------------------------')
	# -- Open the section and an html table
	index += section("Bottom ocean properties (SH)", level=4)	
	
	# -- Bottom Ocean Diags -> Season and Pole
	#if not bottom_ocean_diags:
	bottom_ocean_diags = [('ANM', 'SH30')] #, ('JAS', 'SH30'), ('DJF', 'SH30')]
	#
	# -- Period Manager
	if not use_available_period_set:
		Wmodels = period_for_diag_manager(models, diag='bottom_ocean_maps')
	else:
		Wmodels = copy.deepcopy(Wmodels_clim)
	# -- Add table
	for model in Wmodels:
		model.update(dict(table='Omon', grid='gn'))
		
		thetao = ds(variable = 'thetao', **model)
		so = ds(variable = 'so', **model)
		rhopoto = ds(variable = 'rhopoto', **model)
		
		cscript('Tbot_script','python script_Tbot.py ${in_1} ${in_2} ${out}', _var='T_bottom')     
		Tbot = Tbot_script(thetao, so)
		
		cscript('Sbot_script','python script_Sbot.py ${in_1} ${out}', _var='S_bottom')
		Sbot = Sbot_script(so)
		
		#cscript('rhobot_script','python script_rhobot.py ${in_1} ${in_2} ${out}', _var='rhopot_bottom')
		#rhobot = rhobot_script(rhopoto, so)
		## -- template de prise en compte d'obs
		
	# -- Loop on the bottom ocean diags: region and season
	for bottom_ocean_diag in bottom_ocean_diags:
		season = bottom_ocean_diag[0]
		proj = bottom_ocean_diag[1]
		proj = 'GLOB'
		#
		# -- Bottom temperature ---------------------------------------------------
		variable = 'T_bottom'
		# -- Check which reference will be used:
		#       -> 'default' = the observations that we get from variable2reference()
		#       -> or a dictionary pointing to a CliMAF dataset (without the variable)
		if reference == 'default':
			ref = variable2reference(variable, my_obs=custom_obs_dict)
		else:
			if type(reference) is list:
				ref = reference[0]
			else:
				ref = reference
		
		# -- Control the size of the thumbnail -> thumbN_size
		thumbN_size = (thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size_global)
		
		# -- Open the html line with the title
		index += open_table()
		line_title = season+' '+proj+' climato ' + varlongname(variable)+' ('+variable+')'
		index += open_line(line_title) + close_line() + close_table()
		#
		# -- Open the html line for the plots
		index += open_table() + open_line('')
		#
		# --> Plot the climatology vs the reference
		# -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
		# -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
		wref = ref.copy()
		wref.update(dict(table='Omon', grid='gn'))
		if 'frequency_for_annual_cycle' in wref:
			wref.update(dict(frequency=wref['frequency_for_annual_cycle']))
		ref_Tbot_climato = plot_climato(variable, wref, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
		#
		# -- Add the climatology to the line
		index += cell("", ref_Tbot_climato, thumbnail=thumbN_size,
                      hover=hover, **alternative_dir)
        #
		for model in Wmodels:
			# -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
			# -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
			wmodel = model.copy()
			wmodel.update(dict(table='Omon', grid='gn'))
			if 'frequency_for_annual_cycle' in wmodel:
				wmodel.update(dict(frequency=wmodel['frequency_for_annual_cycle']))
			print('wmodel = ')
			Tbot_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
			index += cell("", Tbot_climato, thumbnail=thumbN_size,
                          hover=hover, **alternative_dir)
                          
        # -- Close the line and the table of the climatos
		close_line()
        #
        # -- Close the table
		index += close_table()

	#derive('IGCM_OUT','T_bottom','Tbot_script','thetao','so')
	#T_bottom = ds(variable = 'T_bottom', **req_dict)
	
	

        
# ---
# dat = ds(...)
# anncyc : Annual cycle (dat)
# cscript('monoperatuer','python ...'
# res = monoperateur (Anncyc)


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
