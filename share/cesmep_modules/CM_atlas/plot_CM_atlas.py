#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
#from __future__ import unicode_literals, print_function, absolute_import, division


from climaf.api import *
from climaf.chtml import *
from reference import variable2reference
from env.clogging import clogger, dedent
from .time_manager import *
from climaf import __path__ as cpath
import os
from climaf import cachedir
import shutil
import getpass
from climaf.plot.ocean_plot_params import dict_plot_params as ocean_plot_params
from climaf.chtml import blank_cell

StringFontHeight = 0.019

hover = False

cscript(
    'rmse_xyt', 'cdo sqrt -fldmean -timmean -sqr -sub ${in_1} ${in_2} ${out}')


def corr_xy(dat1, dat2):
    anom_dat1 = fsub(dat1, cscalar(ccdo(dat1, operator='fldmean')))
    anom_dat2 = fsub(dat2, cscalar(ccdo(dat2, operator='fldmean')))
    return divide(ccdo(multiply(anom_dat1, anom_dat2), operator='fldmean'),
                  multiply(ccdo(anom_dat1, operator='fldstd'),
                           ccdo(anom_dat2, operator='fldstd'))
                  )


ocean_variables = []
for oceanvar in ocean_plot_params:
    ocean_variables.append(oceanvar)


def is3d(variable):
    if variable in ['ta', 'ua', 'va', 'hus', 'hur', 'wap', 'cl', 'clw', 'cli', 'mc', 'tro3', 'vitu', 'vitv', 'vitw',
                    'geop', 'temp']:
        return True
    return False


def build_period_str(dat):
    if isinstance(dat, dict):
        ds_dat = ds(**dat)
    else:
        ds_dat = dat
    tmp_period = str(ds_dat.period)
    if 'clim_period' in ds_dat.kvp and str(ds_dat.period) == 'fx':
        tmp_period = ds_dat.kvp['clim_period']
    if 'years' in ds_dat.kvp and ds_dat.period == 'fx':
        tmp_period = ds_dat.kvp['years']
    return tmp_period


def replace_keywords_with_values(dat_dict, string):
    ds_dat = ds(**dat_dict)
    if '${' in string:
        new_string = string
        dum_split_string = string.split('${')
        for elt in dum_split_string:
            dum_split_elt = elt.split('}')
            if len(dum_split_elt) == 2:
                kw = dum_split_elt[0]
                if kw in ds_dat.kvp:
                    new_string = new_string.replace(
                        '${' + kw + '}', ds_dat.kvp[kw])
                else:
                    new_string = new_string.replace(
                        '${' + kw + '}', kw + '_not_available')
        return new_string
    else:
        return string


def get_realization_simulation_kw(ds_obj):
    if 'realization' in ds_obj.kvp:
        return ds_obj.kvp['realization']
    elif 'simulation' in ds_obj.kvp:
        return ds_obj.kvp['simulation']
    else:
        return ' '


def build_plot_title(model, ref=None, add_product_in_title=True):
    #if model is None:
    #    return "No data"
    if not ref:
        add_product_in_title = False
    #print('model = ', model)
    ds_model = ds(**model)
    #print('ds_model.kvp = ', ds_model.kvp)
    if 'customname' in model:
        title = replace_keywords_with_values(model, model['customname'])
    else:
        if 'product' not in ds_model.kvp:
            if model['project'] == 'CMIP5':
                title = ds_model.kvp['model']
            else:
                title = get_realization_simulation_kw(ds_model)
        else:
            title = ('OBS' if model['project'] ==
                     'LMDZ_OBS' else ds_model.kvp["product"])
    if add_product_in_title:
        ds_ref = ds(**ref)
        print('ref = ', ref)
        if 'model' in ds_ref.kvp:
            ref_in_title = (
                ref['customname'] if 'customname' in ref else ds_ref.kvp['model'] + ' ' + get_realization_simulation_kw(
                    ds_ref))
        else:
            ref_in_title = ('OBS' if ref['project'] ==
                            'LMDZ_OBS' else ds_ref.kvp["product"])
        title = title + ' (vs ' + ref_in_title + ')'
        title = title.replace('*', '')
    return title


# -- 2D Maps
def plot_climato( var, dat_dict, season, proj='GLOB', domain={},
                  custom_plot_params={}, do_cfile=True, mpCenterLonF=None,
                  cdogrid=None, regrid_option='remapbil', safe_mode=True,
                  ocean_variables=ocean_variables, shade_missing=False,
                  zonmean_variable=False, plot_context_suffix=None,
                  add_vectors=False, add_aux_contours=False,
                  display_field_stats=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print('var = ', var)
    grid = None
    table = None
    realm = None
    scale = 1.
    offset = 0.
    title = None
    project_specs = None
    if isinstance(var, dict):
        wvar = var.copy()
        variable = wvar['variable']
        wvar.pop('variable')
        if 'climato_plot_params' in wvar:
            wvar.update(wvar['climato_plot_params'])
            wvar.pop('climato_plot_params')
        if 'diff_plot_params' in wvar:
            wvar.pop('diff_plot_params')
        if 'regridding' in wvar:
            wvar.pop('regridding')
        if 'season' in wvar:
            season = wvar['season']
            wvar.pop('season')
        if 'cdogrid' in wvar:
            cdogrid = wvar['cdogrid']
            wvar.pop('cdogrid')
        if 'proj' in wvar:
            proj = wvar['proj']
            wvar.pop('proj')
        if 'domain' in wvar:
            domain = wvar['domain']
            wvar.pop('domain')
        if 'zonmean_variable' in wvar:
            zonmean_variable = wvar['zonmean_variable']
            wvar.pop('zonmean_variable')
        if 'regrid_option' in wvar:
            regrid_option = wvar['regrid_option']
            wvar.pop('regrid_option')
        if 'add_climato_contours' in wvar:
            add_climato_contours = wvar['add_climato_contours']
            wvar.pop('add_climato_contours')
        if 'add_product_in_title' in wvar:
            wvar.pop('add_product_in_title')
        if 'add_aux_contours' in wvar:
            add_aux_contours = wvar['add_aux_contours']
            wvar.pop('add_aux_contours')
        if 'plot_context_suffix' in wvar:
            plot_context_suffix = wvar['plot_context_suffix']
            wvar.pop('plot_context_suffix')
        if 'vectors' in wvar:
            add_vectors = True
            vectors_u = wvar['vectors']['u_comp']
            vectors_v = wvar['vectors']['v_comp']
            if 'grid' in wvar['vectors']:
                vectors_grid = wvar['vectors']['grid']
                wvar['vectors'].pop('grid')
            else:
                vectors_grid = None
            if 'table' in wvar['vectors']:
                vectors_table = wvar['vectors']['table']
                wvar['vectors'].pop('table')
            else:
                vectors_table = None
            vectors_field = 'full_field'
            vectors_options = wvar['vectors'].copy()
            vectors_options.pop('u_comp')
            vectors_options.pop('v_comp')
            if 'context' in vectors_options:
                vectors_options.pop('context')
            print('vectors_options = ', vectors_options)
            wvar.pop('vectors')
        if 'grid' in wvar:
            grid = wvar['grid']
            wvar.pop('grid')
        if 'table' in wvar:
            table = wvar['table']
            wvar.pop('table')
        if 'realm' in wvar:
            realm = wvar['realm']
            wvar.pop('realm')
        if 'display_field_stats' in wvar:
            display_field_stats = wvar['display_field_stats']
            wvar.pop('display_field_stats')
        if 'scale' in wvar:
            scale = wvar['scale']
        if 'offset' in wvar:
            offset = wvar['offset']
        if 'project_specs' in wvar:
            project_specs = wvar['project_specs']
            wvar.pop('project_specs')
        if 'title' in wvar:
            title = wvar['title']
            wvar.pop('title')
        if 'display_bias_corr_rmse' in wvar:
            wvar.pop('display_bias_corr_rmse')
    else:
        variable = var
        wvar = dict()
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    context = 'full_field'
    if plot_context_suffix:
        context = context + '_' + plot_context_suffix
    p = plot_params(variable, context, custom_plot_params=custom_plot_params)
    #
    # -- Add the projection
    if 'proj' not in p:
        p.update(dict(proj=proj))

    #
    if isinstance(var, dict):
        if 'options' in wvar:
            options = wvar['options']
            if 'options' in p:
                p['options'] = p['options'] + '|' + options
            else:
                p.update(dict(options=options))
            wvar.pop('options')
        if 'aux_options' in wvar:
            aux_options = wvar['aux_options']
            if 'aux_options' in p:
                p['aux_options'] = p['aux_options'] + '|' + aux_options
            else:
                p.update(dict(aux_options=aux_options))
            wvar.pop('aux_options')
    #
    # -- Add the variable and get the dataset
    wdat_dict = dat_dict.copy()
    wdat_dict.update(dict(variable=variable))
    #
    # -- Add the gr and table for the CMIP6 datasets
    if grid:
        wdat_dict.update(dict(grid=grid))
    if table:
        wdat_dict.update(dict(table=table))
        if 'mon' in table:
            wfreq = 'monthly'
        if 'yr' in table:
            wfreq = 'yearly'
        if 'day' in table:
            wfreq = 'daily'
        if '3hr' in table:
            wfreq = '3hourly'
        if 'frequency' in wdat_dict:
            if wdat_dict['frequency'] not in ['seasonal', 'annual_cycle']:
                wdat_dict.update(dict(frequency=wfreq))
        else:
            wdat_dict.update(dict(frequency=wfreq))
    if realm:
        wdat_dict.update(dict(realm=realm))

    # -- project_specs
    # -- This functionality allows to pass given specifications for one given project => more generic
    if project_specs:
        if wdat_dict['project'] in project_specs:
            wdat_dict.update(project_specs[wdat_dict['project']])
    #
    # -- Apply get_period_manager
    wdat_dict = get_period_manager(wdat_dict, diag='clim')
    print('wdat_dict in plot_climato = ', wdat_dict)
    #
    # -- Get the dataset
    if safe_mode:
        try:
            ds_dat = ds(**wdat_dict).explore('resolve')
        except:
            return safe_mode_cfile_plot(plot(ds(**wdat_dict)), do_cfile, safe_mode)
    else:
        try:
            ds_dat = ds(**wdat_dict).explore('resolve')
        except:
            ds_dat = ds(**wdat_dict)
    #
    # -- Compute the seasonal climatology
    climato_dat = clim_average(ds_dat, season)
    #
    # -- If we want to add vectors:
    if add_vectors:
        if 'product' in wdat_dict:
            u_wdat_dict = variable2reference(vectors_u)
            v_wdat_dict = variable2reference(vectors_v)
        else:
            # -- Prepare the dictionaries
            u_wdat_dict = wdat_dict.copy()
            u_wdat_dict.update(dict(variable=vectors_u))
            v_wdat_dict = wdat_dict.copy()
            v_wdat_dict.update(dict(variable=vectors_v))
            if vectors_grid:
                u_wdat_dict.update(dict(grid=vectors_grid))
                v_wdat_dict.update(dict(grid=vectors_grid))
            if vectors_table:
                u_wdat_dict.update(dict(table=vectors_table))
                v_wdat_dict.update(dict(table=vectors_table))
        # -- Compute the climatologies for model
        climato_u_wdat = clim_average(ds(**u_wdat_dict), season)
        climato_v_wdat = clim_average(ds(**v_wdat_dict), season)
        if vectors_u in ocean_variables:
            climato_u_wdat = regridn(climato_u_wdat, cdogrid='r360x180')
            climato_v_wdat = regridn(climato_v_wdat, cdogrid='r360x180')
        # -- Assign vectors_field_u and vectors_field_v depending on the context
        if vectors_field == 'full_field':
            vectors_field_u = climato_u_wdat
            vectors_field_v = climato_v_wdat
    #
    # -- Auxilliary contours
    if add_aux_contours:
        if 'product' in wdat_dict:
            aux_wdat = variable2reference(add_aux_contours['variable'])
        else:
            # -- Get the variable
            aux_wdat_dict = wdat_dict.copy()
            aux_wdat_dict.update(dict(variable=add_aux_contours['variable']))
            if 'grid' in add_aux_contours:
                aux_wdat_dict.update(dict(variable=add_aux_contours['grid']))
                add_aux_contours.pop('grid')
            if 'table' in add_aux_contours:
                aux_wdat_dict.update(dict(variable=add_aux_contours['table']))
                add_aux_contours.pop('table')
        climato_aux_dat = clim_average(ds(**aux_wdat_dict), season)
        aux_plot_params = add_aux_contours.copy()
        aux_plot_params.pop('variable')

    # -- Computing the spatial anomalies if needed (notably for zos)
    if 'spatial_anomalies' in wvar:
        climato_dat = fsub(climato_dat, str(
            cvalue(space_average(climato_dat))))
        wvar.pop('spatial_anomalies')
    #
    # -- If we are working on 3D atmospheric variable, compute the zonal mean
    if is3d(variable) or zonmean_variable:
        climato_dat = zonmean(climato_dat)
        p["forbid_plotmap"]=True
        
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wdat_dict)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    if not title:
        title = build_plot_title(wdat_dict, None)
    else:
        title = replace_keywords_with_values(wdat_dict, title)
        #
    # -- Min, max et mean of the field
    if display_field_stats:
        if safe_mode:
            try:
                field_min = '%s' % (
                    float('%.3g' % (float(cMA(ccdo(climato_dat, operator='fldmin'))[0][0][0]) * scale + offset)))
                field_max = '%s' % (
                    float('%.3g' % (float(cMA(ccdo(climato_dat, operator='fldmax'))[0][0][0]) * scale + offset)))
                field_mean = '%s' % (
                    float('%.3g' % (float(cMA(ccdo(climato_dat, operator='fldmean'))[0][0][0]) * scale + offset)))
                minmaxmean_str = variable + ' min=' + str(field_min) + ' ; max=' + str(field_max) + ' ; mean=' + str(
                    field_mean)
                p.update(dict(gsnLeftString=minmaxmean_str,
                              gsnCenterString=' ',
                              gsnRightString=season))
                title += ' ' + tmp_period
            except:
                print('----> display_field_stats failed')
    else:
        # -- Set the left, center and right strings of the plot
        p.update(dict(gsnLeftString=tmp_period,
                      gsnCenterString=variable,
                      gsnRightString=season))
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable):
        if 'aux_options' in p:
            p.update(
                dict(aux_options=p['aux_options'] + '|cnLineThicknessF=2|cnLineLabelsOn=True'))
        else:
            p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables:
        p.update(dict(mpCenterLonF=200, focus='ocean'))
        if 'meshmask_for_navlon_navlat' in wdat_dict:
            climato_dat = add_nav_lon_nav_lat_from_mesh_mask(climato_dat,
                                                             mesh_mask_file=wdat_dict['meshmask_for_navlon_navlat'])
            cdogrid = 'r720x360'
        if not cdogrid:
            climato_dat = regridn(
                climato_dat, cdogrid='r360x180', option=regrid_option)
        else:
            climato_dat = regridn(
                climato_dat, cdogrid=cdogrid, option=regrid_option)
    elif cdogrid:
        climato_dat = regridn(
            climato_dat, cdogrid=cdogrid, option=regrid_option)
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
        climato_dat = llbox(climato_dat, **domain)
        if 'mpCenterLonF' in p:
            p.pop('mpCenterLonF')
        if proj == 'GLOB':
            p.pop('proj')
    else:
        if not is3d(variable) and not zonmean_variable:
            if 'options' in p:
                if 'gsnAddCyclic' not in options:
                    p.update(dict(options=p['options'] + '|gsnAddCyclic=True'))
            else:
                p.update(dict(options='gsnAddCyclic=True'))
    if 'proj' in p:
        if proj == 'GLOB':
            p.pop('proj')
        else:
            if 'NH' not in p['proj'] and 'SH' not in p['proj']:
                projoptions = 'mpProjection=' + proj
                p.pop('proj')
                if 'options' in p:
                    p.update(dict(options=p['options'] + '|' + projoptions))
                else:
                    p.update(dict(options=projoptions))
    #
    # -- Update p (the plotting parameters) with the dictionary of var
    if isinstance(var, dict):
        # -- If the user wants to pass the isolines with min, max, delta, we remove colors
        if 'delta' in var and 'colors' in p:
            p.pop('colors')
        p.update(wvar)
    #
    # -- Add gray for the missing values
    if shade_missing:
        if 'options' in p:
            p['options'] = p['options'] + '|cnMissingValFillColor=gray'
        else:
            p.update(dict(options='cnMissingValFillColor=gray'))
    # -- gsnStringFontHeightF
    if not 'gsnStringFontHeightF' in p:
        p['gsnStringFontHeightF'] = StringFontHeight
    # -- Call the climaf plot function
    myplot = plot(climato_dat,
                  title=title,
                  # gsnStringFontHeightF=StringFontHeight,
                  **p)
    # -- ... and update the dictionary 'p'
    if add_aux_contours and not add_vectors:
        p.update(aux_plot_params)
        # -- Call the climaf plot function
        myplot = plot(climato_dat, climato_aux_dat, title=title,
                      # gsnStringFontHeightF=StringFontHeight,
                      **p)
    elif add_vectors and not add_aux_contours:
        p.update(vectors_options)
        # -- Call the climaf plot function
        myplot = plot(climato_dat, None, vectors_field_u, vectors_field_v, title=title,
                      # gsnStringFontHeightF=StringFontHeight,
                      **p)
    elif add_vectors and add_aux_contours:
        p.update(vectors_options)
        p.update(aux_plot_params)
        # -- Call the climaf plot function
        myplot = plot(climato_dat, climato_aux_dat, vectors_field_u, vectors_field_v, title=title,
                      # gsnStringFontHeightF=StringFontHeight,
                      **p)
    else:
        # -- Call the climaf plot function
        myplot = plot(climato_dat, title=title,
                      # gsnStringFontHeightF=StringFontHeight,
                      **p)

    #
    #print('climato_dat  = ', cfile(climato_dat))
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


#

# Si on veut proposer l'interpolation 'en ligne', il faut:
# - la proposer pour le modele et pour la ref
# - partir du nom sur niveaux modeles, interpoler, renommer, modifier les axes (si besoin)
# - proposer des niveaux de pression par defaut mais donner la possibilite de changer
# -

def plot_diff(var, model, ref, season='ANM', proj='GLOB', domain={}, add_product_in_title=True,
              ocean_variables=ocean_variables, cdogrid=None, add_climato_contours=False, regrid_option='remapdis', regridding='model_on_ref',
              safe_mode=True, custom_plot_params={}, do_cfile=True, spatial_anomalies=False, shade_missing=False,
              zonmean_variable=False, plot_context_suffix=None, add_vectors=False, add_aux_contours=False,
              display_bias_corr_rmse=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print('var = ', var)
    scale = 1.
    offset = 0.
    grid = None
    table = None
    realm = None
    project_specs = None
    if isinstance(var, dict):
        wvar = var.copy()
        variable = wvar['variable']
        wvar.pop('variable')
        if 'climato_plot_params' in wvar:
            wvar.pop('climato_plot_params')
        if 'diff_plot_params' in wvar:
            wvar.update(wvar['diff_plot_params'])
            wvar.pop('diff_plot_params')
        if 'season' in wvar:
            season = wvar['season']
            wvar.pop('season')
        if 'spatial_anomalies' in wvar:
            spatial_anomalies = wvar['spatial_anomalies']
            wvar.pop('spatial_anomalies')
        if 'regridding' in wvar:
            regridding = wvar['regridding']
            wvar.pop('regridding')
        if 'cdogrid' in wvar:
            cdogrid = wvar['cdogrid']
            wvar.pop('cdogrid')
        if 'proj' in wvar:
            proj = wvar['proj']
            wvar.pop('proj')
        if 'domain' in wvar:
            domain = wvar['domain']
            wvar.pop('domain')
        if 'scale' in wvar:
            scale = wvar['scale']
            wvar.pop('scale')
        if 'offset' in wvar:
            offset = wvar['offset']
            wvar.pop('offset')
        if 'zonmean_variable' in wvar:
            zonmean_variable = wvar['zonmean_variable']
            wvar.pop('zonmean_variable')
        if 'regrid_option' in wvar:
            regrid_option = wvar['regrid_option']
            wvar.pop('regrid_option')
        if 'add_climato_contours' in wvar:
            add_climato_contours = wvar['add_climato_contours']
            wvar.pop('add_climato_contours')
        if 'add_aux_contours' in wvar:
            add_aux_contours = wvar['add_aux_contours'].copy()
            wvar.pop('add_aux_contours')
        if 'plot_context_suffix' in wvar:
            plot_context_suffix = wvar['plot_context_suffix']
            wvar.pop('plot_context_suffix')
        if 'add_product_in_title' in wvar:
            add_product_in_title = wvar['add_product_in_title']
            wvar.pop('add_product_in_title')
        if 'display_bias_corr_rmse' in wvar:
            display_bias_corr_rmse = wvar['display_bias_corr_rmse']
            wvar.pop('display_bias_corr_rmse')
        if 'vectors' in wvar:
            add_vectors = True
            vectors_u = wvar['vectors']['u_comp']
            vectors_v = wvar['vectors']['v_comp']
            if 'grid' in wvar['vectors']:
                vectors_grid = wvar['vectors']['grid']
                wvar['vectors'].pop('grid')
            else:
                vectors_grid = None
            if 'table' in wvar['vectors']:
                vectors_table = wvar['vectors']['table']
                wvar['vectors'].pop('table')
            else:
                vectors_table = None
            vectors_field = 'full_field'
            vectors_options = wvar['vectors'].copy()
            vectors_options.pop('u_comp')
            vectors_options.pop('v_comp')
            if 'context' in vectors_options:
                vectors_options.pop('context')
            print('vectors_options = ', vectors_options)
            wvar.pop('vectors')
        if 'table' in wvar:
            table = wvar['table']
            wvar.pop('table')
        if 'realm' in wvar:
            realm = wvar['realm']
            wvar.pop('realm')
        if 'project_specs' in wvar:
            project_specs = wvar['project_specs']
            wvar.pop('project_specs')
    else:
        variable = var
        wvar = dict()
    #
    # -- Get the datasets of the model and the ref
    wmodel = model.copy()
    wmodel.update(dict(variable=variable))
    # -- Add the gr and table for the CMIP6 datasets
    if 'grid' in wvar:
        wmodel.update(dict(grid=wvar['grid']))
        wvar.pop('grid')
    # if table: wmodel.update(dict(table=table))
    # -- project_specs
    # -- This functionality allows to pass given specifications for one given project => more generic
    if project_specs:
        if wmodel['project'] in project_specs:
            wmodel.update(project_specs[wmodel['project']])
    #
    if 'table' in wmodel:
        table = wmodel['table']
    #
    if table:
        wmodel.update(dict(table=table))
        if 'mon' in table:
            wfreq = 'monthly'
        if 'yr' in table:
            wfreq = 'yearly'
        if 'day' in table:
            wfreq = 'daily'
        if '3hr' in table:
            wfreq = '3hourly'
        if 'frequency' in wmodel:
            if wmodel['frequency'] not in ['seasonal', 'annual_cycle']:
                wmodel.update(dict(frequency=wfreq))
        else:
            wmodel.update(dict(frequency=wfreq))
    if realm:
        wmodel.update(dict(realm=realm))
    #
    # -- Reference
    wref = ref.copy()
    wref.update(dict(variable=variable))
    if project_specs:
        if wref['project'] in project_specs:
            wref.update(project_specs[wref['project']])
    if 'CMIP' in wref['project']:
        if grid:
            wref.update(dict(grid=grid))
        if realm:
            wref.update(dict(realm=realm))
        if project_specs:
            if wref['project'] in project_specs:
                wref.update(project_specs[wref['project']])
        if 'table' in wref:
            table = wref['table']
        if table:
            wref.update(dict(table=table))
    #
    # -- Apply get_period_manager
    wmodel = get_period_manager(wmodel, diag='clim')
    wref = get_period_manager(wref, diag='clim')
    #
    # -- Get the dataset
    ds_model = ds(**wmodel)
    ds_ref = ds(**wref)
    #
    # -- Compute the seasonal climatology of the reference
    if 'season' in ref:
        refseason = ref['season']
    else:
        refseason = season
    climato_ref = clim_average(ds_ref, refseason)
    if 'season' in model:
        modelseason = model['season']
    else:
        modelseason = season
    #
    #
    # -- If we want to add vectors:
    if add_vectors:
        # -- Prepare the dictionaries
        u_wmodel = wmodel.copy()
        u_wmodel.update(dict(variable=vectors_u))
        v_wmodel = wmodel.copy()
        v_wmodel.update(dict(variable=vectors_v))
        if vectors_grid:
            u_wmodel.update(dict(grid=vectors_grid))
            v_wmodel.update(dict(grid=vectors_grid))
        if vectors_table:
            u_wmodel.update(dict(table=vectors_table))
            v_wmodel.update(dict(table=vectors_table))
        if 'product' in wref:
            u_wref = variable2reference(vectors_u)
            v_wref = variable2reference(vectors_v)
        else:
            u_wref = wref.copy()
            u_wref.update(dict(variable=vectors_u))
            v_wref = wref.copy()
            v_wref.update(dict(variable=vectors_v))
            if vectors_grid:
                u_wref.update(dict(grid=vectors_grid))
                v_wref.update(dict(grid=vectors_grid))
            if vectors_table:
                u_wref.update(dict(table=vectors_table))
                v_wref.update(dict(table=vectors_table))
        # -- Compute the climatologies for model and ref
        climato_u_wmodel = clim_average(ds(**u_wmodel), modelseason)
        climato_v_wmodel = clim_average(ds(**v_wmodel), modelseason)
        ref_u_wmodel = clim_average(ds(**u_wref), refseason)
        ref_v_wmodel = clim_average(ds(**v_wref), refseason)
        if vectors_u in ocean_variables:
            climato_u_wmodel = regridn(climato_u_wmodel, cdogrid='r360x180')
            climato_v_wmodel = regridn(climato_v_wmodel, cdogrid='r360x180')
            ref_u_wmodel = regridn(ref_u_wmodel, cdogrid='r360x180')
            ref_v_wmodel = regridn(ref_v_wmodel, cdogrid='r360x180')
        # -- Assign vectors_field_u and vectors_field_v depending on the context
        if vectors_field == 'full_field':
            vectors_field_u = climato_u_wmodel
            vectors_field_v = climato_v_wmodel
        if vectors_field == 'ref':
            vectors_field_u = ref_u_wmodel
            vectors_field_v = ref_v_wmodel
        if vectors_field == 'bias':
            vectors_field_u = diff_regrid(climato_u_wmodel, ref_u_wmodel)
            vectors_field_v = diff_regrid(climato_v_wmodel, ref_v_wmodel)
    #
    # -- Auxilliary contours
    if add_aux_contours:
        # -- Get the variable
        aux_wmodel = wmodel.copy()
        aux_wmodel.update(dict(variable=add_aux_contours['variable']))
        if 'grid' in add_aux_contours:
            aux_wmodel.update(dict(variable=add_aux_contours['grid']))
            add_aux_contours.pop('grid')
        if 'table' in add_aux_contours:
            aux_wmodel.update(dict(variable=add_aux_contours['table']))
            add_aux_contours.pop('table')
        climato_aux_model = clim_average(ds(**aux_wmodel), modelseason)
        aux_plot_params = add_aux_contours.copy()
        aux_plot_params.pop('variable')
    #
    # -- Here we treat two cases:
    #       -> the 3D variables: need to compute the zonal means,
    #          and potentially interpolate on pressure levels with ml2pl
    #       -> the 2D variables:
    #            * only compute the seasonal average for the atmospheric field and regrid the model on the ref
    #              (using diff_regrid)
    #            * for ocean variables, regrid on a 1deg lon/lat grid and compute the difference (using diff_regridn)
    #            * Option: we remove the spatial mean if spatial_anomalies=True (notably for SSH)
    #
    # -- After the vertical interpolation, compute the climatology
    if is3d(variable) or zonmean_variable:
        # -- First case: 3D variable -------------------------------------------- #
        # -- Vertical interpolation (only if needed)
        if 'press_levels' in model:
            # -- To do this the user has to specify 'press_levels' in the dictionary of the dataset, and 'press_var'
            #    if the variable is not 'pres'
            fixed_fields('ml2pl', ('press_levels.txt', model['press_levels']))
            pres_wmodel = wmodel.copy()
            pres_wmodel.pop('variable')
            ds_pres = ds(variable=(
                model['press_var'] if 'press_var' in model else 'pres'), **pres_wmodel)
            print("ds_pres", ds_pres)
            nds_model = ccdo(ds_model, operator='mulc,1')
            nds_pres = ccdo(ds_pres, operator='mulc,1')
            ds_model = ml2pl(nds_model, nds_pres)
        climato_sim = clim_average(ds_model, modelseason)
        # -- Eventually, compute the zonal mean difference
        if safe_mode:
            try:
                if regridding == 'model_on_ref':
                    bias = diff_zonmean(climato_sim, climato_ref)
                    climato_ref = zonmean(climato_ref)
                if regridding == 'ref_on_model':
                    bias = diff_zonmean(climato_ref, climato_sim)
                    climato_ref = zonmean(climato_ref)
                if regridding == 'no_regridding':
                    bias = minus(zonmean(climato_sim), zonmean(climato_ref))
                    climato_ref = zonmean(climato_ref)
            except:
                bias = minus(climato_sim, climato_ref)
                print('No data found for zonal mean for ',
                      climato_ref, climato_sim)
                return blank_cell
        else:
            if regridding == 'model_on_ref':
                bias = diff_zonmean(climato_sim, climato_ref)
            if regridding == 'ref_on_model':
                bias = diff_zonmean(climato_sim, climato_ref)
            if regridding == 'no_regridding':
                bias = minus(zonmean(climato_sim), zonmean(climato_ref))
            climato_ref = zonmean(climato_ref)
    else:
        # -- Alternative: 2D variable ------------------------------------------- #
        climato_sim = clim_average(ds_model, modelseason)
        # -- Particular case of SSH: we compute the spatial anomalies
        if spatial_anomalies:
            try:
                climato_sim = fsub(climato_sim, cscalar(
                    ccdo(climato_sim, operator='fldmean')))
                climato_ref = fsub(climato_ref, cscalar(
                    ccdo(climato_ref, operator='fldmean')))
            except:
                print('==> Error when trying to compute spatial anomalies for ',
                      climato_ref, climato_sim)
                print('==> Check data availability')
                return ''
        # -- If we work on ocean variables, we regrid both the model and the ref on a 1deg grid
        # -- If not, we regrid the model on the ref
        if regridding != 'no_regridding':
            if variable in ocean_variables:
                if 'meshmask_for_navlon_navlat' in wmodel:
                    climato_sim = add_nav_lon_nav_lat_from_mesh_mask(climato_sim,
                                                                     mesh_mask_file=wmodel['meshmask_for_navlon_navlat'])
                if not cdogrid:
                    climato_sim = regrid(
                        climato_sim, climato_ref, option=regrid_option)
                else:
                    climato_sim = regridn(
                        climato_sim, cdogrid=cdogrid, option=regrid_option)
                    climato_ref = regridn(
                        climato_ref, cdogrid=cdogrid, option=regrid_option)
            elif cdogrid:
                climato_sim = regridn(
                    climato_sim, cdogrid=cdogrid, option=regrid_option)
                climato_ref = regridn(
                    climato_ref, cdogrid=cdogrid, option=regrid_option)
            else:
                if regridding == 'ref_on_model':
                    clogger.warning(
                        "Warning in plot_CM_atlas.plot_diff : regridding the reference on the model (and not the model on the reference) ; regridding is set to ref_on_model (in the params file or the diagnostic file)")
                    climato_ref = regrid(climato_ref, climato_sim)
                if regridding == 'model_on_ref':
                    climato_sim = regrid(climato_sim, climato_ref)
        bias = minus(climato_sim, climato_ref)
        if regridding == 'no_regridding' and variable in ocean_variables:
            bias = regridn(bias, cdogrid='r360x180')
    print('bias = ', bias)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    print('add_product_title_in_title in plot_diff = ', str(add_product_in_title))
    print('wmodel before build_plot_title = ', wmodel)
    print('wref before build_plot_title = ', wref)
    title = build_plot_title(wmodel, wref, add_product_in_title)
    #
    # -- Check whether the ref is a model or an obs to set the appropriate context
    context = ('model_model' if 'model' in ds_ref.kvp else 'bias')
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    if plot_context_suffix:
        context = context + '_' + plot_context_suffix
    p = plot_params(variable, context, custom_plot_params=custom_plot_params)
    if is3d(variable) or zonmean_variable:
        p["forbid_plotmap"]=True
    #
    # -- Add the projection
    if 'proj' not in p:
        p.update(dict(proj=proj))
    #
    if isinstance(var, dict):
        if 'options' in wvar:
            options = wvar['options']
            if 'options' in p:
                p['options'] = p['options'] + '|' + options
            else:
                p.update(dict(options=options))
            wvar.pop('options')
        if 'aux_options' in wvar:
            aux_options = wvar['aux_options']
            if 'aux_options' in p:
                p['aux_options'] = p['aux_options'] + '|' + aux_options
            else:
                p.update(dict(aux_options=aux_options))
            wvar.pop('aux_options')
    #
    #
    # -- Set the left, center and right strings of the plot
    if not 'gsnLeftString' in p:
        p['gsnLeftString'] = tmp_period
    if not 'gsnCenterString' in p:
        p['gsnCenterString'] = variable
    if not 'gsnRightString' in p:
        p['gsnRightString'] = modelseason
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable):
        if 'aux_options' in p:
            p.update(
                dict(aux_options=p['aux_options'] + '|cnLineThicknessF=2|cnLineLabelsOn=True'))
        else:
            p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables:
        p.update(dict(mpCenterLonF=200, focus='ocean'))
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
        bias = llbox(bias, **domain)
        climato_sim = llbox(climato_sim, **domain)
        climato_ref = llbox(climato_ref, **domain)
        if 'mpCenterLonF' in p:
            p.pop('mpCenterLonF')
        if proj == 'GLOB':
            p.pop('proj')
    else:
        if not is3d(variable) and not zonmean_variable:
            if 'options' in p:
                p.update(dict(options=p['options'] + '|gsnAddCyclic=True'))
            else:
                p.update(dict(options='gsnAddCyclic=True'))
    if 'proj' in p:
        if p['proj'] == 'GLOB':
            p.pop('proj')
        else:
            if 'NH' not in p['proj'] and 'SH' not in p['proj']:
                projoptions = 'mpProjection=' + p['proj']
                p.pop('proj')
                if 'options' in p:
                    p.update(dict(options=p['options'] + '|' + projoptions))
                else:
                    p.update(dict(options=projoptions))
    #
    # -- Update p (the plotting parameters) with the dictionary of var
    if isinstance(var, dict):
        if 'delta' in var and 'colors' in p:
            p.pop('colors')
        p.update(wvar)
    #
    # -- Add gray for the missing values
    if shade_missing:
        if 'options' in p:
            p['options'] = p['options'] + '|cnMissingValFillColor=gray'
        else:
            p.update(dict(options='cnMissingValFillColor=gray'))
    #
    # -- Get the corresponding plot parameters for the auxillary field (the climatology of the reference)
    refcontext = 'full_field'
    if plot_context_suffix:
        refcontext = refcontext + '_' + plot_context_suffix
    ref_aux_params = plot_params(
        variable, refcontext, custom_plot_params=custom_plot_params)

    # -- Field stats
    if display_bias_corr_rmse:
        if 'scale' in p:
            mscale = float(p['scale'])
        else:
            mscale = scale
        if safe_mode:
            try:
                avg_bias = '%s' % (
                    float('%.3g' % (float(cscalar(ccdo(bias, operator='fldmean'))) * mscale)))
                field_rmse = '%s' % (
                    float('%.3g' % (float(cscalar(rmse_xyt(climato_sim, climato_ref)) * mscale))))
                field_corr = '%s' % (
                    float('%.3g' % (float(cscalar(corr_xy(climato_sim, climato_ref))))))
                stats_str = variable + ' bias=' + str(avg_bias) + ' ; rmse=' + str(field_rmse) + ' ; corr=' + str(
                    field_corr)
                p.update(dict(gsnLeftString=stats_str,
                              gsnCenterString=' ',
                              gsnRightString=season))
                title += ' ' + tmp_period
            except:
                print('----> display_bias_corr_rmse failed')
        else:
            avg_bias = '%s' % (
                float('%.3g' % (float(cscalar(ccdo(bias, operator='fldmean'))) * mscale)))
            field_rmse = '%s' % (
                float('%.3g' % (float(cscalar(rmse_xyt(climato_sim, climato_ref)) * mscale))))
            field_corr = '%s' % (
                float('%.3g' % (float(cscalar(corr_xy(climato_sim, climato_ref))))))
            stats_str = 'bias=' + str(avg_bias) + ' ; rmse=' + str(field_rmse) + ' ; corr=' + str(
                field_corr)
            p.update(dict(gsnRightString=stats_str,
                          gsnCenterString=' ',
                          gsnLeftString=variable+', '+season))
            title += ' ' + tmp_period
    else:
        # -- Set the left, center and right strings of the plot
        if not 'gsnLeftString' in p:
            p['gsnLeftString'] = tmp_period
        if not 'gsnCenterString' in p:
            p['gsnCenterString'] = variable
        if not 'gsnRightString' in p:
            p['gsnRightString'] = season
        # p.update(dict(gsnLeftString=tmp_period,
        #              gsnCenterString=variable,
        #              gsnRightString=season))

        #
        # -- gsnStringFontHeightF
        if not 'gsnStringFontHeightF' in p:
            p['gsnStringFontHeightF'] = StringFontHeight
        #
        # -- Call the climaf plot function
        myplot = plot(bias, climato_ref, title=title,
                      # gsnStringFontHeightF=StringFontHeight,
                      **p)
    # -- ... and update the dictionary 'p'
    # if 'colors' in ref_aux_params and add_climato_contours:
    if add_climato_contours:
        # -- plot_params_aux is a dictionary with plot parameters for the auxiliary field that supercedes the default
        #    plot params
        if 'plot_params_aux' in p:
            ref_aux_params = p['plot_params_aux']
            p.pop('plot_params_aux')
        if 'colors' in ref_aux_params:
            clim_contours = ref_aux_params['colors']
        elif 'min' in ref_aux_params and 'max' in ref_aux_params and 'delta' in ref_aux_params:
            clim_min = float(ref_aux_params['min'])
            clim_max = float(ref_aux_params['max'])
            clim_delta = float(ref_aux_params['delta'])
            clim_contours = ''
            for l in range(min, max + delta, delta):
                clim_contours += (str(l)) + ' '
        #
        p.update(dict(contours=clim_contours))
        # -- We apply the scale and offset with 'offset_aux' and 'scale_aux' to plot the auxillary field
        if 'offset' in ref_aux_params and 'offset_aux' not in p:
            p.update({'offset_aux': ref_aux_params['offset']})
        if 'scale' in ref_aux_params and 'scale_aux' not in p:
            p.update({'scale_aux': ref_aux_params['scale']})
        #
        # -- Call the climaf plot function
        myplot = plot(bias, climato_ref, title=title,
                      **p)

    #
    elif add_aux_contours and not add_vectors:
        p.update(aux_plot_params)
        # -- Call the climaf plot function
        myplot = plot(bias, climato_aux_model, title=title,
                      **p)
    elif add_vectors and not add_aux_contours:
        p.update(vectors_options)
        # -- Call the climaf plot function
        myplot = plot(bias, None, vectors_field_u, vectors_field_v, title=title,
                      **p)
    elif add_vectors and add_aux_contours:
        p.update(vectors_options)
        p.update(aux_plot_params)
        # -- Call the climaf plot function
        myplot = plot(bias, climato_aux_model, vectors_field_u, vectors_field_v, title=title,
                      **p)
    else:
        # -- Call the climaf plot function
        myplot = plot(bias, title=title,
                      **p)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    #print('cfile(bias) = ', cfile(bias))
    print('myplot = ', myplot)
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


thumbnail_size_global = "300*175"
thumbnail_polar_size = "250*250"
thumbnail_size_3d = "250*250"


# -- Function to produce a section of 2D maps (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------

def section_2D_maps(models=[], reference=[], proj='GLOB', season='ANM', variables=[],
                    section_title='Climatology (ref) and bias maps', domain=dict(),
                    safe_mode=True, add_product_in_title=True, shade_missing=False,
                    zonmean_variable=False, ocean_variables=ocean_variables,
                    custom_plot_params={}, custom_obs_dict={}, alternative_dir={},
                    add_line_of_climato_plots=False,
                    thumbnail_size=None, regridding='model_on_ref',
                    do_cfile=True, filename_func=None):
    #
    # -- Upper band at the top of the section
    if do_cfile:
        index = section(section_title, level=4)
    else:
        plots_crs = []
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title = None
        project_specs = None
        w_thumbnail_size = thumbnail_size
        print('\nvar in section_2D_maps = ', var)
        if isinstance(var, dict):
            variable = var['variable']
            if 'zonmean_variable' in var:
                zonmean_variable = var['zonmean_variable']
            if 'season' in var:
                season = var['season']
            if 'line_title' in var:
                line_title = var['line_title']
                var.pop('line_title')
            if 'project_specs' in var:
                project_specs = var['project_specs']
            if 'thumbnail_size' in var:
                w_thumbnail_size = var['thumbnail_size']
                var.pop('thumbnail_size')
        else:
            variable = var
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        if not isinstance(reference, list):
            reference = [reference]
        print('reference => ', reference)
        for ref in reference:
            if ref == 'default':
                var_references.append(ref)
            else:
                if isinstance(ref, dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable'] == variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list, list):
                                    ref_list = [ref_list]
                                var_references = var_references + ref_list
                        else:
                            ref.pop('variable')
                            var_references.append(ref)
        #
        print('var_references = ', var_references)
        for wref in var_references:
            #
            print('Reference wref = ', wref)
            # -- Get the reference (model or obs, reanalysis)
            if wref == 'default':
                ref = variable2reference(variable, my_obs=custom_obs_dict)
                if not ref:
                    ref = dict(project='ref_climatos',
                               frequency='seasonal', table='Amon')
                if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']:
                    ref.update(dict(product='CERES'))
            else:
                ref = wref.copy()
                ref.update(dict(variable=variable))
                if 'table' in var:
                    ref['table'] = var['table']
                if 'grid' in var:
                    ref['grid'] = var['grid']
                if project_specs:
                    if ref['project'] in project_specs:
                        ref.update(project_specs[ref['project']])
                ref = get_period_manager(ref, diag='clim')
            #
            print('custom_obs_dict = ', custom_obs_dict)
            print('ref in plot_climato = ', ref)
            # -- Open the html table of this section
            if do_cfile:
                index += open_table()
            #
            # -- Start the line with the title
            if not line_title:
                wline_title = varlongname(
                    variable) + ' (' + variable + ') ; season = ' + season
            else:
                wline_title = line_title
            # -- Add the reference to the title of the line:
            # --> if we do_cfile, it means that we actually build the html page
            #     If not, we are gathering the crs of all the plots to execute them in parallel
            if do_cfile:
                wline_title += ' ; REF = ' + build_plot_title(ref, None)
                index += open_line(wline_title) + close_line() + close_table()
                index += open_table()
                index += open_line('')
            #
            #
            # -- Set the size of the thumbnail
            # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size
            #    (from params.py)
            # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
            # -> And for the other cases, we set thumbN_size to thumbnail_size
            if w_thumbnail_size:
                thumbN_size = w_thumbnail_size
            else:
                thumbN_size = (thumbnail_size_3d if is3d(
                    variable) or zonmean_variable else thumbnail_size_global)
                if 'SH' in proj or 'NH' in proj:
                    thumbN_size = thumbnail_polar_size
                if 'Satellite' in proj:
                    thumbN_size = '325*300'
            #
            #
            # -- Plot the climatology of the reference and add it to the line
            print('Computing climatology map for ' + variable +
                  ' ' + proj + ' ' + season + ' of ', ref)
            ref_climato = plot_climato(var, ref, season, proj=proj, domain=domain,
                                       custom_plot_params=custom_plot_params,
                                       ocean_variables=ocean_variables,
                                       shade_missing=shade_missing,
                                       safe_mode=safe_mode, do_cfile=do_cfile)
            print('ref_climato = ', ref_climato)
            if do_cfile:
                if filename_func is not None :
                    alternative_dir.update(
                        target_filename = filename_func(ref, None, variable, season))
                print('alternative_dir = ', alternative_dir)
                index += cell("", ref_climato, thumbnail=thumbN_size,
                              hover=hover, **alternative_dir)
            else:
                plots_crs.append(ref_climato)
            #
            # -- Loop on the models and compute the difference against the reference
            for model in models:
                wmodel = model.copy()
                print('Computing bias map for ' + variable +
                      ' ' + proj + ' ' + season + ' of ', model)
                model_diff = plot_diff(var, wmodel, ref, season, proj=proj, domain=domain,
                                       custom_plot_params=custom_plot_params,
                                       ocean_variables=ocean_variables,
                                       safe_mode=safe_mode, add_product_in_title=add_product_in_title,
                                       shade_missing=shade_missing, regridding=regridding,
                                       do_cfile=do_cfile)
                if do_cfile:
                    if filename_func is not None :
                        alternative_dir.update(
                            target_filename = filename_func(wmodel, ref, variable, season))
                    index += cell("", model_diff, thumbnail=thumbN_size,
                                  hover=hover, **alternative_dir)
                else:
                    plots_crs.append(model_diff)
            #
            # -- Close the line
            if do_cfile:
                index += close_line()
                index += close_table()
        #
        # -- Add a line with the climatology plots
        if add_line_of_climato_plots:
            if do_cfile:
                index += open_table() + open_line('')
                # -- Add a blank space to match the columns
                index += cell("", blank_cell, thumbnail=thumbN_size,
                              hover=hover, **alternative_dir)
            for model in models:
                climato_plot = plot_climato(var, model, season, proj=proj, domain=domain,
                                            custom_plot_params=custom_plot_params,
                                            ocean_variables=ocean_variables,
                                            safe_mode=safe_mode, shade_missing=shade_missing,
                                            do_cfile=do_cfile)
                if do_cfile:
                    if filename_func is not None :
                        alternative_dir.update(
                            target_filename = filename_func(model, None, variable, season))
                    index += cell("", climato_plot, thumbnail=thumbN_size,
                                  hover=hover, **alternative_dir)
                else:
                    plots_crs.append(climato_plot)
            #
            #
            if do_cfile:
                index += close_line()
                index += close_table()
    #
    # -- Close the table of the section
    if do_cfile:
        return index
    else:
        return plots_crs


# -- Function to produce a section of 2D maps climatologies (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_climato_2D_maps(models=[], reference=[], proj='GLOB', season='ANM', variables=[],
                            section_title='Climatologies', domain=dict(),
                            safe_mode=True, do_cfile=True, add_product_in_title=True, shade_missing=False,
                            zonmean_variable=False,
                            custom_plot_params={}, custom_obs_dict={}, alternative_dir={},
                            thumbnail_size=None, filename_func=None):
    #
    # -- Upper band at the top of the section
    if do_cfile:
        index = section(section_title, level=4)
    else:
        plots_crs = []
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title = None
        project_specs = None
        print('var in section_climato_2D_maps = ', var)
        if isinstance(var, dict):
            variable = var['variable']
            if 'zonmean_variable' in var:
                zonmean_variable = var['zonmean_variable']
            if 'season' in var:
                season = var['season']
            if 'line_title' in var:
                line_title = var['line_title']
                var.pop('line_title')
            if 'project_specs' in var:
                project_specs = var['project_specs']
        else:
            variable = var
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        #
        if not reference:
            reference = models[0]
            models.remove(models[0])
        #
        if not isinstance(reference, list):
            reference = [reference]
        for ref in reference:
            if ref == 'default':
                var_references.append(ref)
            else:
                if isinstance(ref, dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable'] == variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list, list):
                                    ref_list = [ref_list]
                                var_references = var_references + ref_list
                        else:
                            ref.pop('variable')
                            var_references.append(ref)

        #
        for wref in var_references:
            #
            print('Reference wref = ', wref)
            # -- Get the reference (model or obs, reanalysis)
            if wref == 'default':
                ref = variable2reference(variable, my_obs=custom_obs_dict)
                if not ref:
                    ref = dict(project='ref_climatos')
                if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']:
                    ref.update(dict(product='CERES'))
            else:
                ref = wref.copy()
                ref.update(dict(variable=variable))
                if project_specs:
                    if ref['project'] in project_specs:
                        ref.update(project_specs[ref['project']])
                ref = get_period_manager(ref, diag='clim')
            #
            # -- Open the html table of this section
            index += open_table()
            #
            # -- Start the line with the title
            if not line_title:
                wline_title = varlongname(
                    variable) + ' (' + variable + ') ; season = ' + season
            else:
                wline_title = line_title
            # -- Add the reference to the title of the line:
            print('ref = ', ref)
            wline_title += ' ; REF = ' + build_plot_title(ref, None)
            index += open_line(wline_title) + close_line() + close_table()
            #
            index += open_table()
            index += open_line('')
            #
            # -- Set the size of the thumbnail
            # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size
            #    (from params.py)
            # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
            # -> And for the other cases, we set thumbN_size to thumbnail_size
            if thumbnail_size:
                thumbN_size = thumbnail_size
            else:
                thumbN_size = (thumbnail_size_3d if is3d(
                    variable) or zonmean_variable else thumbnail_size_global)
                if 'SH' in proj or 'NH' in proj:
                    thumbN_size = thumbnail_polar_size
                if 'Satellite' in proj:
                    thumbN_size = '325*300'
            #
            # -- Plot the climatology of the reference and add it to the line
            print('Computing climatology map for ' + variable +
                  ' ' + proj + ' ' + season + ' of ', ref)
            ref_climato = plot_climato(var, ref, season, proj=proj, domain=domain,
                                       custom_plot_params=custom_plot_params,
                                       ocean_variables=ocean_variables,
                                       safe_mode=safe_mode, do_cfile=do_cfile, shade_missing=shade_missing)
            #
            # -- if do_cfile, we return the index; if do_cfile=False, add the CRS of the plot to plots_crs
            print('ref_climato = ', ref_climato)
            if do_cfile:
                if filename_func is not None :
                    alternative_dir.update(
                        target_filename = filename_func(ref, None, variable, season))
                index += cell("", ref_climato, thumbnail=thumbN_size,
                              hover=hover, **alternative_dir)
            else:
                plots_crs.append(ref_climato)
            #
            # -- Loop on the models and compute the difference against the reference
            for model in models:
                print('Computing bias map for ' + variable +
                      ' ' + proj + ' ' + season + ' of ', model)
                model_climato = plot_climato(var, model, season, proj=proj, domain=domain,
                                             custom_plot_params=custom_plot_params,
                                             ocean_variables=ocean_variables,
                                             safe_mode=safe_mode, shade_missing=shade_missing)
                # -- if do_cfile, we return the index; if do_cfile=False, add the CRS of the plot to plots_crs
                if do_cfile:
                    if filename_func is not None :
                        alternative_dir.update(
                            target_filename = filename_func(model, None, variable, season))
                    print('alternative_dir = ',alternative_dir)
                    index += cell("", model_climato, thumbnail=thumbN_size,
                                  hover=hover, **alternative_dir)
                else:
                    plots_crs.append(model_climato)
            #
            # -- Close the line
            index += close_line()
            index += close_table()
    #
    # -- if do_cfile, we return the complete index; if do_cfile=False, we return plots_crs for a parallel execution
    if do_cfile:
        # -- Close the table of the section
        return index
    else:
        return plots_crs


# -- Function to produce a section of 2D maps (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_2D_maps_climobs_bias_modelmodeldiff(
        models, reference, proj, season, variables, section_title, domain,
        safe_mode=True, add_product_in_title=True, shade_missing=False,
        custom_plot_params={}, custom_obs_dict={}, alternative_dir={},
        filename_func=None):
    #
    # -- Upper band at the top of the section
    index = section(section_title, level=4)
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title = None
        print('var in section_2D_maps = ', var)
        if isinstance(var, dict):
            variable = var['variable']
            if 'season' in var:
                season = var['season']
            if 'line_title' in var:
                line_title = var['line_title']
                var.pop('line_title')
        else:
            variable = var
        #
        # -- Set the size of the thumbnail
        # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size (from params.py)
        # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
        # -> And for the other cases, we set thumbN_size to thumbnail_size
        thumbN_size = (thumbnail_size_3d if is3d(
            variable) else thumbnail_size_global)
        if 'SH' in proj or 'NH' in proj:
            thumbN_size = thumbnail_polar_size
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        if not isinstance(reference, list):
            reference = [reference]
        for ref in reference:
            if ref == 'default':
                var_references.append(ref)
            else:
                if isinstance(ref, dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable'] == variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list, list):
                                    ref_list = [ref_list]
                                var_references = var_references + ref_list

        #
        print('var_references = ', var_references)
        for wref in var_references:
            #
            print('Reference wref = ', wref)
            # -- Get the reference (model or obs, reanalysis)
            if wref == 'default':
                ref = variable2reference(variable, my_obs=custom_obs_dict)
                if not ref:
                    ref = dict(project='ref_climatos', frequency='seasonal')
                if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']:
                    ref.update(dict(product='CERES', frequency='seasonal'))
            else:
                ref = wref.copy()
            #
            # -- Plot the climatology of the reference and add it to the line
            print('Computing climatology map for ' + variable +
                  ' ' + proj + ' ' + season + ' of ', ref)
            ref_climato = plot_climato(var, ref, season, proj=proj, domain=domain,
                                       custom_plot_params=custom_plot_params,
                                       ocean_variables=ocean_variables,
                                       safe_mode=safe_mode, shade_missing=shade_missing)
            if ref_climato:
                # -- Open the html table of this section
                index += open_table()
                #
                # -- Start the line with the title
                if not line_title:
                    wline_title = varlongname(
                        variable) + ' (' + variable + ') ; season = ' + season
                else:
                    wline_title = line_title
                # -- Add the reference to the title of the line:
                wline_title += ' ; REF = ' + build_plot_title(ref, None)
                index += open_line(wline_title) + close_line() + close_table()
                #
                index += open_table()
                index += open_line()
                #
                if filename_func is not None :
                    alternative_dir.update(
                        target_filename = filename_func(ref, None, variable, season))
                index += cell("", ref_climato, thumbnail=thumbN_size,
                              hover=hover, **alternative_dir)
                #
                # -- Plot the bias map of the first model
                bias_first_model = plot_diff(var, models[0], ref, season, proj=proj, domain=domain,
                                             custom_plot_params=custom_plot_params,
                                             ocean_variables=ocean_variables,
                                             safe_mode=safe_mode, add_product_in_title=add_product_in_title,
                                             shade_missing=shade_missing)
                if filename_func is not None :
                    alternative_dir.update(
                        target_filename = filename_func(models[0], ref, variable, season))
                index += cell("", bias_first_model, thumbnail=thumbN_size,
                              hover=hover, **alternative_dir)
                # -- Loop on the models and compute the difference against the reference
                if len(models) > 1:
                    for model in models[1:len(models)]:
                        print('Computing bias map for ' + variable +
                              ' ' + proj + ' ' + season + ' of ', model)
                        model_diff = plot_diff(var, model, models[0], season, proj=proj, domain=domain,
                                               custom_plot_params=custom_plot_params,
                                               ocean_variables=ocean_variables,
                                               safe_mode=safe_mode, add_product_in_title=add_product_in_title,
                                               shade_missing=shade_missing)
                        if filename_func is not None :
                            alternative_dir.update(
                                target_filename = filename_func(model, models[0], variable, season))
                        index += cell("", model_diff, thumbnail=thumbN_size,
                                      hover=hover, **alternative_dir)
                #
                # -- Close the line
                index += close_line()
                index += close_table()
                #
            else:
                # -- Start the line with the title
                line_title = "No ref available for " + \
                    varlongname(variable) + ' (' + variable + ')'
                index += open_table()
                index += open_line(line_title)
                close_line()
                index += close_table()
    #
    # -- Close the table of the section
    index += close_table()
    return index


def plot_zonal_profile(variable, model, reference=dict(), season='ANM', domain={}, safe_mode=True, do_cfile=True,
                       minval=None, maxval=None, scale=1., offset=0.):
    #
    # -- Get the arguments
    project_specs = None
    if isinstance(variable, dict):
        if 'season' in variable:
            season = variable['season']
        if 'reference' in variable:
            reference = variable['reference']
        if 'domain' in variable:
            domain = variable['domain']
        if 'min' in variable:
            minval = variable['min']
        if 'max' in variable:
            maxval = variable['max']
        if 'scale' in variable:
            scale = variable['scale']
        if 'offset' in variable:
            offset = variable['offset']
        if 'project_specs' in variable:
            project_specs = variable['project_specs']
        var = variable['variable']
    else:
        var = variable
    #
    # -- If we give a list of models, we treat them as an ensemble
    if not isinstance(model, list):
        models = [model]
    else:
        models = copy.deepcopy(model)
    #
    models_dict = dict()
    model_names = []
    for model in models:
        # -- copy the model dictionary
        wmodel = model.copy()
        #
        # -- Check if the variable is in model; if not, get it from reference; if not, stop
        if 'variable' not in wmodel:
            wmodel.update(dict(variable=var))
        # -- Apply period manager
        if project_specs:
            if wmodel['project'] in project_specs:
                wmodel.update(project_specs[wmodel['project']])
        wmodel = get_period_manager(wmodel, diag='clim')
        dat = ds(**wmodel)
        #
        # -- Compute the climatology
        clim_dat = clim_average(dat, season)
        #
        # -- Extract a domain
        if domain:
            clim_dat = llbox(clim_dat, **domain)
        #
        # -- Compute the zonal average
        offset = 0.
        if 'offset' in variable:
            offset = variable['offset']
        scale = 1.
        if 'scale' in variable:
            scale = variable['scale']
        zmean_dat = ccdo(clim_dat, operator='zonmean')
        #
        # -- Name of the simulation
        simname = build_plot_title(wmodel, None)
        models_dict.update(
            {simname: apply_scale_offset(zmean_dat, scale, offset)})
        model_names.append(simname)
    #
    if len(models) == 1:
        if reference:
            wreference = reference.copy()
            if 'variable' not in wreference:
                wreference.update(dict(variable=var))
            ref = ds(**wreference)
            #
            # -- Compute the climatology
            clim_ref = clim_average(ref, season)
            #
            # -- Extract a domain
            if domain:
                clim_ref = llbox(clim_ref, **domain)
            #
            # -- Compute the zonal average
            zmean_ref = ccdo(clim_ref, operator='zonmean')
            #
            # -- Regrid model on ref
            zmean_dat = regrid(zmean_dat, zmean_ref)
            #
            # -- Reference name
            refname = build_plot_title(wreference, None)
            #
            # -- Build the ensemble
            print('simname, refname = ', simname, refname)
            print('cfile(zmean_dat) = ', cfile(zmean_dat))
            print('cfile(zmean_ref) = ', cfile(zmean_ref))
            models_dict.update({refname: zmean_ref})
            dat4plot = cens(models_dict)
            # dat4plot = cens({simname:zmean_dat, refname:zmean_ref})
            dat4plot.set_order([refname, simname])
        else:
            #
            wreference = None
            dat4plot = cens(models_dict)
        # -- Title
        CenterString = build_plot_title(
            wmodel, wreference) + ' ' + build_period_str(wmodel)
    else:
        dat4plot = cens(models_dict)
        dat4plot.set_order(model_names)
        #
        # -- Title
        CenterString = '-'
    #
    # -- Add the longitudinal range (if not the whole globe)
    if domain:
        var = var + ' ' + domain['lonmin'] + '/' + domain['lonmax'] + 'E'
    #
    # Min and Max
    if minval or maxval:
        minmax = dict(min=minval, max=maxval)
    else:
        minmax = dict()
    #
    # -- Do the plot
    zmean_fig = curves(dat4plot,  # scale=scale, offset=offset,
                       title=" ",
                       lgcols=3,
                       options='tmYROn=True|' + \
                               'tmYRBorderOn=True|' + \
                               'tmYLOn=False|' + \
                               'tmYUseRight=True|' + \
                               'vpXF=0|' + \
                               'vpWidthF=0.66|' + \
                               'vpHeightF=0.33|' + \
                               'tmYRLabelsOn=True|' + \
                               'tmXBLabelFontHeightF=0.018|' + \
                               'tmYLLabelFontHeightF=0.016|' + \
                               'lgLabelFontHeightF=0.018|' + \
                               # 'pmLegendOrthogonalPosF=-0.32|'+\
                               # 'pmLegendParallelPosF=0.|'+\
                               'pmLegendHeightF=0.4|' + \
                               'pmLegendWidthF=0.12|' + \
                               'pmLegendSide=Bottom|' + \
                               'tmXMajorGrid=True|' + \
                               'tmYMajorGrid=True|' + \
                               'tmXMajorGridLineDashPattern=2|' + \
                               'tmYMajorGridLineDashPattern=2|' + \
                               'xyLineThicknessF=8|' + \
                               'gsnLeftString=' + var + '|' + \
                               'gsnCenterString=' + CenterString + '|' + \
                               'gsnRightString=' + season + '|' + \
                               'gsnStringFontHeightF=0.018', **minmax)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(zmean_fig, do_cfile, safe_mode)


# -- Function to produce a section of 2D maps climatologies (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_zonal_profiles(
        models, reference, season, variables, section_title, domain,
        safe_mode=True, custom_obs_dict={}, alternative_dir={},
        filename_func=None):
    #
    # -- Upper band at the top of the section
    index = section(section_title, level=4)
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title = None
        print('var in section_zonal_profiles = ', var)
        if isinstance(var, dict):
            variable = var['variable']
            if 'season' in var:
                season = var['season']
            if 'line_title' in var:
                line_title = var['line_title']
                var.pop('line_title')
        else:
            variable = var
        #
        # -- Get the reference (model or obs, reanalysis)
        if reference == 'default':
            ref = variable2reference(variable, my_obs=custom_obs_dict)
            if not ref:
                ref = dict(project='ref_climatos')
            if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']:
                ref.update(dict(product='CERES'))
        else:
            ref = reference
        #
        # -- Open the html table of this section
        index += open_table()
        #
        # -- Start the line with the title
        if not line_title:
            wline_title = varlongname(
                variable) + ' (' + variable + ') ; season = ' + season
        else:
            wline_title = line_title
        # -- Add the reference to the title of the line:
        if ref:
            wline_title += ' ; REF = ' + build_plot_title(ref, None)
        index += open_line(wline_title) + close_line() + close_table()
        #
        index += open_table()
        index += open_line('')
        #
        # -- Set the size of the thumbnail
        # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size (from params.py)
        # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
        # -> And for the other cases, we set thumbN_size to thumbnail_size
        thumbN_size = "300*250"
        #
        # -- Plot the ensemble
        ens_zonal_profile = plot_zonal_profile(var, models, ref, season, domain=domain,
                                               safe_mode=safe_mode)
        index += cell("", ens_zonal_profile, thumbnail=thumbN_size,
                      hover=hover, **alternative_dir)
        # -- Loop on the models and compute the difference against the reference
        for model in models:
            print('Computing zonal profile for ' +
                  variable + ' ' + season + ' of ', model)
            zonal_profile = plot_zonal_profile(var, model, ref, season, domain=domain,
                                               safe_mode=safe_mode)
            if filename_func is not None :
                alternative_dir.update(
                    target_filename = filename_func(model, ref, variable, season))
            index += cell("", zonal_profile, thumbnail=thumbN_size,
                          hover=hover, **alternative_dir)
        #
        # -- Close the line
        close_line()
        index += close_table()
    #
    # -- Close the table of the section
    return index
