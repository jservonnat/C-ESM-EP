#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division


from CM_atlas import *
from datetime import datetime


clog('debug')
# -- Copy the existing one if there is one
# -- Update!! if the list models is not the same in datasets_setup and datasets_setup_available_period,
# -- we update it.
# -- priority to changes in datasets_setup_available_period; try to merge them!!


# -- Get the comparison name and build the datasets_setup.py file name
args = sys.argv
if len(args) == 1:
    print '--> Provide a comparison name'
if len(args) >= 2:
    comparison = args[1]
    if not comparison[len(comparison) - 1] == '/':
        comparison += '/'
    datasets_setup_file = comparison + 'datasets_setup.py'
# -- Which variable do we use to test the availability of the files?
check = None
if len(args) == 3:
    period_manager_test_variable = args[2]
    check = True
else:
    period_manager_test_variable = 'tas'

# -- Create the datasets_setup_period_set.py file
datasets_setup_available_period_set_file = str.replace(datasets_setup_file, '.py', '_available_period_set.py')
# -- If datasets_setup_available_period_set_file already exists, we copy it to create a backup

delay = datetime.utcnow() - datetime(2015, 1, 1)
additionnal = str(delay.microseconds)
back_up_datasets_setup_available_period_set_file = str.replace(datasets_setup_available_period_set_file, '.py',
                                                               '_' + additionnal + '.py')

if os.path.isfile(datasets_setup_available_period_set_file):
    os.system('cp ' + datasets_setup_available_period_set_file + ' ' + back_up_datasets_setup_available_period_set_file)
else:
    os.system('cp ' + datasets_setup_file + ' ' + datasets_setup_available_period_set_file)

# -- Execute the datasets_setup file to get the content
execfile(datasets_setup_file)

# -- Clim ---------------------------------------------
Wmodels_clim = period_for_diag_manager(models, diag='clim')
for dataset_dict in Wmodels_clim:
    #
    wdataset_dict = dataset_dict.copy()
    # -- Fix CMIP6 --
    if dataset_dict['project'] == 'IGCM_CMIP6':
        wdataset_dict.update(dict(project='IGCM_OUT', model='IPSLCM6'))
        if 'root' in wdataset_dict:
            wdataset_dict.update(dict(root=str.replace(wdataset_dict['root'], 'work', 'store')))
    # ---
    print 'wdataset_dict = ', wdataset_dict
    wdataset_dict.update(dict(variable=period_manager_test_variable))
    if dataset_dict['project'] == 'CMIP6' and period_manager_test_variable == 'tas':
        wdataset_dict.update(dict(grid='gr', table='Amon'))
    if dataset_dict['project'] == 'IGCM_OUT' and period_manager_test_variable == 'tas':
        wdataset_dict.update(dict(DIR='ATM'))
    if 'clim_period' in wdataset_dict:
        wdataset_dict = get_period_manager(wdataset_dict, diag='clim')
    if check:
        print '-----> Proceed checking clim = '
        cdrop(ds(**wdataset_dict))
        print cfile(ds(**wdataset_dict))
    # -- Fix CMIP6 --
    if 'period' in wdataset_dict:
        dataset_dict.update(dict(period=wdataset_dict['period']))
    if 'frequency' in wdataset_dict:
        dataset_dict.update(dict(frequency=wdataset_dict['frequency']))

# -- TS ---------------------------------------------
Wmodels_ts = period_for_diag_manager(models, diag='TS')
for dataset_dict in Wmodels_ts:
    #
    wdataset_dict = dataset_dict.copy()
    # -- Fix CMIP6 --
    if dataset_dict['project'] == 'IGCM_CMIP6':
        wdataset_dict.update(dict(project='IGCM_OUT', model='IPSLCM6'))
        if 'root' in wdataset_dict:
            wdataset_dict.update(dict(root=str.replace(wdataset_dict['root'], 'work', 'store')))
    # ---
    print 'wdataset_dict = ', wdataset_dict
    wdataset_dict.update(dict(variable=period_manager_test_variable))
    if dataset_dict['project'] == 'CMIP6' and period_manager_test_variable == 'tas':
        wdataset_dict.update(dict(grid='gr', table='Amon'))
    if dataset_dict['project'] == 'IGCM_OUT' and period_manager_test_variable == 'tas':
        wdataset_dict.update(dict(DIR='ATM'))
    if 'ts_period' in wdataset_dict:
        wdataset_dict = get_period_manager(wdataset_dict, diag='ts')
    if check:
        print '-----> Proceed checking TS = '
        cdrop(ds(**wdataset_dict))
        print cfile(ds(**wdataset_dict))
    # -- Fix CMIP6 --
    if 'period' in wdataset_dict:
        dataset_dict.update(dict(period=wdataset_dict['period']))
    if 'frequency' in wdataset_dict:
        dataset_dict.update(dict(frequency=wdataset_dict['frequency']))
    # --

thefile = open(datasets_setup_available_period_set_file, 'w')
print>> thefile, '# -- This file is used as a dataset_setup.py file.'
print>> thefile, '# -- It is used by main_C-ESM-EP.py if it exists. Remove it (or rename it) if you want to use the ' \
                 'period manager again.'
print>> thefile, '# -- All the modifications that you do here will be used by the C-ESM-EP.'
print>> thefile, '# -- However, they wont be merged to datasets_setup.py if you want to restart from datasets_setup.py.'
print>> thefile, ''
print>> thefile, ''
print>> thefile, ''

# -- Append the results to datasets_setup_available_period_set.py
list_of_kw = ['project', 'root', 'login', 'model', 'experiment', 'simulation',
              'realization']  # ,'frequency','period','clim_period','ts_period']
kw_for_ts = ['frequency', 'period', 'ts_period', 'diag']
kw_for_clim = ['frequency', 'period', 'clim_period', 'diag']

print>> thefile, 'Wmodels = ['

item_number = 0
for item in Wmodels_ts:
    print>> thefile, '    dict('
    for kw in list_of_kw:
        if kw in item:
            print>> thefile, '         ' + kw + '="' + item[kw] + '",'
    for kw in item:
        if kw not in list_of_kw + kw_for_ts + kw_for_clim:
            print>> thefile, '         ' + kw + '="' + item[kw] + '",'
    # -- Add period for climatology
    print>> thefile, '         clim_period = dict('
    for kw in kw_for_clim:
        if kw in Wmodels_clim[item_number]:
            print>> thefile, '                            ' + kw + '="' + Wmodels_clim[item_number][kw] + '",'
    print>> thefile, '                           ),'
    # -- Add period for the time series
    print>> thefile, '         ts_period   = dict('
    for kw in kw_for_ts:
        if kw in Wmodels_ts[item_number]:
            print>> thefile, '                            ' + kw + '="' + Wmodels_ts[item_number][kw] + '",'
    print>> thefile, '                           ),'
    # -- Close the item
    print>> thefile, '        ),'
    item_number = item_number + 1
print>> thefile, ']'

# -- Append the datasets_setup file
print>> thefile, ''
print>> thefile, ''
print>> thefile, ''

theoldlines = open(datasets_setup_file, 'r').readlines()
for oldline in theoldlines:
    print>> thefile, str.replace(oldline, '\n', '')

thefile.close()
