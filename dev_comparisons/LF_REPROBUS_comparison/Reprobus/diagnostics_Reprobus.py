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

import calendar
import climaf.operators as clop


# ----------------------------------------------
# --                                             \
# --  Atlas Explorer                              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print('---------------------------------')
print('-- Running Atlas Explorer      --')
print('--                             --')


# -- Plotting specific options for chemistry variables --
dict_plotting_specs = {'BrONO2': dict(y='log', scale="10^12", min=0.5, max=7, delta=0.5),
                       'BrOx': dict(y='log', scale="10^12", min=1, max=15, delta=1),
                       'CH4': dict(y='log', scale="10^6", min=0.1, max=1.6, delta=0.1, scale_aux="10^6", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.1|cnMaxLevelValF=1.6|cnLevelSpacingF=0.1|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'Cl2O2': dict(y='log', scale="10^12", min=2, max=20, delta=2),
                       'ClONO2': dict(y='log', scale="10^11", min=2, max=30, delta=2),
                       'ClOx': dict(y='log', scale="10^11", min=1, max=13, delta=1),
                       'H2': dict(y='log', scale="10^7", min=2, max=14, delta=1),
                       'H2Orep': dict(y='log', scale="10^5", min=0.1, max=1, delta=0.1, scale_aux="10^5", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.1|cnMaxLevelValF=1|cnLevelSpacingF=0.1|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'H2O': dict(y='log', scale="10^5", min=0.1, max=1, delta=0.1, scale_aux="10^5", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.1|cnMaxLevelValF=1|cnLevelSpacingF=0.1|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'H2SO4': dict(y='log', scale="10^10", min=1, max=10, delta=0.5),
                       'HCl': dict(y='log', scale="10^9", min=0.2, max=3.0, delta=0.2, scale_aux="10^9", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.2|cnMaxLevelValF=3.0|cnLevelSpacingF=0.2|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'HNO3': dict(y='log', scale="10^9", min=1, max=14, delta=1),
                       'N2O': dict(y='log', scale="10^7", min=0.2, max=2.8, delta=0.2),
                       'NOx': dict(y='log', scale="10^9", min=2, max=18, delta=2),
                       'O3': dict(y='log', scale="10^6", min=0.75, max=11.25, delta=0.75, scale_aux="10^6", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.75|cnMaxLevelValF=11.25|cnLevelSpacingF=0.75|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'OX': dict(y='log', scale="10^6", min=1, max=10, delta=1),
                       'ta': dict(y='log', min=175, max=325, delta=10),
                       'ua': dict(y='log', min=-80, max=80, delta=10),
                       'default': dict(y='log', scale="1"),
                       'general': dict(options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'")
                      }

# -- Observation variables
dict_var_obs_names = {'reprobus_name': ['project_name', 'obs_name'],
                      'ta': ['ECMWF_data_t', 't'],
                      'ua': ['ECMWF_data_u', 'u'],
                      'O3': ['HALOE_data_chimie', 'O3'],
                      'HCl': ['HALOE_data_chimie', 'HCl'],
                      'CH4': ['HALOE_data_chimie', 'CH4'],
                      'H2Orep': ['HALOE_data_chimie', 'H2O']
                     }


# -- REPROBUS obs projects
my_projects = {'definitions': ['pathfilename', 'frequency'],
               'ECMWF_data_t': ['/ccc/work/cont003/gen0826/fallettl/OBS_data/t_merged_all.nc',
                                       ""],
               'ECMWF_data_u': ['/ccc/work/cont003/gen0826/fallettl/OBS_data/ECMWF/u_merged_all.nc',
                                       ""],
               'HALOE_data_chimie': ['/ccc/work/cont003/gen0826/fallettl/OBS_data/HALOE/haloe_lat_climat.nc',
                                       ""]
              }



if do_my_own_diag:
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    #index += section("My own CliMAF diagnostic for "+atmos_simulation, level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    print("THUMBNAIL")
    print(thumbN_size)

    
    # Récupération du modèle pour créer ensuite le dataset
    dico=models[-1]
    dico.pop('ts_period',None)
    dico.pop('clim_period',None)
    dico.pop('customname',None)
    dico.pop('ENSO_ts_period',None)
    dico.pop('mesh_hgr',None)
    dico.pop('gridfile',None)
    dico.pop('varname_area',None)
    dico['DIR']='CHM'


    for atmos_family, atmos_variables_list in atmos_variable_dict.items():
        line_title_atmos_family = '--- '+atmos_family+' family ---'
        index += section(line_title_atmos_family, level=1)
        
        for atmos_variable in atmos_variables_list:
            print('\n--- ATMOS VARIABLE: ', atmos_variable, ' ---')
            # Maj variable
            dico['variable']=atmos_variable
            
            line_title_atmos_variable = 'Climato for '+atmos_variable
            index += section(line_title_atmos_variable, level=3)
            
            # Obs data
            if atmos_variable in dict_var_obs_names.keys():
                with_obs = True
                data_project = dict_var_obs_names[atmos_variable][0]
                pathfilename_data = my_projects[data_project][0]
                print("We use obs: ",data_project, "located at: ", pathfilename_data)
                if data_project=="ECMWF_data_t" or data_project=="ECMWF_data_u":
                    cproject(data_project)
                    dataloc(project=data_project, organization='generic', url=pathfilename_data)
                elif data_project=="HALOE_data_chimie":
                    ds_data = fds(pathfilename_data, variable=dict_var_obs_names[atmos_variable][1], period='fx')
                    cfile(ds_data)
                else:
                    with_obs = False
                    print("!!! No data for comparaison !!! We nevertheless continue.")
            else:
                with_obs = False
                print("!!! No data for comparaison !!! We nevertheless continue.")

            
            # specs for the plot
            try: plotting_specs = dict(dict_plotting_specs[atmos_variable],**dict_plotting_specs["general"])
            except:
                print('Variable ', atmos_variable, 'not in the dict of plotting specs. Use of default.')
                plotting_specs = dict(dict_plotting_specs['default'],**dict_plotting_specs["general"])

            # units
            try: units = "("+plotting_specs['scale'].replace("^", "^-")+")"
            except: units = ""

            for my_period in atmos_periods:
                line_title_period = 'Period: '+my_period
                index += section(line_title_period, level=2)
                # ==> Dataset
                my_ds = ds(period=my_period,**dico)
                if with_obs and data_project!="HALOE_data_chimie":
                    print("with_obs and data_project!=HALOE_data_chimie")
                    try:
                        ds_data = ds(project=data_project, period=my_period, variable=dict_var_obs_names[atmos_variable][1])
                        cfile(ds_data)
                    except:
                        with_obs=False

                line_title_seasons = 'Seasons'
                index += section(line_title_seasons, level=5)
                for season in atmos_seasons:
                    # ==> clim average
                    my_ds_clim = clim_average(my_ds, season)
                    if no_post_proc:
                        my_ds_clim = zonmean(my_ds_clim)
                    
                    # ==> -- Making the plot
                    plot_title = atmos_variable+' '+units+' - '+season+' '+my_period
                    #plot_save_png = output_plots_path+"plot_"+atmos_variable+'_'+my_period+"_"+season+".png"
                    if with_obs:
                        if data_project=="HALOE_data_chimie":
                            my_ds_obs_clim = (clim_average(ds_data, season))
                        else:
                            my_ds_obs_clim = zonmean(clim_average(ds_data, season))
                        plot_title = plot_title+' - with '+dict_var_obs_names[atmos_variable][0].split('_')[0]
                        #plot_map = clop.plotLF(my_ds_clim, my_ds_obs_clim, title=plot_title, var_1=atmos_variable, **plotting_specs)
                        plot_map = clop.plot(my_ds_clim, my_ds_obs_clim, title=plot_title, **plotting_specs)
                    else:
                        #plot_map = clop.plotLF(my_ds_clim, title=plot_title, var_1=atmos_variable, **plotting_specs)
                        plot_map = clop.plot(my_ds_clim, title=plot_title, **plotting_specs)
                    #cfile(plot_map, target=plot_save_png)
                    cfile(plot_map)
                    index += cell("",safe_mode_cfile_plot(plot_map, safe_mode=safe_mode),
                              thumbnail=thumbN_size, hover=hover, **alternative_dir)

                line_title_seasons = 'Months'
                index += section(line_title_seasons, level=5)
                for month in atmos_months:
                    month_name = calendar.month_name[month]
                    # ==> clim average
                    my_ds_clim = clim_average(my_ds, month)
                    if no_post_proc:
                        my_ds_clim = zonmean(my_ds_clim)

                    # ==> -- Making the plot
                    plot_title = atmos_variable+' '+units+' - '+month_name+' '+my_period
                    #plot_save_png = output_plots_path+"plot_"+atmos_variable+'_'+my_period+"_"+str(month)+"-"+month_name+".png"
                    if with_obs:
                        if data_project=="HALOE_data_chimie":
                            my_ds_obs_clim = clim_average(ds_data, month)
                        else:
                            my_ds_obs_clim = zonmean(clim_average(ds_data, month))
                        plot_title = plot_title+' - with '+dict_var_obs_names[atmos_variable][0].split('_')[0]
                        #plot_map = clop.plotLF(my_ds_clim, my_ds_obs_clim, title=plot_title, var_1=atmos_variable, **plotting_specs)
                        plot_map = clop.plot(my_ds_clim, my_ds_obs_clim, title=plot_title, **plotting_specs)
                    else:
                        #plot_map=clop.plotLF(my_ds_clim, title=plot_title, var_1=atmos_variable, **plotting_specs)
                        plot_map=clop.plot(my_ds_clim, title=plot_title, **plotting_specs)
                    #cfile(plot_map, target=plot_save_png)
                    cfile(plot_map)
                    index += cell("",safe_mode_cfile_plot(plot_map, safe_mode=safe_mode),
                              thumbnail=thumbN_size, hover=hover, **alternative_dir)




# -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
#kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
#              section_title='Reprobus plots', domain=domain, custom_plot_params=custom_plot_params,
#              add_product_in_title=add_product_in_title, safe_mode=safe_mode,
#              add_line_of_climato_plots=add_line_of_climato_plots,
#              alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
#              regridding=regridding,
#              thumbnail_size=thumbN_size)
#if do_parallel:
#    index += parallel_section(section_2D_maps, **kwargs)
#else:
#    index += section_2D_maps(**kwargs)

   
#if atlas_explorer_climato_variables:
#    # -- Update kwargs accordingly
#    kwargs.pop('add_line_of_climato_plots')
#    kwargs.update(dict(variables=atlas_explorer_climato_variables, section_title='Reprobus plots'))
#    #
#    if do_parallel:
#        index += parallel_section(section_climato_2D_maps, **kwargs)
#    else:
#        index += section_climato_2D_maps(**kwargs)


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


