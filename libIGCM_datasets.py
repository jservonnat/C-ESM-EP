# This is a version of datasets_setup.py adapted for the case of a libIGCM
# running simulation at TGCC.

import sys
#from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM, atCerfacs
from CM_atlas import *
from libIGCM_settings import root, Login, TagName, SpaceName, \
    ExpType, ExperimentName, frequency, OUT, begin, end, DateBegin

# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

gridpath = '/ccc/work/cont003/igcmg/igcmg/Database/grids/'

models = [
        
        dict(project='IGCM_OUT',
             login='lurtont',
             model='IPSLCM6',
             experiment='historical',
             simulation='CM61-LR-hist-01',
             clim_period='1981-2005',
             customname='CM61-LR-hist-01 *',
             color='red'
        ),

        dict(project='IGCM_OUT',
             root = root,
             login=Login,
             model=TagName,
             status=SpaceName,
             experiment=ExpType,
             simulation=ExperimentName,
             frequency=frequency,
             OUT=OUT,
             clim_period="%s_%s"%(begin,end),
             period="%s_%s"%(begin,end),
             ts_period="%s_%s"%(begin,end),
             color='blue'
        ),
]
        
root = '/ccc/store/cont003/gencmip6'
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
    if model['model'] == 'IPSL-CM6A-LR':
        model['gridfile'] = gridpath+ 'eORCA1.2_mesh_mask_glo.nc'
        model['mesh_hgr'] = gridpath + 'eORCA1.1_grid.nc'
    

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


#
# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #

