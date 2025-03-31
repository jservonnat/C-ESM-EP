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
clog("debug")

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
### atlas_head_title = "Reprobus simple"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print('---------------------------------')
print('-- Running Atlas Explorer for REPROBUS      --')
print('--                             --')

if do_my_own_diag:
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    print("THUMBNAIL")
    print(thumbN_size)

    # ==> General options for REPROBUS chemistry species 
    dict_plotting_specs = {'BrONO2': dict(y='log', scale="10^12", min=0.5, max=7, delta=0.5,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'BrOx': dict(y='log', scale="10^12", min=1, max=15, delta=1,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'CH4': dict(y='log', scale="10^6", min=0.1, max=1.6, delta=0.1, scale_aux="10^6",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'Cl2O2': dict(y='log', scale="10^12", min=2, max=20, delta=2,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'ClONO2': dict(y='log', scale="10^11", min=2, max=30, delta=2,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'ClOx': dict(y='log', scale="10^11", min=1, max=13, delta=1,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'H2': dict(y='log', scale="10^7", min=2, max=14, delta=1,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'H2Orep': dict(y='log', scale="10^5", min=0.1, max=1, delta=0.1, scale_aux="10^5",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'H2O': dict(y='log', scale="10^5", min=0.1, max=1, delta=0.1, scale_aux="10^5",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'H2SO4': dict(y='log', scale="10^10", min=1, max=10, delta=0.5,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'HCl': dict(y='log', scale="10^9", min=0.2, max=3.0, delta=0.2, scale_aux="10^9",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'HNO3': dict(y='log', scale="10^9", min=1, max=14, delta=1,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'N2O': dict(y='log', scale="10^7", min=0.2, max=2.8, delta=0.2,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'NOx': dict(y='log', scale="10^9", min=2, max=18, delta=2,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'O3': dict(y='log', scale="10^6", min=0.75, max=11.25, delta=0.75, scale_aux="10^6",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'OX': dict(y='log', scale="10^6", min=1, max=10, delta=1,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'ta': dict(y='log', min=175, max=325, delta=10,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'ua': dict(y='log', min=-80, max=80, delta=10,
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude"),
                           'default': dict(y='log', scale="1",
                                      options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude")

                          }

    # ==> Obs info for several species
    dict_var_obs_names = {'reprobus_name': ['project_name', 'obs_name'],
                          'ta': ['ECMWF_data_t', 't'],
                          'ua': ['ECMWF_data_u', 'u'],
                          'O3': ['HALOE_data_chimie', 'O3'],
                          'HCl': ['HALOE_data_chimie', 'HCl'],
                          'CH4': ['HALOE_data_chimie', 'CH4'],
                          'H2Orep': ['HALOE_data_chimie', 'H2O']
                         }

    
    # Récupération du modèle pour créer ensuite le dataset spécifique à REPROBUS
    dico=models[-1]
    dico.pop('ts_period',None)
    dico.pop('clim_period',None)
    dico.pop('customname',None)
    dico.pop('ENSO_ts_period',None)
    dico.pop('mesh_hgr',None)
    dico.pop('gridfile',None)
    dico.pop('varname_area',None)
    dico['DIR']='CHM'

    
    # Boucle principale sur les variables (divisées par familles) 
    for atmos_family, atmos_variables_list in atmos_variable_dict.items():
        line_title_atmos_family = '--- '+atmos_family+' family ---'
        index += section(line_title_atmos_family, level=1)
        
        for atmos_variable in atmos_variables_list:
            print('atmos_variable :', atmos_variable)
            # Maj variable
            dico['variable']=atmos_variable
            
            line_title_atmos_variable = 'Climato for '+atmos_variable
            index += section(line_title_atmos_variable, level=3)
            

            ### Test only for O3 with obs
            # obs
            if with_obs:
                data_project = dict_var_obs_names[atmos_variable][0]
                pathfilename_data = my_projects[data_project][0]
                print("We use obs: ",data_project, "located at: ", pathfilename_data)
                if data_project=="ECMWF_data_t" or data_project=="ECMWF_data_u":
                    cproject(data_project)
                    dataloc(project=data_project, organization='generic', url=pathfilename_data)
                elif data_project=="HALOE_data_chimie":
                    ds_data = fds(pathfilename_data, variable=dict_var_obs_names[atmos_variable][1], period='fx')
                    cfile(ds_data)
            
            # plot
            plotting_specs = dict_plotting_specs[atmos_variable]
            units = "("+plotting_specs['scale'].replace("^", "^-")+")"
            for my_period in atmos_periods:
                line_title_period = 'Period: '+my_period
                index += section(line_title_period, level=2)
                # ==> Dataset
                my_ds = ds(period=my_period,**dico)
                line_title_seasons = 'Seasons'
                index += section(line_title_seasons, level=5)
                for season in atmos_seasons:
                    # ==> clim average
                    my_ds_clim = clim_average(my_ds, season)
                    my_ds_clim = zonmean(my_ds_clim)
                    plot_title = atmos_variable+' '+units+' - '+season+' '+my_period

                    if with_obs:
                        if data_project=="HALOE_data_chimie":
                            my_ds_obs_clim = (clim_average(ds_data, season))
                        else:
                            my_ds_obs_clim = zonmean(clim_average(ds_data, season))
                        plot_map3 = clop.plot(my_ds_clim, my_ds_obs_clim, title=plot_title, y='log', scale=10e6,min=7.5, max=112.5, delta=7.5, scale_aux="10^6", options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.75|cnMaxLevelValF=11.25|cnLevelSpacingF=0.75|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'") #tmYLLabels=(/'1000','100','10','1','0.1'/)
                        cfile(plot_map3)
                        index += cell("",safe_mode_cfile_plot(plot_map3, safe_mode=safe_mode),
                              thumbnail=thumbN_size, hover=hover, **alternative_dir)
                    else:
                    #plot_map = clop.plotLF(my_ds_clim, title=plot_title, var_1=atmos_variable, **plotting_specs)
                    #cfile(plot_map)
                    #index += cell("",safe_mode_cfile_plot(plot_map, safe_mode=safe_mode),
                    #          thumbnail=thumbN_size, hover=hover, **alternative_dir)
#                          res@tmYLMode="Explicit"
#      res@tmYLValues=10^(ispan(-1,3,1))    ; 0.1 to 1000 hPa, log step
#      res@tmYLLabels= "" + res@tmYLValues
                        plot_map2 = clop.plot(my_ds_clim, title=plot_title, y='log', scale=10e6, options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude")
                        cfile(plot_map2)
                        index += cell("",safe_mode_cfile_plot(plot_map2, safe_mode=safe_mode),
                              thumbnail=thumbN_size, hover=hover, **alternative_dir)
                        plot_map3 = clop.plot(my_ds_clim, title=plot_title, y='log', scale=10e6, options="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'") #|tmYLValues=(/1000,100,10,1,0.1/) #tmYLLabels=(/'1000','100','10','1','0.1'/)
                        cfile(plot_map3)
                        index += cell("",safe_mode_cfile_plot(plot_map3, safe_mode=safe_mode),
                              thumbnail=thumbN_size, hover=hover, **alternative_dir)






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


