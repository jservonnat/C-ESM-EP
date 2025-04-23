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

##from climaf.utils import ranges_to_string
##from env.environment import *


# ----------------------------------------------
# --                                             \
# --  MAPS for INCA model                         \
# --                                              /
# --                                             /
# -----------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "INCA - Atmospheric Surface"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
print('------------------------------------')
print('-- Running Atmospheric chemistry  --')
print('--   atlas_explorer_variables =   --')
print('-> ', atlas_explorer_variables)
print('--                                --')
# -- Period Manager
if not use_available_period_set:
    Wmodels = period_for_diag_manager(models, diag='atm_2D_maps')
else:
    Wmodels = copy.deepcopy(Wmodels_clim)
if thumbnail_size:
    thumbN_size = thumbnail_size
else:
    thumbN_size = None

#my_dict_plot_params = {}
#for var in atlas_explorer_variables_list:
#    my_dict_plot_params[var] = {'default':{'color':'BlueWhiteOrangeRed'}, 'bias':{'color':'BlueWhiteOrangeRed'}}
#
#print(my_dict_plot_params)

#my_dict_plot_params = {
#    'vmrn2o': {
#        'default': {'scale': 1e9, 'color': 'WhiteBlueGreenYellowRed', 'contours': 1, 'units': 'ppb'},
#        'full_field': {'color': 'WhViBlGrYeOrRe'},
#        'bias': {'color': 'WhiteBlueGreenYellowRed'},
#        'model_model': {'color': 'WhiteBlueGreenYellowRed'},
#    },
#    'emi_n2o': {
#        'default': {'scale': 86400., 'color': 'WhiteBlueGreenYellowRed', 'contours': 1, 'units': 'kgN2O/m2/y'},
#        'full_field': {'color': 'WhViBlGrYeOrRe' },
#        'bias': {'color': 'WhiteBlueGreenYellowRed'},
#        'model_model': {'color': 'precip_diff_12lev'}
#    },
#}

# -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
              section_title='Atmosphere Surface', domain=domain, custom_plot_params=custom_plot_params,
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
    kwargs.update(dict(variables=atlas_explorer_climato_variables,
                  section_title='Atmospheric Chemistry Climatologies'))
    #
    if do_parallel:
        index += parallel_section(section_climato_2D_maps, **kwargs)
    else:
        index += section_climato_2D_maps(**kwargs)

#dict_std_name = {
#        # -- INCA variables
#    emich4=("Emissions CH4", ""),
#    vmrch4=("Volume Mix Ratio CH4", "vmr ch4"),
#    vmrch4_surf=("Volume Mix Ratio CH4 at the surface", "vmr ch4 surf"),
#    vmrch4850=("Volume Mix Ratio CH4 at 850 hPa", "vmr ch4 at 850 hPa"),
#    vmrch4700=("Volume Mix Ratio CH4 at 700 hPa", "vmr ch4 at 700 hPa"),
#    vmrch4500=("Volume Mix Ratio CH4 at 500 hPa", "vmr ch4 at 500 hPa"),
#    vmrch4200=("Volume Mix Ratio CH4 at 200 hPa", "vmr ch4 at 200 hPa"),
#    emico=("Emissions CO", ""),
#    vmrco=("Volume Mix Ratio CO", "vmr co"),
#    vmrco_surf=("Volume Mix Ratio CO at the surface", "vmr co surf"),
#    vmrco850=("Volume Mix Ratio CO at 850 hPa", "vmr co at 850 hPa"),
#    vmrco700=("Volume Mix Ratio CO at 700 hPa", "vmr co at 700 hPa"),
#    vmrco500=("Volume Mix Ratio CO at 500 hPa", "vmr co at 500 hPa"),
#    vmrco200=("Volume Mix Ratio CO at 200 hPa", "vmr co at 200 hPa"),
#    emin2o=("Emissions N2O", ""),
#    vmrn2o=("Volume Mix Ratio N2O", "vmr n2o"),
#    vmrn2o_surf=("Volume Mix Ratio N2O at the surface", "vmr n2o surf"),
#    vmrn2o850=("Volume Mix Ratio N2O at 850 hPa", "vmr n2o at 850 hPa"),
#    vmrn2o700=("Volume Mix Ratio N2O at 700 hPa", "vmr n2o at 700 hPa"),
#    vmrn2o500=("Volume Mix Ratio N2O at 500 hPa", "vmr n2o at 500 hPa"),
#    vmrn2o200=("Volume Mix Ratio N2O at 200 hPa", "vmr n2o at 200 hPa"),
#    }
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
