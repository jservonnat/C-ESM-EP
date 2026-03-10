#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------ #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division

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
# --  INCA - Zonal Means                          \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------
import climaf.operators as clop


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print('--------------------------------------')
print('-- Running Atlas Explorer           --')
print('-- atlas_explorer_variables =       --')
#if 'atmos_variables' in locals():
#    atlas_explorer_variables = atmos_variables
#    print('-- (from atmos_variables in params) --')
#print('-> ', atlas_explorer_variables)
print('--                                  --')


# -- Period Manager
if not use_available_period_set:
    Wmodels = period_for_diag_manager(models, diag='atm_2D_zonmean')
else:
    Wmodels = copy.deepcopy(Wmodels_clim)
#for model in Wmodels:
#    model.update(dict(table='Amon'))


dict_plotting_specs = {'vmrn2o': dict(y='log', scale="10^9", min=0, max=340, delta=20,
                                      option="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'|tmYLLabels=(/'1000','500','100','10','1','0.1'/)", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0|cnMaxLevelValF=340|cnLevelSpacingF=40|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'vmrch4': dict(y='log', scale="10^6", min=0.1, max=1.6, delta=0.1,
                                      option="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'|tmYLLabels=(/'1000','500','100','10','1','0.1'/)", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0.1|cnMaxLevelValF=1.6|cnLevelSpacingF=0.1|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                       'vmro3': dict(y='log', scale="10^6", min=0, max=12, delta=0.75,
                                      option="tiYAxisString=Pressure (hPa)|tiXAxisString=Latitude|tmYLMode='Explicit'|tmYLLabels=(/'1000','500','100','10','1','0.1'/)", aux_options="cnLineLabelsOn=True|cnLineThicknessF=4.0|cnLevelSelectionMode='ManualLevels'|cnMinLevelValF=0|cnMaxLevelValF=12|cnLevelSpacingF=0.75|cnLineLabelPlacementMode='Constant'|tiMainString='Constant'"),
                                      }
dict_var_obs_names = {'inca_name': ['project_name', 'obs_name'],
                          'vmrn2o': ['Satellite', 'value'],
                          'vmrch4': ['HALOE', 'CH4'],
                          'vmro3': ['HALOE', 'O3'],
                          }
# Récupération du modèle pour créer ensuite le dataset
dico=models[-1]
dico.pop('ts_period',None)
#dico.pop('clim_period',None)
dico.pop('customname',None)
dico.pop('ENSO_ts_period',None)
dico.pop('mesh_hgr',None)
dico.pop('gridfile',None)
dico.pop('varname_area',None)
dico['DIR']='CHM'

for atmos_variable in atmos_variables_list:
      print('atmos_variable :', atmos_variable)
      # Maj variable
      dico['variable']=atmos_variable

      line_title_atmos_variable = 'Climato for '+atmos_variable
      index += section(line_title_atmos_variable, level=3)

      # obs
      data_project = dict_var_obs_names[atmos_variable][0]
      pathfilename_data = my_projects[data_project][0]
      print("We use obs: ",data_project, "located at: ", pathfilename_data)
      #cproject(data_project)
      #dataloc(project=data_project, organization='generic', url=pathfilename_data)
      ds_data = fds(pathfilename_data, variable=dict_var_obs_names[atmos_variable][1], period='fx')
      cfile(ds_data)

      # plot
      plotting_specs = dict_plotting_specs[atmos_variable]
      units = "("+plotting_specs['scale'].replace("^", "^-")+")"
      # ==> Dataset
      print('My model is =', models)
      my_period=models[0]['clim_period']
      print('My period is =', my_period)
      my_ds = ds(period=my_period,**dico)
      line_title_seasons = 'Seasons'
      index += section(line_title_seasons, level=5)
      for seas in season:
          # ==> clim average
          my_ds_clim = clim_average(my_ds, seas)
          my_ds_clim = zonmean(my_ds_clim)
          plot_title = atmos_variable+' '+units+' - '+seas+' '+my_period

          my_ds_obs_clim = (clim_average(ds_data, seas))
          plot_map3 = clop.plot(my_ds_clim, my_ds_obs_clim, title=plot_title, y='log', scale=dict_plotting_specs[atmos_variable]['scale'], min=dict_plotting_specs[atmos_variable]['min'], max=dict_plotting_specs[atmos_variable]['max'], scale_aux=dict_plotting_specs[atmos_variable]['scale'], options=dict_plotting_specs[atmos_variable]['option'], aux_options=dict_plotting_specs[atmos_variable]['aux_options'])
          cfile(plot_map3)
          index += cell("",safe_mode_cfile_plot(plot_map3, safe_mode=safe_mode),
                    thumbnail=thumbnail_size, hover=hover, **alternative_dir)






## -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
#kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
#              section_title='INCA - Zonal means vs Satellite', domain=domain, custom_plot_params=custom_plot_params,
#              add_product_in_title=add_product_in_title, safe_mode=safe_mode,
#              add_line_of_climato_plots=add_line_of_climato_plots,
#              regridding=regridding,
#              alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)
#if do_parallel:
#    index += parallel_section(section_2D_maps, **kwargs)
#else:
#    index += section_2D_maps(**kwargs)
#
#   
#if atlas_explorer_climato_variables:
#    # -- Update kwargs accordingly
#    kwargs.pop('add_line_of_climato_plots')
#    kwargs.pop('regridding')
#    kwargs.update(dict(variables=atlas_explorer_climato_variables, section_title='Atmosphere Zonal mean Climatologies'))
#    #
#    if do_parallel:
#        index += parallel_section(section_climato_2D_maps, **kwargs)
#    else:
#        index += section_climato_2D_maps(**kwargs)
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


