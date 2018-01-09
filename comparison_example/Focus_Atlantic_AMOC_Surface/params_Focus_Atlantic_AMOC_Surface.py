# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: AtlasExplorer                                                 - |
# --                                                                                             - |
# --      Developed within the ANR Convergence Project                                           - |
# --      CNRM GAME, IPSL, CERFACS                                                               - |
# --      Contributions from CNRM, LMD, LSCE, NEMO Group, ORCHIDEE team.                         - |
# --      Based on CliMAF: WP5 ANR Convergence, S. Senesi (CNRM) and J. Servonnat (LSCE - IPSL)  - |
# --                                                                                             - |
# --      J. Servonnat, S. Senesi, L. Vignon, MP. Moine, O. Marti, E. Sanchez, F. Hourdin,       - |
# --      I. Musat, M. Chevallier, J. Mignot, M. Van Coppenolle, J. Deshayes, R. Msadek,         - |
# --      P. Peylin, N. Vuichard, J. Ghattas, F. Maignan, A. Ducharne, P. Cadule,                - |
# --      P. Brockmann, C. Rousset                                                               - |
# --                                                                                             - |
# --      Contact: jerome.servonnat@lsce.ipsl.fr                                                 - |
# --                                                                                             - |
# --                                                                                            - /
# --                                                                                           - /
# --------------------------------------------------------------------------------------------- /




# -- Preliminary settings: import module, set the verbosity and the 'safe mode'
# ---------------------------------------------------------------------------- >
from os import getcwd
# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug', intermediate -> 'warning')
verbose='debug'
# -- Safe Mode (set to False and verbose='debug' if you want to debug)
safe_mode = True
# -- Set to 'True' (string) to clean the CliMAF cache
clean_cache = 'False'
# -- routine_cache_cleaning is a dictionary or list of dictionaries provided
#    to crm() at the end of the atlas (for a routine cache management)
routine_cache_cleaning = [dict(access='+20')]



# -- Set the reference against which we plot the diagnostics 
# -- If you set it in the parameter file, it will overrule
# -- the reference set in datasets_setup.py
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
#reference = 'default'




# -- Set the overall season, region and geographical domain
# --> season, region and domain do not overwrite the values that are pre-defined with some diagnostics
# ---------------------------------------------------------------------------- >
season = 'ANM'  # -> Choose among all the possible values taken by clim_average (see help(clim_average)) like JFM, December,...
proj = 'GLOB'   # -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
domain = dict(lonmin=-100,lonmax=20,latmin=25,latmax=90) # -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2)



# ---------------------------------------------------------------------------- >
# -- Atlas Explorer diagnostics
# -- Atlas Explorer is meant to be a simple and flexible way to produce an atlas
# -- on demand.
# -- atlas_explorer_variables is a list of variables, and/or python dictionaries
# -- that allow to pass custom specifs with the variable, like:
# --   - season
# --   - region
# --   - domain
# --   - and various plot parameters taken as argument by plot() (CliMAF operator)
# ---------------------------------------------------------------------------- >
do_atlas_explorer        = True    # -> use atlas_explorer_variables to set your own selection of variables
add_line_of_climato_plots=False

calias('IGCM_OUT', 'hflsevap', 'flat', scale=-1./2.5e6, filenameVar='histmth')

uvs_vector_plot_params = dict(vcRefLengthF=0.001, vcRefMagnitudeF=0.08,
                              vcMinDistanceF=0.025, vcLineArrowColor="black")
tau_vector_plot_params = dict(vcRefLengthF=0.002, vcRefMagnitudeF=0.01,
                              vcMinDistanceF=0.015, vcLineArrowColor="black")

atlas_explorer_variables = [#dict(variable='tos',add_aux_contours=dict(variable='sic',contours=15, aux_options='cnLineThicknessF=10'),
                            #     line_title = 'SST + 0.15 contour Sea Ice conc. (black line)'),
                            #'sos','wfo',
                            'pme',
                            # 'to1000',
                            dict(variable='uas',vectors=dict(u_comp='uas',v_comp='vas', **uvs_vector_plot_params)),
                            dict(variable='vas',vectors=dict(u_comp='uas',v_comp='vas', **uvs_vector_plot_params)),
                            dict(variable='uas', season='DJF', vectors=dict(u_comp='uas',v_comp='vas', **uvs_vector_plot_params)),
                            dict(variable='vas', season='DJF', vectors=dict(u_comp='uas',v_comp='vas', **uvs_vector_plot_params)),
                            dict(variable='tauu', season='ANM', vectors=dict(u_comp='tauu',v_comp='tauv', **tau_vector_plot_params)),
                            dict(variable='tauv', season='ANM', vectors=dict(u_comp='tauu',v_comp='tauv', **tau_vector_plot_params)),
                            dict(variable='tauu', season='DJF', vectors=dict(u_comp='tauu',v_comp='tauv', **tau_vector_plot_params)),
                            dict(variable='tauv', season='DJF', vectors=dict(u_comp='tauu',v_comp='tauv', **tau_vector_plot_params)),
                            #dict(variable='tauuo',vectors=dict(u_comp='tauuo',v_comp='tauvo', **tau_vector_plot_params)),
                            #dict(variable='tauvo',vectors=dict(u_comp='tauuo',v_comp='tauvo', **tau_vector_plot_params)),
                           ]
#atlas_explorer_variables = ['tauuo','tauvo']
#atlas_explorer_climato_variables = [dict(variable='mlotst',season='JFM'), 'socurl', 'curltau', 'sic']
atlas_explorer_climato_variables = ['curltau',
                                    #dict(variable='mlotst',season='JFM',add_aux_contours=dict(variable='sic',contours=15, aux_options='cnLineThicknessF=10')),
                                    #dict(variable='sic',season='JFM',)]
                                   ]
# Biais = 'tos', 'sos', 'uas', 'vas'
# Climatos = 'curltau', 'socurl', 'mlotst', 'sic'
# Rajouter les vecteurs de vent et le contour de glace de mer?

calias('ref_climatos', 'tauuo', 'tauu')
calias('ref_climatos', 'tauvo', 'tauv')
# -- Mixed Layer Depth
#do_MLD_maps            = True    # -> [NEMO Atlas] Maps of Mixed Layer Depth
#MLD_diags=[('JFM','GLOB')]

# -- Wind stress curl
#do_curl_maps = True
#curl_diags= [ dict(name='North Atlantic, annual mean', season='ANM', domain=dict(lonmin=-80,lonmax=0,latmin=30,latmax=90), thumbNsize='400*300')]



#dict_params = dict(focus='land')
#new_atlas_explorer_variables = []
#for elt in atlas_explorer_variables:
#    if not isinstance(elt,dict):
#       new_elt = dict(variable=elt)
#    else:
#       new_elt = elt.copy()
#    new_elt.update(dict_params)


# ---------------------------------------------------------------------------- >




# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Focus North Atlantic for AMOC"

# -- Setup a custom css style file
# ---------------------------------------------------------------------------- >
style_file = '/share/fp_template/cesmep_atlas_style_css'
i=1
while not os.path.isfile(os.getcwd()+style_file):
    print i
    style_file = '/..'+style_file
    if i==3:
       break
    i=i+1
style_file = os.getcwd()+style_file


# -- Add the name of the product in the title of the figures
# ---------------------------------------------------------------------------- >
add_product_in_title = True

# -- Automatically zoom on the plot when the mouse is on it
# ---------------------------------------------------------------------------- >
hover = False

# -- Add the compareCompanion (P. Brockmann)
# --> Works as a 'basket' on the html page to select some figures and
# --> display only this selection on a new page
# ---------------------------------------------------------------------------- >
add_compareCompanion = True


# -- Name of the html file
# -- if index_name is set to None, it will be build as user_comparisonname_season
# -- with comparisonname being the name of the parameter file without 'params_'
# -- (and '.py' of course)
# ---------------------------------------------------------------------------- >
index_name = None


# -- Custom plot params
# -- Changing the plot parameters of the plots
# ---------------------------------------------------------------------------- >
# Load an auxilliary file custom_plot_params (from the working directory)
# of plot params (like atmos_plot_params.py)
from custom_plot_params import dict_plot_params as custom_plot_params
# -> Check $CLIMAF/climaf/plot/atmos_plot_params.py or ocean_plot_params.py
#    for an example/



# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #

