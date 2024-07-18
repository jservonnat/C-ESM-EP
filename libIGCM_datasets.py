# This is a version of datasets_setup.py adapted for the case of a libIGCM
# running simulation at TGCC. It creates a list of 'models' made of
# successive time slices up to the last processed one (which is described by
# imported file libIGCM_settings

from libIGCM_settings import root, Login, TagName, SpaceName, \
    frequency, OUT, DateBegin, \
    CesmepSlices, CesmepPeriod, CesmepSlices, CesmepSlicesDuration, \
    end, data_end

try:
    from libIGCM_settings import JobName, ExperimentName
except:
    # Odd syntax from an old version of CESMEP. To me removed at some date...
    from libIGCM_settings import ExperimentName as JobName, ExpType as ExperimentName

from env.site_settings import atIDRIS, atTGCC, onSpirit

# Next three imports allow to process data that is not at the location
# initialized by libIGCM. This is the case when creating a fake
# simulation for processing the data of another simulation
# Each segment of the data path which is not correct should be changed
try:
    from libIGCM_settings import DataPathJobName
except:
    try:
        # Old (odd) syntax, and for upward compatibility
        from libIGCM_settings import DataPathExperimentName as DataPathJobName
    except:
        DataPathJobName = JobName

#  e.g. /ccc/store/cont003/gen0826
try:
    from libIGCM_settings import DataPathRoot
except:
    DataPathRoot = root

try:
    from libIGCM_settings import DataPathLogin
except:
    DataPathLogin = Login


#from CM_atlas.time_manager import find_common_period

# -- Patterns to clean the cache at the end of the execution of the atlas
routine_cache_cleaning = [dict(age='+20')]

models = []
common = dict(project='IGCM_OUT',
              root=DataPathRoot,
              login=DataPathLogin,
              model=TagName,
              status=SpaceName,
              experiment=ExperimentName,
              simulation=DataPathJobName,
              frequency=frequency,
              OUT=OUT,
              ts_period='full'
              )

YearBegin = int(DateBegin[0:4])
if CesmepPeriod != 0:
    begin = end - CesmepSlicesDuration + 1
    count = 0
    while begin >= YearBegin and count < CesmepSlices:
        current_slice = common.copy()
        clim_period = "%d_%d" % (begin, end)
        current_slice.update(clim_period=clim_period,
                             customname=JobName + '_' + clim_period)
        models.insert(0, current_slice)
        begin -= CesmepPeriod
        end -= CesmepPeriod
        count += 1
else:
    clim_period = "%d_%d" % (YearBegin, data_end)
    common.update(clim_period=clim_period,
                  customname=JobName + ' ' + clim_period)
    models.append(common)

#
# -- Provide a set of common keys to the elements of models
# ---------------------------------------------------------------------------- >
if atTGCC:
    root = '/ccc/store/cont003/gencmip6'
    gridpath = '/ccc/work/cont003/igcmg/igcmg/Database/grids/'
elif atIDRIS:
    root = '/gpfsstore/rech/psl'
    gridpath = '/gpfswork/rech/psl/commun/database/grids'
elif onSpirit:
    root = 'please_set_default_root_for_spirit_in_libIGCM_datasets.py'
    gridpath = 'please_set_gridpath_for_spirit_in_libIGCM_datasets.py'

IGCM_common_keys = dict(
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
        for key in IGCM_common_keys:
            if key not in model:
                model.update({key: IGCM_common_keys[key]})
    if model['model'] == 'IPSL-CM6A-LR':
        model['gridfile'] = gridpath + 'eORCA1.2_mesh_mask_glo.nc'
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
try:
    from libIGCM_references import reference
    print("References were provided through libIGCM")
except:
    reference = 'default'


#
# ---------------------------------------------------------------------------------------- #
# -- END                                                                                -- #
# ---------------------------------------------------------------------------------------- #
