# ---------------------------------------------------------------------------- >
from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM, atCerfacs, onObelix
from CM_atlas import *


# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

# -- Set the path to the grids
gridpath = '/data/igcmg/database/grids/'


# --> case onCiclad or atTGCC:
models = [

    # dict(project='IGCM_OUT',
    #      login='lurtont',
    #      model='IPSLCM6',
    #      experiment='historical',
    #      simulation='CM61-LR-hist-01',
    #      clim_period='1980-2005',
    #      customname='CM61-LR-hist-01 *',
    #      color='red',
    #      ts_period='1980-1989',
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
              root='/data',
              login='ssenesi',
              model='IGCM_OUT/OL2',
              status='TEST',
              experiment='cesmep',
              simulation='FG2C',
              frequency='monthly',
              OUT='Analyse',
              ts_period='full',
              )

    #/data/lolivera/IGCM_OUT/OL2/TEST/secsto/FG2nd.siberia.10mHF
    #/data/lolivera/IGCM_OUT/OL2/TEST/secsto/FG2nd.siberia.30mHF

    ]
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
