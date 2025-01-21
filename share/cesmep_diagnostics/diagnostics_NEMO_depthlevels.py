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
# --  NEMO depthlevels                            \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------



# - Init html index
# -----------------------------------------------------------------------------------
if atlas_head_title is None :
    atlas_head_title = "Ocean depth levels"
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print('---------------------------------')
print('-- Running Atlas Explorer      --')
print('-- atlas_explorer_variables =  --')
if 'ocean_2D_variables' in locals():
    atlas_explorer_variables = ocean_2D_variables
    print('-- (from ocean_2D_variables in params) --')
print('-> ', atlas_explorer_variables)
print('--                             --')

# -- Period Manager
if not use_available_period_set:
    Wmodels = period_for_diag_manager(models, diag='ocean_2D_maps')
else:
    Wmodels = copy.deepcopy(Wmodels_clim)
if thumbnail_size:
    thumbN_size = thumbnail_size
else:
    thumbN_size = None

# -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
              section_title='Ocean 2D maps', domain=domain, custom_plot_params=custom_plot_params,
              add_product_in_title=add_product_in_title, safe_mode=safe_mode,
              add_line_of_climato_plots=add_line_of_climato_plots,
              alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
              regridding=regridding,
              thumbnail_size=thumbN_size)
if do_parallel:
    index += parallel_section(section_2D_maps, **kwargs)
else:
    index += section_2D_maps(**kwargs)

   
if atlas_explorer_climato_variables:
    # -- Update kwargs accordingly
    kwargs.pop('add_line_of_climato_plots')
    kwargs.pop('regridding')
    kwargs.update(dict(variables=atlas_explorer_climato_variables, section_title='Atlas Explorer Climatologies'))
    #
    if do_parallel:
        index += parallel_section(section_climato_2D_maps, **kwargs)
    else:
        index += section_climato_2D_maps(**kwargs)


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


