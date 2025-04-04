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
    if thumbnail_size:
        thumbN_size = thumbnail_size
    else:
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
        sea_ice_diags = [('F', 'SH'), ('September', 'SH')]
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
