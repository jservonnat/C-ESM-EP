
# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Atlas for Earth System Model:                                              - \
# --               - Atlas Explorer                                                              - |
# --               - Atmosphere                                                                  - |
# --               - Blue Ocean (physics)                                                        - |
# --               - White Ocean (sea ice)                                                       - |
# --               - Green Ocean (geochemistry)                                                  - |
# --               - Turbulent Air-Sea Fluxes                                                    - |
# --               - Land Surfaces                                                               - |
# --               - ENSO - CLIVAR                                                               - |
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
# --                                                                                             - |
# --                                                                                             - |
# --      This user interface or parameter file allows providing instructions                    - |
# --      to the atlas_CM.py script.                                                             - |
# --      Each parameter file is (notably) defined by a set of datasets to be compared.          - |
# --      The name of the parameter file should be as follows:                                   - |
# --          params_My_Comparison.py                                                            - |
# --      'My_Comparison' is the name provided by the user to identify the comparison            - |
# --      of simulations. It will be used by the atlas_CM.py to build the name of                - |
# --      the html file.                                                                         - |
# --      The parameter file is used by the atlas script like this:                              - |
# --         > python atlas_CM.py -p params_My_Comparison.py                                     - |
# --                                                                                             - |
# --      To run the atlas, either:                                                              - |
# --          - use job_atlas_computer.job:                                                      - |
# --              * includes setting the environment properly                                    - |
# --              * defining an appropriate cache directory                                      - |
# --              * running the atlas                                                            - |
# --              * can be run either interactively (./job_atlas_computer.job)                   - |
# --                or submitted as a job                                                        - |
# --          - directly with a command line:                                                    - |
# --              * first, setup the environment with ./setenv_atlas_computer                    - |
# --              * Then run the atlas: > python atlas_CM.py [arguments]                         - |
# --      The atlas takes as arguments:                                                          - |
# --          - -p or --params : the parameter file                                              - |
# --          - -s or --season : a season (string) taken by clim_average()                       - |
# --          - --proj : a projection (string) taken by plot()                                   - |
# --          - --index_name : a custom name for the html file                                   - |
# --          - --clean_cache : set to 'True' (string) to clean the CliMAF cache                 - |
# --                                                                                            - /
# --      These additionnal arguments will have the priority over the overall settings         - /
# --      defined in the parameter file, like, for instance, the season).                     - /
# --                                                                                         - /
# --                                                                                        - /
# --                                                                                       - /
# --                                                                                      - /
# ---------------------------------------------------------------------------------------- /





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
proj = 'Satellite' # -> Set to a value taken by the argument 'proj' of plot(): GLOB, NH, SH, NH20, SH30...
#domain = dict(lonmin=0, lonmax=360, latmin=-30, latmax=30) # -> set domain = dict(lonmin=X1, lonmax=X2, latmin=Y1, latmax=Y2) 
domain = {}




# ---------------------------------------------------------------------------- >
# -- Atmosphere diagnostics
# -- This section is based on the same mechanisms as Atlas Explorer; it is
# -- thus possible to use the functionalities (python dictionaries to add options
# -- with a variable)
# ---------------------------------------------------------------------------- >
do_atmos_maps   = True    # -> [LMDZ_SE Atlas] builds a section with a list of standard atmospheric variables (2D maps and zonal means)
my_seasons = ['ANM','DJF','JJA']
atmos_variables_list = ['tas','pr','hfls','hfss','uas','vas','tauu','tauv','psl','hurs',
                   'albt','albs','rsutcs','rsut','rlut','rlutcs',
                   'crest','crelt','crett','cress']

atmos_variables = []
for var in atmos_variables_list:
    for seas in my_seasons:
        atmos_variables.append(dict(variable=var, season=seas, proj='Satellite',mpCenterLonF='-40',options="mpCenterLatF=45|mpSatelliteDistF=3"))
# ---------------------------------------------------------------------------- >


thumbnail_size="400*400"



# -- Some settings -- customization
# ---------------------------------------------------------------------------- >

# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Focus Atlantic - Atmosphere Surface"

# -- Setup a custom css style file
# ---------------------------------------------------------------------------- >
style_file = '/share/fp_template/cesmep_atlas_style_css'
while not os.path.isfile(getcwd()+style_file):
    style_file = '/..'+style_file
style_file = getcwd()+style_file


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

