# TIME MANAGER
from climaf.api import *
import os, copy, subprocess, shlex
from datetime import datetime
from shutil import copyfile
from getpass import getuser

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
    def period_update_dict(DAT_DICT,diag):
        wdat_dict = copy.deepcopy(DAT_DICT)
        if diag+'_frequency' in wdat_dict:
            wdat_dict.update(dict(frequency=wdat_dict[diag+'_frequency']))
        if diag+'_period' in wdat_dict:
            wdat_dict.update(dict(period=wdat_dict[diag+'_period']))
        if diag+'_clim_period' in wdat_dict:
            wdat_dict.update(dict(clim_period=wdat_dict[diag+'_clim_period']))
        if diag+'_ts_period' in wdat_dict:
            wdat_dict.update(dict(ts_period=wdat_dict[diag+'_ts_period']))
        return wdat_dict
    print ''
    if isinstance(DAT_DICT,dict):
        return period_update_dict(dat_dict,diag)
    if isinstance(DAT_DICT,list):
        WDAT_DICT = copy.deepcopy(DAT_DICT)
        for dat_dict in WDAT_DICT:
            dat_dict.update(period_update_dict(dat_dict,diag))
        return WDAT_DICT

    
def base_variable_of_derived_variable(tested_variable, project='*'):
    ''' Returns one of the variables used to compute a derived variable '''
    project_derived_variables = copy.deepcopy(derived_variables['*'])
    if project in derived_variables: project_derived_variables.update(derived_variables[project])
    while tested_variable in project_derived_variables.keys():
        for elt in project_derived_variables[tested_variable]:
            if isinstance(elt,list):
                base_var = elt[0]
        tested_variable = base_var
    return tested_variable


def frequency_manager_for_diag_type(model, diag_type='TS'):
    if 'frequency' in model:
        # -- Diagnostics on TS
        if diag_type.upper()=='TS':
            model.update(dict(diag_type=diag_type))
            if 'ts_period' in model:
                model.update(dict(period=model['ts_period']))
            if 'ts_frequency' in model:
                model['frequency']=model['ts_frequency']
            else:
                model['frequency']='monthly'
        # -- Diagnostics on SE
        if diag_type.upper() in ['SE', 'CLIM']:
            model.update(dict(diag_type=diag_type))
            # -- Fix to avoid errors when clim_period contains a - instead of _
            if 'clim_period' in model:
                model.update(dict(clim_period=str.replace(model['clim_period'],'-','_')))
                # -- If frequency=='monthly' or 'yearly', we use clim_period for period

                if model['frequency'] in ['monthly', 'yearly']:
                    if 'SE' in model['clim_period']:
                        model['clim_period'] = str.replace(model['clim_period'],'_SE','')
                        model['frequency'] = 'seasonal'
                    else:
                        model.update(dict(period=model['clim_period']))
    return ''

supported_projects=['IGCM_OUT', 'IGCM_OUT_old']

def split_periods_in_models(models):
    import copy
    Wmodels = copy.deepcopy(models)
    New_models = []
    #
    for model in Wmodels:
        splitted_model = []
        if 'frequency' in model:
            if model['frequency'] in ['seasonal', 'annual_cycle']: wperiod = 'clim_period'
            if model['frequency'] in ['monthly']: wperiod = 'period'
            if isinstance(model[wperiod],list):
                for PRD in model[wperiod]:
                    wmodel = model.copy()
                    wmodel.update({wperiod:PRD})
                    splitted_model.append(wmodel)
                New_models = New_models + splitted_model
            else:
                New_models.append(model)
        else:
            print 'frequency is missing in model: ',model
    return New_models



def get_keys_for_PMP_MG(wmodel):
    ''' Works on a python dictionary that typically describes a dataset '''
    ''' in the C-ESM-EP datasets_setup.py.                              '''
    ''' Get the keys that are necessary to work with the PMP / MG       '''
    ''' These keys will be used to build the path the metrics results,  '''
    ''' the name of the netcdf climatology file taken as input by the   '''
    ''' PMP, or to provide the keys in the PMP so that the metrics      '''
    ''' metadata are provided.                                          '''
    Wmodel = wmodel.copy()
    for key in ['project','model','experiment','simulation','variable','login']:
       if key not in wmodel:
          Wmodel.update({key:key+'_not_defined'})
       else:
          if wmodel[key]=='*': Wmodel.update({key:key+'_not_defined'})
    #
    return Wmodel

    

def build_metric_outpath(model, group, subdir=None, root_outpath=None):
    ''' Builds the typical output tree for the metrics  '''
    ''' Takes as input a python dictionary (dataset),   '''
    ''' a group of metrics (name in the mongo database) '''
    ''' and a sub-directory subdir.                     '''
    #
    if not root_outpath:
        from getpass import getuser
        if onCiclad: root_outpath = '/data/'+getuser()
        if atTGCC:   root_outpath = '${SCRATCHDIR}'
    if not subdir:
        from datetime import datetime
        subdir = datetime.today().strftime("%Y-%m-%d")
    #
    # -- 0/ Fill the keys with 'not provided' with get_keys_for_PMP_MG
    wmodel = get_keys_for_PMP_MG(model)
    #
    project =    wmodel['project']
    model =      wmodel['model']
    experiment = wmodel['experiment']
    simulation = wmodel['simulation']
    login =      wmodel['login']
    if wmodel['period']=='fx':
       period = wmodel['clim_period']
    else:
       period = wmodel['period']
    #
    # -- Prepare the output directory for the temporary netcdf files that will be used
    # -- to compute the metrics
    #
    return root_outpath + '/PMP_OUT/metrics_results/'+ subdir + '/raw/' + project+'_'+login+'_'+model+'_'+experiment+'_'+simulation+'_'+period+'_'+group
    

def build_input_climatology_filename(model):
    ''' Builds the name of an input climatology filename '''
    ''' Takes as input a python dictionary (dataset).    '''
    #
    # -- 0/ Fill the keys with 'not provided' with get_keys_for_PMP_MG
    wmodel = get_keys_for_PMP_MG(model)
    
    project =    wmodel['project']
    model =      wmodel['model']
    experiment = wmodel['experiment']
    simulation = wmodel['simulation']
    period =     wmodel['period']
    variable =   wmodel['variable']

    # -- Prepare the output directory for the temporary netcdf files that will be used
    # -- to compute the metrics
    return project+'_'+model+'_'+experiment+'_'+simulation+'_'+period+'_'+variable+'.nc'
    



dict_group = {
        'LMDZ_PCMDI':{
           'variables':['pr','prw','tas','uas','vas','psl','rlut','rsut','rlutcs','rsutcs','huss',
                        'ta_850','ta_200','ua_850','ua_200','va_850','va_200','zg_500','hus_850'
                        'rtnetcre','rstcre','rltcre',
                        'tauu','tauv'],
            'targetGrid':'2.5x2.5'
        },
        'NEMO_PCMDI':{
            'variables':['sos','tos','wfo','zos','mldpt'],
            'targetGrid':'2.5x2.5'
        },
        'NEMO_VertLevels':{
            'variables':['tod_50','tod_100','tod_500','tod_1000',
                        'sod_50','sod_100','sod_500','sod_1000'],
            'targetGrid':'2.5x2.5'
        },
        'PISCES_VertLevels':{
            'variables':['PO4_1000m'],
            'targetGrid':'2.5x2.5'
        },
        'ORCHIDEE_PCMDI':{
            'variables':['gpp'],
            'targetGrid':'2.5x2.5'
        }
    }

import re

def pysed(file, old_pattern, new_pattern):
    with open(file, "r") as sources:
        lines = sources.readlines()
    with open(file, "w") as sources:
        for line in lines:
            sources.write(re.sub(old_pattern, new_pattern, line))
    print 'Replaced old_pattern = '+old_pattern+' with new_pattern = '+new_pattern
    print 'in the file : ',file
    return ''


