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
# --  My very own diagnostics                     \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "For Julie"


verbose='debug'
safe_mode = False


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)

# ==> -- Start section
# -----------------------------------------------------------------------------------------
index += section("Inter-member spread", level=4)
thumbN_size = thumbnail_size_global

# ==> -- Open the html line with the title
# -----------------------------------------------------------------------------------------
index += open_table()
line_title = 'Std tos - 2000-2010 climatology'
index+=start_line(line_title)

period='2000-2010'

# -- Request dictionary
req_dict = dict(project='CMIP6', model='IPSL-CM6A-LR', experiment='historical', period=period, realization='*')

# -- Build the ensemble for tos
tos_ens = ds(variable='tos', table='Omon', **req_dict).explore('ensemble')

# -- Compute climatologies
clim_tos_ens = clim_average(tos_ens, 'ANM')

# -- Standard Deviation
std_clim_tos_ens = ccdo_ens(clim_tos_ens, operator='ensstd')

std_plot = plot(std_clim_tos_ens, title='Inter-member std IPSL-CM6A-LR', gsnLeftString=period, gsnRightString='tos', focus='ocean',
                contours=1, color='WhBlGrYeRe')

# -- Amplitude (max-min)
min_clim_tos_ens = ccdo_ens(clim_tos_ens, operator='ensmin')
max_clim_tos_ens = ccdo_ens(clim_tos_ens, operator='ensmax')
amp_clim_tos_ens = minus(max_clim_tos_ens, min_clim_tos_ens)

amp_plot = plot(amp_clim_tos_ens, title='Inter-member Ampl. IPSL-CM6A-LR', gsnLeftString=period, gsnRightString='tos', focus='ocean',
                contours=1, color='WhBlGrYeRe')



index += cell("",safe_mode_cfile_plot(std_plot, safe_mode=safe_mode),
                      thumbnail=thumbN_size, hover=hover, **alternative_dir)

index += cell("",safe_mode_cfile_plot(amp_plot, safe_mode=safe_mode),
                      thumbnail=thumbN_size, hover=hover, **alternative_dir)

#
# ==> -- Close the line and the table for this section
# -----------------------------------------------------------------------------------------
index+=close_line() + close_table()



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


