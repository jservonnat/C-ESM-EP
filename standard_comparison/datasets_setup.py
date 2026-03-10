# ---------------------------------------------------------------------------- >
from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM, atCerfacs, onObelix
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
    
    dict(project='CMIP6',
         model='IPSL-CM6A-LR',
         experiment='historical',
         frequency='monthly',
         period='1980-2005',
         realization='r2i1p1f1',
         version='latest'
         ),

    # dict(project='CMIP5',
    #      model='IPSL-CM5A-MR',
    #      experiment='historical',
    #      frequency='monthly',
    #      period='1980-2005',
    #      version='latest',
    #      customname='CMIP5 IPSL-CM5A-MR'
    #      ),

    # dict(project='IGCM_OUT',
    #           root='/data',
    #           login='ssenesi',
    #           model='IGCM_OUT/OL2',
    #           status='TEST',
    #           experiment='cesmep',
    #           simulation='FG2C',
    #           frequency='monthly',
    #           OUT='*',
    #           ts_period='full',
    #           ),
    # dict(project='IGCM_OUT',
    #          login='p86caub',
    #          model='IPSLCM7',
    #          experiment='pdControl',
    #          simulation='CM70-ico-O4-BOOST100',
    #          clim_period='1880_1889',
    #          customname='ICOBOOST100',
    #          color='red'
    #          ),
    # dict(project='IGCM_OUT',
    #      login='p86caub',
    #      model='IPSLCM7',
    #      experiment='pdControl',
    #      simulation='CM70-ico-O4-BOOST100',
    #      clim_period='last_5Y',
    #      customname='ICOBOOST100_L5',
    #      color='red'
    #      ),


    #/data/lolivera/IGCM_OUT/OL2/TEST/secsto/FG2nd.siberia.10mHF
    #/data/lolivera/IGCM_OUT/OL2/TEST/secsto/FG2nd.siberia.30mHF

    ]
if atTGCC:
    root = '/ccc/store/cont003/gencmip6'
    # -- We don't have access to the CMIP archive at TGCC;
    # we remove them from the list models
    models = [ m for m in models if not m['project'].startswith('CMIP') ]
if onSpirit:
    root = '/thredds/tgcc/store'

if atTGCC:
    root = '/ccc/store/cont003/gencmip6'
    # -- We don't have access to the CMIP archive at TGCC;
    # we remove them from list models
    models = [ m for m in models if not m['project'].startswith('CMIP') ]
if onSpirit:
    root = '/thredds/tgcc/store'

        
if onObelix:
    models = [
        dict(project='IGCM_OUT',
             root = '/home/scratch01', 
             login='vbastri',
             model='IGCM_OUT/OL2',
             experiment='ORC3v8120',
             status='TEST',
             OUT='Output',
             simulation='FGH.20Y',
             #clim_period='2001-2020',
             clim_period='2001-2002',
             #customname='CM61-LR-hist-01 *',
             color='red'
             ),
        # /home/orchideeshare/repository/IGCM_OUT/OL2/PROD/ORC4tag42/FGH.CRUJRA.tag42
        dict(project='IGCM_OUT',
             root = '/home/orchideeshare', 
             login='repository',
             model='IGCM_OUT/OL2',
             experiment='ORC4tag42',
             status='PROD',
             OUT='Output',
             simulation='FGH.CRUJRA.tag42',
             clim_period='2001-2002',  #dispo : '1901-2020'
             #customname='CM61-LR-hist-01 *',
             color='blue'
             ),
        ]
    

if atIPSL:
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

# You can have last.out accumulate the outputs of launched scripts
#climaf.driver.scripts_ouput_write_mode='a'

import env
try:
    # If possible, use (new) script plotmap for plotting maps
    # (generally, this works without changing anything else)
    # env.environment.plot_use_plotmap = True
    
    # plotmap wrapper may printout how it transforms the calls to plot()
    env.environment.teach_me_plotmap = True
except:
    pass
