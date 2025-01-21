#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
#from __future__ import unicode_literals, print_function, absolute_import, division


from climaf.api import *
import os
import copy

# -- Si je veux choisir ma periode, et qu'elle soit la meme entre les TS et les climato
#    -> frequency='monthly', period='1980-2000'
# -- Si je veux utiliser les SE:
#    -> frequency='seasonal', clim_period='1980_1989'
# -- Si je veux utiliser les SE pour les climatos, et choisir ma periode pour les TS:
#    -> frequency='seasonal', clim_period='1980_1989', ts_period='full'
# -- Si je veux le dernier SE pour les climatos, et choisir ma periode pour les TS:
#    -> frequency='seasonal', clim_period='last', ts_period='full'
# -- Si je veux toute la periode pour les TS, et seulement une selection pour les climatos (ne pas tout utiliser)
#    -> frequency='monthly', clim_period='last_30Y', ts_period='full'
#    -> frequency='monthly', clim_period='1980_2005', ts_period='full'

# -- En amont du diag, il faut faire la difference entre diag 'clim' ou diag 'TS'
import copy


def period_for_diag_manager(DAT_DICT, diag=''):
    ''' In a python dictionary dat_dict defining a CliMAF dataset, '''
    ''' this function updates:                                     '''
    '''   - period with dat_dict[diag+'_period']                   '''
    '''   - ts_period with dat_dict[diag+'_ts_period']             '''
    '''   - clim_period with dat_dict[diag+'_clim_period']         '''
    ''' In the context of a CliMAF atlas, it allows choosing the   '''
    ''' period for each diagnostic.                                '''
    '''                                                            '''
    ''' Returns the updated dictionary.                            '''

    def period_update_dict(DAT_DICT, diag):
        wdat_dict = copy.deepcopy(DAT_DICT)
        if diag + '_frequency' in wdat_dict:
            wdat_dict.update(dict(frequency=wdat_dict[diag + '_frequency']))
        if diag + '_period' in wdat_dict:
            wdat_dict.update(dict(period=wdat_dict[diag + '_period']))
        if diag + '_clim_period' in wdat_dict:
            wdat_dict.update(dict(clim_period=wdat_dict[diag + '_clim_period']))
        if diag + '_ts_period' in wdat_dict:
            wdat_dict.update(dict(ts_period=wdat_dict[diag + '_ts_period']))
        return wdat_dict

    print('')
    if isinstance(DAT_DICT, dict):
        return period_update_dict(dat_dict, diag)
    if isinstance(DAT_DICT, list):
        WDAT_DICT = copy.deepcopy(DAT_DICT)
        for dat_dict in WDAT_DICT:
            dat_dict.update(period_update_dict(dat_dict, diag))
        return WDAT_DICT


def base_variable_of_derived_variable(tested_variable, project='*'):
    ''' Returns one of the variables used to compute a derived variable '''
    project_derived_variables = copy.deepcopy(derived_variables['*'])
    if project in derived_variables:
        project_derived_variables.update(derived_variables[project])
    while tested_variable in project_derived_variables.keys():
        for elt in project_derived_variables[tested_variable]:
            if isinstance(elt, list):
                base_var = elt[0]
        tested_variable = base_var
    return tested_variable


def frequency_manager_for_diag(model, diag='TS'):
    ''' Modify a model dictionary according to the diag required:
          - if diag='TS', then period is updated with the value passed to ts_period
          - if diag='SE' or 'CLIM', the period is updated with the value passed to clim_period
        If you have no ts_period or clim_period, then frequency_manager_for_diag doesn't do anything.
    '''

    if 'frequency' in model:
        # -- Diagnostics on TS
        if diag.upper() == 'TS':
            model.update(dict(diag=diag))
            if 'ts_period' in model:
                model.update(dict(period=model['ts_period']))
            if 'ts_frequency' in model:
                model['frequency'] = model['ts_frequency']
            else:
                model['frequency'] = 'monthly'
        # -- Diagnostics on SE
        if diag.upper() in ['SE', 'CLIM']:
            model.update(dict(diag=diag))
            # -- Fix to avoid errors when clim_period contains a - instead of _
            if 'clim_period' in model:
                model.update(dict(clim_period=model['clim_period'].replace('-', '_')))
                # -- If frequency=='monthly' or 'yearly', we use clim_period for period
                if model['frequency'] in ['daily', 'monthly', 'yearly']:
                    if 'SE' in model['clim_period']:
                        model.update({'frequency': 'seasonal'})
                    else:
                        model.update(dict(period=model['clim_period']))
    print("model in frequency_manager = ", model)
    return ''


def get_period_manager(dat_dict, diag=None):
    #
    # Garde fou: if frequency is missing in dat_dict, we use the default value (monthly most of the time)
    if 'frequency' not in dat_dict:
        ds_dat_dict = ds(**dat_dict)
        dat_dict.update(dict(frequency=ds_dat_dict.kvp['frequency']))
    #
    # Treat the three cases, so that we get the right 'period' to use with ds().explore
    #   - 1. diag = None   -> use period
    #   - 2. diag = 'clim' -> use clim_period, or period if clim_period not provided
    #   - 3. diag = 'ts'   -> use ts_period, or period if ts_period not provided
    #
    period = None
    clim_period = None
    #
    # - 1. diag = None
    if not diag:
        # Garde fou
        if 'period' in dat_dict:
            period = dat_dict['period']
        else:
            period = 'No period provided and diag=None'
            print(period, 'in', dat_dict)
    #
    # - 2. diag = 'clim'
    if diag == 'clim':
        # - if we use SE data
        if dat_dict['frequency'] in ['annual_cycle', 'seasonal']:
            if 'period' in dat_dict:
                dat_dict.pop('period')
            if 'clim_period' in dat_dict:
                clim_period = dat_dict['clim_period']
            else:
                clim_period = 'No clim period provided!'
        else:
            if 'clim_period' in dat_dict:
                period = dat_dict['clim_period']
            else:
                period = dat_dict['period']
    #
    # - 3. diag = 'ts'
    if diag == 'ts':
        if dat_dict['frequency'] in ['daily', 'monthly', 'yearly']:
            if 'ts_period' in dat_dict:
                if dat_dict['ts_period'] == 'full':
                    period = '*'
                else:
                    period = dat_dict['ts_period']
            else:
                # Garde fou
                if 'period' in dat_dict:
                    period = dat_dict['period']
                else:
                    period = 'No period nor ts_period provided'
                    print(period, 'in ', dat_dict)
    #
    print('dat_dict before .resolve ', dat_dict)
    # -- request for all the files
    req_dict = dat_dict.copy()
    #
    # -> Check if the variable is a derived variable; if yes, returns one variable it is based on
    # -> Will be used only for the request
    tested_variable = req_dict['variable']
    req_dict.update(dict(variable=base_variable_of_derived_variable(
        tested_variable, req_dict['project'])))
    #
    # -- if period, we can use the .explore('resolve') method to get the available period
    if period:
        req_dict.update(dict(period=period))
        # - Get the period corresponding to the user request (among *, last_10Y,...)
        if period.upper() in ['FULL', '*'] \
           or 'LAST_' in period.upper() \
           or 'FIRST_' in period.upper():
            # -- Use ds.explore method to find the available period
            #try:
            #    req = ds(**req_dict).explore('resolve')
            #    print('req.kvp = ', req.kvp)
            #    dat_dict['period'] = str(req.kvp['period'])
            #except:
            #    print('Error in get_period_manager => No File found for ', req_dict)
            #    if tested_variable != req_dict['variable']:
            #        print('Initially you asked for variable ', tested_variable)
            req = ds(**req_dict).explore('resolve')
            if req.baseFiles():
                dat_dict['period'] = str(req.kvp['period'])
            else:
                print('Error in get_period_manager => No File found for ', req_dict)
                #print(cfile(req))
                if tested_variable != req_dict['variable']:
                    print('Initially you asked for variable ', tested_variable)

        else:
            dat_dict.update(dict(period=period))
    if clim_period and dat_dict['frequency'] in ['annual_cycle', 'seasonal']:
        req_dict.update(dict(clim_period=clim_period, period='fx'))
        if 'LAST' in clim_period.upper() or 'FIRST' in clim_period.upper():
            # -- request for all the files
            req = ds(**req_dict)
            #
            # -- Get all the available clim periods
            clim_periods = req.explore('choices')['clim_period']
            first_SE = clim_periods[0]
            last_SE = clim_periods[-1]
            # -- Treat either first or last file
            if clim_period.upper() in ['LAST', 'LAST_SE']:
                dat_dict['clim_period'] = last_SE
            if clim_period.upper() in ['FIRST', 'FIRST_SE']:
                dat_dict['clim_period'] = first_SE
    #
    return dat_dict


def find_common_period(models, common_period_variable, common_clim_period):
    last_available_periods = []
    startyear_last_available_periods = []
    common_period_models = []
    for model in models:
        wmodel = model.copy()
        if 'clim_period' in model:
            if model['clim_period'] == 'common_clim_period':
                wmodel.update(dict(variable=common_period_variable, clim_period=common_clim_period))
                frequency_manager_for_diag(wmodel, diag='SE')
                get_period_manager(wmodel)
                cp_model = ''
                if 'model' in wmodel:
                    cp_model = wmodel['model'] + ' '
                if 'simulation' in wmodel:
                    cp_model = cp_model + wmodel['simulation']
                common_period_models.append(cp_model)
                if model['frequency'] == 'monthly':
                    wperiod = wmodel['period']
                if model['frequency'] == 'seasonal':
                    wperiod = wmodel['clim_period']
                print(wmodel)
                print(wperiod)
                last_available_periods.append(wperiod)
                startyear_last_available_periods.append(int(wperiod[0:4]))
    #
    # -- find the last available period
    sorted_periods = sorted(startyear_last_available_periods)
    last_available_period = last_available_periods[startyear_last_available_periods.index(sorted_periods[0])]
    #
    # -- Now update the model dictionaries with the common period that we found:
    for model in models:
        if 'clim_period' in model:
            if model['clim_period'] == 'common_clim_period':
                model.update(dict(clim_period=last_available_period))
        print('--> Updated model with common period found accross all simulations:')
        print(model)
    #
    print('==> Model with earliest last available clim_period = ' + common_period_models[
        startyear_last_available_periods.index(sorted_periods[0])])
    return models
