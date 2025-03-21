
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

# -- List of simulations: models = [dict(...), dict(...), ...]
# --
# -- Specify the list of 'datasets' (list of python dictionaries) you want to assess with the atlas.
# -- A CliMAF dataset is defined by:
# --      - project: a pre-defined organization of data (ex: CMIP5, IGCM_OUT, EM...)
# --      - simulation: the simulation name
# --      - frequency: monthly, seasonal, yearly...
# --      - period: the time period (if frequency = monthly or yearly)
# --        CliMAF will extract this period from the files in the directory
# --        pointed at by the request
# --      - clim_period: a character string indicating the period over which you want
# --        your climatology (pre-computed, or to be done)
# --        => pre-computed for frequency='seasonal'
# --        => to be done on demand for frequency='monthly'
# --      - ts_period: a character string indicating the period over which you want
# --        your time series
# --
# -- The atlas loops over pre-defined variables. The user doesn't have to define a variable
# -- in the dataset definition.
# --
# -- All other keywords are linked with the projects (see the definition of the projects
# -- for more informations).
# --
# -- Option =
# --   - You can pass a season in the dataset definition (ex: season='DJF'); any season used by clim_average()
# --     This season will have higher priority than the overall season argument (in this param file or
# --     via the command line).
# --
# -- Examples:
# -- CMIP5: dict(project='CMIP5', model='IPSL-CM5A-LR', experiment='historical',
# --             period='1980-2000')
# -- IGCM_OUT:
# --   -> Working on SE on Curie:
# --      dict(project='IGCM_OUT', root='/ccc/store/cont003/gencmip6', login='p86ghatt',
# --           model='LMDZOR', simulation='CL4.3934.L2595', frequency='seasonal', clim_period='2001_2010')
# --   -> Working on TS_MO on Curie:
# --      dict(project='IGCM_OUT', root='/ccc/store/cont003/gencmip6', login='p86ghatt',
# --           model='LMDZOR', simulation='CL4.3934.L2595', frequency='monthly', period='2001_2010')
# --   -> On Ciclad, the default root is the common space (default login is 'fabric');
# --      If your dataset is stored in the /prodigfs/fabric/IGCM_OUT tree, you don't have to pass root and login
# --
# -- From the definition of a dataset it is possible to control the period for a given type of
# -- diagnostic.
# -- You can control:
# --    - period with ${diag}_period
# --    - ts_period with ${diag}_ts_period
# --    - clim_period with ${diag}_clim_period
# -- available values for ${diag}:
# --    - atlas_explorer
# --    - atm_2D_maps
# --    - ocean_2D_maps
# --    - MLD_maps
# --    - ocean_basin_timeseries
# --    - MOC_slice
# --    - MOC_profile
# --    - MOC_timeseries
# --    - ocean_vertical_profiles
# --    - ocean_zonalmean_sections
# --    - ocean_drift_profiles
# --    - sea_ice_volume_annual_cycle
# --    - sea_ice_maps
# --    - ENSO
# --    - ENSO_annual_cycles
# --    - TurbulentAirSeaFluxes
# --    - PISCES_2D_maps
# --    - ORCHIDEE_2D_maps

# ---------------------------------------------------------------------------- >
from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM, atCerfacs
from CM_atlas import *

# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

# -- Set the path to the grids
if onCiclad or onSpirit:
    gridpath = '/data/igcmg/database/grids/'
if atTGCC:
    gridpath = '/ccc/work/cont003/igcmg/igcmg/Database/grids/'
if atCNRM:
    gridpath = '/cnrm/est/COMMON/C-ESM-EP/grids/'

# -- Setup the models list
# --> case atCNRM:
if atCNRM:
    models = [

        dict(project='CMIP5', model='CNRM-CM5', experiment='piControl',
             frequency='monthly', period='1850-1853', version="*",
             customname='CNRM-CM5-hist'
             ),
        dict(project='CMIP6', model='CNRM-CM6-1', experiment='piControl',
             frequency='monthly', period='1950-1953',
             customname='CNRM-CM6-control'
             ),

    ]
    for model in models:
        if model['model'] == 'CNRM-CM6-1' or model['model'] == 'CNRM-ESM2-1':
            model['gridfile'] = gridpath+'ORCA1_mesh_zgr.nc'
            model['mesh_hgr'] = gridpath+'ORCA1_mesh_hgr.nc'

if atCerfacs:
    models = [

        # Sorte de dataset mais que avec les attributs communs a toutes les variables et simus
        dict(project='PRIMAVERA', model='CNRM-CM6-1', simulation='spinup-1950',
             realization='r1i1p1f2', period='1950-1979', frequency='monthly',
             customname='CNRM-CM6-1_spinup-1950_r1i1p1f2'
             ),

        # dict(project='CMIP6', model='CNRM-CM6-1', experiment='abrupt-4xCO2',
        #      frequency='monthly', period='1850-1853',
        #      customname='CNRM-CM6-abrupt'
        #      ),

    ]


# --> case onCiclad or atTGCC:
if onCiclad or atTGCC or onSpirit:
    models = [

        # dict(project='IGCM_OUT',
        #      login='lurtont',
        #      model='IPSLCM6',
        #      experiment='historical',
        #      simulation='CM61-LR-hist-01',
        #      clim_period='1980-2005',
        #      customname='CM61-LR-hist-01 *',
        #      color='red'
        #      ),

        # dict(project='IGCM_OUT',
        #      login='lurtont',
        #      model='IPSLCM6',
        #      experiment='historical',
        #      simulation='CM61-LR-hist-01',
        #      frequency='monthly',
        #      clim_period='last_10Y',
        #      customname='CM61-LR-hist-01 last_10Y',
        #      color='blue',
        #      ),

        # dict(project='CMIP5',
        #      model='IPSL-CM5A-MR',
        #      experiment='historical',
        #      frequency='monthly',
        #      period='1980-2005',
        #      version='latest',
        #      customname='CMIP5 IPSL-CM5A-MR'
        #      ),

        # dict(project='CMIP6',
        #      model='IPSL-CM6A-LR',
        #      experiment='historical',
        #      frequency='monthly',
        #      period='1980-2005',
        #      realization='r2i1p1f1',
        #      version='latest'
        #      ),

        dict(project='IGCM_OUT',
             login='p86caub',
             model='IPSLCM7',
             experiment='pdControl',
             simulation='CM70-ico-O4-BOOST100',
             clim_period='1880_1889',
             customname='ICOBOOST100',
             color='red'
             ),

        dict(project='IGCM_OUT',
             login='p86caub',
             model='IPSLCM7',
             experiment='pdControl',
             simulation='CM70-ico-O4-BOOST100',
             clim_period='last_5Y',
             customname='ICOBOOST100_L5',
             color='red'
             ),
    ]
    if atTGCC:
        # CMIP5 and CMIP6 data are not readable by everyone there...
        alt_models = [ m for m in models if 'CMIP' not in m['project']]
        models = alt_models
        root = '/ccc/store/cont003/gencmip6'
        
    if onCiclad or onSpirit:
        root = '/thredds/tgcc/store'
    #
    # -- Provide a set of common keys to the elements of models
    # ---------------------------------------------------------------------------- >
    common_keys = dict(
        root=root,
        login='*',
        frequency='monthly',
        clim_period='last_30Y',
        ts_period='full',
        ENSO_ts_period='last_80Y',
        mesh_hgr=gridpath + 'eORCA1.2_mesh_mask_glo.nc',
        gridfile=gridpath + 'eORCA1.1_grid.nc',
        varname_area='area',
    )
    #
    for model in models:
        if model['project'] == 'IGCM_OUT':
            for key in common_keys:
                if key not in model:
                    model.update({key: common_keys[key]})


# -- Find the last available common period to all the datasets
# -- with clim_period = 'common_clim_period'
# ---------------------------------------------------------------------------- >
common_period_variable = 'tas'
# common_clim_period = 'last_10Y'
common_clim_period = None

if common_clim_period:
    find_common_period(models, common_period_variable, common_clim_period)


# -- Set the reference against which we plot the diagnostics
# ---------------------------------------------------------------------------- >
# --    -> 'default' uses variable2reference to point to a default
# --       reference dataset (obs and reanalyses)
# --    -> you can set reference to a dictionary that will point any other
# --       climaf dataset
# --       For instance, you can set it to models[0] if you want to see the
# --       differences relative to the first simulation of the list 'models'
reference = 'default'

# reference = dict(project='CMIP5', model='CNRM-CM5', experiment='historical',
#                  frequency='monthly', period='1980-2005',
#                  customname='CMIP5 CNRM-CM5'
#                 )

# -- Declare a 'CMIP5_bis' CliMAF project (a replicate of the CMIP5 project)
# ---------------------------------------------------------------------------- >
# cproject('CMIP5_bis', ('frequency','monthly'), 'model', 'realm', 'table', 'experiment',
#          ensemble=['model','simulation'],separator='%')
# --> systematic arguments = simulation, frequency, variable
# -- Set the aliases for the frequency
# cfreqs('CMIP5_bis', {'monthly':'mon'})
# -- Set default values
# cdef('simulation'  , 'r1i1p1'       , project='CMIP5_bis')
# cdef('experiment'  , 'historical'   , project='CMIP5_bis')
# cdef('table'       , '*'            , project='CMIP5_bis')
# cdef('realm'       , '*'            , project='CMIP5_bis')
# -- Define the pattern
# pattern="/prodigfs/project/CMIP5/output/*/${model}/${experiment}/${frequency}/${realm}/${table}/${simulation}/latest/
#         "${variable}/${variable}_${table}_${model}_${experiment}_${simulation}_YYYYMM-YYYYMM.nc"
# --> Note that the YYYYMM-YYYYMM string means that the period is described in the filename and that CliMAF can
# --> perform period selection among the files it found in the directory (can be YYYY, YYYYMM, YYYYMMDD).
# --> You can use an argument like ${years} instead if you just want to do string matching (no smart period selection)
#
# -- call the dataloc CliMAF function
# dataloc(project='CMIP5_bis', organization='generic', url=pattern)
# ---------------------------------------------------------------------------- >

#
# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #
