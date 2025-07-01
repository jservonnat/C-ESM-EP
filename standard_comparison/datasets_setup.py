# ---------------------------------------------------------------------------- >
from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM, atCerfacs #, onObelix
from CM_atlas import *


# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

# -- Set the path to the grids
if onCiclad or onSpirit:
    gridpath = '/data/igcmg/database/grids/'
if atTGCC:
    gridpath = '/ccc/work/cont003/igcmg/igcmg/database/grids/'
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

reference = 'default'

#climaf.driver.scripts_ouput_write_mode='a'
