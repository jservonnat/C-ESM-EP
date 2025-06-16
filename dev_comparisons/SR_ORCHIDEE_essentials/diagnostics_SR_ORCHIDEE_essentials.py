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

from climaf.operators import cscript
from climaf.classes import processDatasetArgs

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Essentials"
# When driven by libIGCM, an additional title may be provided by config.card
if AtlasTitle != "NONE":
    atlas_head_title += " - " + AtlasTitle
else:
    print("No change to title")
print("head_title=", atlas_head_title)

# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)

# -- PLOTTING
# ---------------------------------------------------------------------------------------- #
## -- Period Manager
#if not use_available_period_set:
#    Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
#else:
#    Wmodels = copy.deepcopy(Wmodels_clim)

if thumbnail_size:
    figure_size = thumbnail_size  # possibly defined in params_xx.py
else:
    figure_size = thumbnail_size_global # defined in share/default/default_atlas_settings.py ("300*175")

# ---------------------------------------------------------------------------------------- #
# -- ESSENTIALS
# a) GT Evaluation (IPSLCM6 diff with obs)
# b) verification against mapper results (LMDZOR sims), to be removed after

budget_atlas = True
river_basins = True

# remark (2025-06-10)
# This cscript receive a cens object (ensemble) and therefore, can handle labels by itself. 
# However, the python script must receive a single-quoted string, since CLIMAF passes these labels separated by a $ sign
#path = '/home/sreyes/cesmep/git/dev_comparisons/SR_ORCHIDEE_essentials/scripts/'
path = os.path.dirname(os.path.abspath(__file__)) +'/dev_comparisons/SR_ORCHIDEE_essentials/scripts/'

cscript('river_plot', 'python '+path+'river_discharge.py --variable ${var} --reference ${ref} --ref_label ${ref_label} --simulations "${mmin}" --sim_labels \'${labels}\' --basinmap ${basinmap} --outfig ${out}', format='png')

# ---------------------------------------------------------------------------------------- #
variables_filtered = [v for v in atlas_budget_variables if (v['variable'] in ORCH_Essentials_obs)]

essentials = {  'ORCHIDEE':{'keyword':'project', 'pattern':'IGCM_OUT'} }

for plot_section,filters in essentials.items():

    models_essentials = [ m for m in models if (filters['pattern'] in m[filters['keyword']]) ]
 
    if budget_atlas:
        ## DIFF BETWEEN REF AND SIMS
        kwargs = dict(models=models_essentials, reference=reference, proj=proj, season=season, variables=variables_filtered,
                      section_title=plot_section, domain=domain,
                      custom_plot_params=custom_plot_params,
                      add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                      add_line_of_climato_plots=add_line_of_climato_plots,
                      alternative_dir=alternative_dir, custom_obs_dict=ORCH_Essentials_obs,
                      regridding=regridding,
                      thumbnail_size=thumbnail_size)
        
        if do_parallel:
            index += parallel_section(section_2D_maps, **kwargs)
        else:
            index += section_2D_maps(**kwargs)
    
#        ## REF AND SIMS SIDE BY SIDE
#        kwargs = dict(models=models_essentials, reference=reference, proj=proj, season=season, variables=variables_filtered,
#                      section_title=plot_section, domain=domain,
#                      custom_plot_params=custom_plot_params,
#                      add_product_in_title=add_product_in_title, safe_mode=safe_mode,
#                      alternative_dir=alternative_dir, custom_obs_dict=ORCH_Essential_obs,
#                      thumbnail_size=thumbnail_size)
#        
#        index += section_climato_2D_maps(**kwargs)

# RIVER BASINS
# ---------------------------------------------------------------------------------------- #
    if river_basins:
        print('')
        print('RIVER DISCHARGE')
        print('')

        calias('IGCM_OUT', 'basinmap', filenameVar='sechiba_history')
        calias('IGCM_OUT', 'hydrographs', filenameVar='sechiba_history')
 
        # -- Get the reference, open table
        # ----------------------------------------------------------------------------------------- 
        ref = cfile(ds(**ORCH_Essentials_obs['hydrographs']))
        ref_label = ORCH_Essentials_obs['hydrographs']['customname']

        hydro_paths, labels = [], []
        basinmap = None
        basinmap_flag = True

        Wmodels = copy.deepcopy(models_essentials)
        
        for var_name in ['hydrographs']:
                
            # -- Loop on the models 
            # -----------------------------------------------------------------------------------------
            for model in Wmodels:
                wmodel_output = model.copy()
                wmodel_analyse = {}
                b_output_model, b_analyse_model = {}, {}

                # Get hydrographs dataset
                # remarks (2025-06-10)
                # 1) Since routing is still in development, ORCHIDEE currentlt has three possible variable, depending on the version: 
                # a) v4: 'routing_hydrographs_r', at OUTPUT/DA/*sechiba_routing_r.nc
                # b) v4: an intermediate 'routing_hydrographs_r', at OUTPUT/DA/*sechiba_routing.nc
                # c) previous versions use 'hydrographs', at Analyse/SE/*sechiba_history.nc,               
                # However, for no apparent reason, the latter is still available in ORCH. This has to be solved somehow. 
                #
                # 2) Code below manages this situation by searching directly on the respective folders, by changing wmodel_output attributes. 
                # Filename, on the other hand, is indicated through calias, which has to be redefined every time for a) and b), since variable name is the same.
                # -----------------------------------------------------------------------------------------                

                ## CASE A
                calias('IGCM_OUT', 'routing_hydrographs_r', filenameVar='sechiba_routing_r')

                wmodel_output['variable'] = 'routing_hydrographs_r'
                wmodel_output['DIR'] = 'SRF'
                wmodel_output['OUT'] = 'Output'
                wmodel_output['frequency'] = 'daily'
                wmodel_output = get_period_manager(wmodel_output, diag='ts')
                try:
                    dat = ds(**wmodel_output).explore('resolve')
                except Exception as e:
                    print(f"For {wmodel_output['customname']}, 'routing_hydrographs_r' has not been found at 'sechiba_routing_r'", e)
                
                ## CASE B
                calias('IGCM_OUT', 'routing_hydrographs_r', filenameVar='sechiba_routing')

                if hasattr(dat, 'listfiles') and (dat.listfiles() is None):
                    try:
                        dat = ds(**wmodel_output).explore('resolve')
                    except Exception as e:
                        print(f"For {wmodel_output['customname']}, 'routing_hydrographs_r' has not been found at 'sechiba_routing'", e)
 
                ## CASE C
                # calias for 'hydrographs' is defined above, see line 132
                if hasattr(dat, 'listfiles') and (dat.listfiles() is None):
                    wmodel_analyse  = model.copy()
                    wmodel_analyse['variable'] = 'hydrographs'
                    wmodel_analyse['DIR'] = 'SRF'
                    wmodel_analyse['OUT'] = 'Analyse'
                    wmodel_analyse['frequency'] = 'seasonal'
                    
                    try:
                        dat = ds(**wmodel_analyse).explore('resolve')
                    except Exception as e:
                        print(f"For {wmodel_output['customname']}, 'hydrographs' has not been found at 'sechiba_history'", e)
                
                ## variable management
                if hasattr(dat, 'listfiles') and (dat.listfiles() is not None):
                    print(dat.listfiles())
                    print(cfile(dat))

                    hydro_paths.append(dat)
                    labels.append(wmodel_output['customname'])
                else:
                    print(f"Neither 'hydrographs' nor 'routing_hydrographs_r' has been found for {wmodel_output['customname']}") 
                print('') 
                
                # Get basinmap
                # remark (2025-06-04): this variable is used for representation only 
                # ----------------------------------------------------------------------------------------- 
                if basinmap_flag :
                    bmodel_output = wmodel_output.copy()
                    bmodel_output['variable'] = 'basinmap'

                    try:
                        basin = ds(**bmodel_output).explore('resolve')
                    except Exception as e:
                        print(f"'basinmap' not found in OUTPUT for {wmodel_output['customname']}:", e)

                    if hasattr(basin, 'listfiles') and (basin.listfiles() is None) and bool(wmodel_analyse):
                        bmodel_analyse = wmodel_analyse.copy()
                        bmodel_analyse['variable'] = 'basinmap'
                        
                        try:
                            basin = ds(**bmodel_analyse).explore('resolve')
                        except Exception as e:
                            print(f"'basinmap' not found for {wmodel_output['customname']}:", e)                    
                    
                    if hasattr(basin, 'listfiles') and (basin.listfiles() is not None):
                        basinmap = cfile(basin)
                        basinmap_flag = False

                        print('basinmap found !')
                        print(basinmap)
                        print('')

        # -- Inject python code as script 
        # -----------------------------------------------------------------------------------------
        index += open_table()
        index += open_line(f'River discharge (hydrographs); REF = {ref_label}') + close_line()
        index += open_line()

        if len(hydro_paths) > 0:
            ensemble = dict(zip(labels, hydro_paths))
            data = cens(ensemble, order=labels) 

            try:
                figure_file = river_plot(data, var=var_name, ref=ref, ref_label=ref_label, basinmap=basinmap)
                print("Figure output:", cfile(figure_file))
            except Exception as e:
                print("ERROR when calling river_plots():", e)
            
            # -- Add the plot to the figures line
            # -----------------------------------------------------------------------------------------
            index += cell("", cfile(figure_file), thumbnail="700*600", hover=False, **alternative_dir)
        else:
            pass

        # 
        # ==> -- Close the line
        # -----------------------------------------------------------------------------------------
        index += close_line()
        #
        # ==> -- Close the table before possibly adding a section
        # -----------------------------------------------------------------------------------------
        index += close_table()

# -----------------------------------------------------------------------------------
# --   End
# --
# -----------------------------------------------------------------------------------

