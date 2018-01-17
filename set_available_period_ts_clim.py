# -----------------------------------------------------------------------------------------------------
# -- set_period.py is used to speed up the execution of the C-ESM-EP.
# -- A time consuming operation is the period_manager, that checks the available periods for
# -- each dataset, for each set of diagnostic, variable, and at every execution of the C-ESM-EP.
# -- This feature is highly interesting because you work on the up-to-date available results,
# -- but it can be highly time consuming.
# -- set_period.py aims at doing it only when the user needs to find the last data available.
# -- It creates a 'datasets_setup_period_set.py' file that is used by the C-ESM-EP.
# -- It contains two additionnal dictionaries to datasets_setup.py, obtained with period_manager:
# --    - one for diagnostics on climatologies (Wmodels_clim)
# --    - one for the time series diagnostics (Wmodels_ts)
# -- We use it like this:
# --   > python set_period.py ${comparison}
# -- 
# -- Author: Jerome Servonnat, LSCE-CEA
# -- Contact: jerome.servonnat at lsce.ipsl.fr
# -----------------------------------------------------------------------------------------------------
from CM_atlas import *

# -- Get the comparison name and build the datasets_setup.py file name
args = sys.argv
print 'len(args) = ',len(args)
if len(args)==1:
    print '--> Provide a comparison name'
if len(args)==2:
    print 'Ok'
    comparison = args[1]
    if not comparison[len(comparison)-1]=='/': comparison+='/'
    datasets_setup_file = comparison+'datasets_setup.py'

# -- Create the datasets_setup_period_set.py file
datasets_setup_available_period_set_file = str.replace(datasets_setup_file,'.py','_available_period_set.py')
os.system('cp '+datasets_setup_file+' '+datasets_setup_available_period_set_file)


# -- Execute the datasets_setup file to get the content
execfile(datasets_setup_file)

# -- Which variable do we use to test the availability of the files?
period_manager_test_variable = 'tas'

# -- Clim ---------------------------------------------
Wmodels_clim = period_for_diag_manager(models, diag='clim')
for dataset_dict in Wmodels_clim:
   #
   if 'clim_period' in dataset_dict:
        if 'last' in dataset_dict['clim_period'].lower() or 'first' in dataset_dict['clim_period'].lower():
            dataset_dict.update(dict(variable=period_manager_test_variable))
            frequency_manager_for_diag(dataset_dict, diag='clim')
            get_period_manager(dataset_dict)
            dataset_dict.pop('variable')

# -- TS ---------------------------------------------
Wmodels_ts = period_for_diag_manager(models, diag='TS')
for dataset_dict in Wmodels_ts:
   #
   if 'ts_period' in dataset_dict:
        if 'last' in dataset_dict['ts_period'].lower() or 'first' in dataset_dict['ts_period'].lower() or 'full' in dataset_dict['ts_period'].lower():
            dataset_dict.update(dict(variable=period_manager_test_variable))
            frequency_manager_for_diag(dataset_dict, diag='TS')
            get_period_manager(dataset_dict)
            dataset_dict.pop('variable')


# -- Append the results to datasets_setup_available_period_set.py       
thefile = open(datasets_setup_available_period_set_file, 'a')
print>>thefile, 'Wmodels_ts = ['
for item in Wmodels_ts:
    print>>thefile, item,','
print>>thefile, ']'
print>>thefile, ' '
print>>thefile, ' '
print>>thefile, ' '
print>>thefile, 'Wmodels_clim = ['
for item in Wmodels_clim:
    print>>thefile, item,','
print>>thefile, ']'

thefile.close()

