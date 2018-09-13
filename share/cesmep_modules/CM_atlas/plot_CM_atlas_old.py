from climaf.api import *
from climaf.html import *
from reference import variable2reference
from LMDZ_SE_atlas.lmdz_SE import *
from time_manager import *
from climaf.site_settings import atTGCC
from climaf import __path__ as cpath
import os
from climaf import cachedir
import shutil

StringFontHeight=0.019

hover=False

# -- Set a blank space
# -----------------------------------------------------------------------------------
if atTGCC:
   blank_cell=cachedir+'/Empty.png'
elif onCiclad:
   #blank_cell='https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png'
   blank_cell='/prodigfs/ipslfs/dods/jservon/C-ESM-EP/Empty.png'
else:
   blank_cell='https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png'

from climaf.plot.ocean_plot_params import dict_plot_params as ocean_plot_params
ocean_variables=[]
for oceanvar in ocean_plot_params: ocean_variables.append(oceanvar)

def start_line(title):
    tmpindex = open_table()
    tmpindex += open_line(title) + close_line() + close_table()
    tmpindex += open_table()
    tmpindex += open_line()
    return tmpindex



def build_period_str(dat):
    if isinstance(dat,dict):
       ds_dat = ds(**dat)
    else:
       ds_dat = dat
    tmp_period = str(ds_dat.period)
    if 'clim_period' in ds_dat.kvp and str(ds_dat.period)=='fx':
        tmp_period = ds_dat.kvp['clim_period']
    if 'years' in ds_dat.kvp and ds_dat.period=='fx':
        tmp_period = ds_dat.kvp['years']
    return tmp_period

def build_plot_title(model,ref,add_product_in_title=True):
    if not ref: add_product_in_title=False
    ds_model = ds(**model)
    print 'model = ',model
    print 'ds_model.kvp = ',ds_model.kvp
    if 'customname' in model:
        title = model['customname']
    else:
        if 'model' in ds_model.kvp:
           title = ds_model.kvp['model']+' '+ds_model.kvp['simulation']
        else:
           title = ('OBS' if model['project']=='LMDZ_OBS' else ds_model.kvp["product"])
    if add_product_in_title:
        ds_ref = ds(**ref)
        print 'ref = ',ref
        if 'model' in ds_ref.kvp:
            ref_in_title = (ref['customname'] if 'customname' in ref else ds_ref.kvp['model']+' '+ds_ref.kvp['simulation'])
        else:
            ref_in_title = ('OBS' if ref['project']=='LMDZ_OBS' else ds_ref.kvp["product"])
        title = title+' (vs '+ref_in_title+')'
        title = str.replace(title,'*','')
    return title

def safe_mode_cfile_plot(myplot,do_cfile=True,safe_mode=True):
    if not do_cfile:
       return myplot
       #
    else:
       # -- We try to 'cfile' the plot
       if not safe_mode:
          print '-- plot function is not in safe mode --'
          return cfile(myplot)
       else:
          try:
             plot_filename = cfile(myplot)
             print '--> Successfully plotted ',myplot
             return plot_filename
          except:
             # -- In case it didn't work, we try to see if it comes from the availability of the data
             print '!! Plotting failed ',myplot
             print "set clog('debug') and safe_mode=False to identify where the plotting failed"
             return blank_cell







# -- 2D Maps
def plot_climato(var, dat, season, proj='GLOB', domain={}, custom_plot_params={}, do_cfile=True, mpCenterLonF=None,
                 cdogrid='r360x180', regrid_option='remapbil', safe_mode=True, ocean_variables=ocean_variables, spatial_anomalies=False,
                 shade_missing=False, zonmean_variable=False, plot_context_suffix=None, add_vectors=False, add_aux_contours=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print 'var = ',var
    if isinstance(var, dict):
       wvar = var.copy()
       variable = wvar['variable']
       wvar.pop('variable')
       if 'season' in wvar:
           season = wvar['season']
           wvar.pop('season')
       if 'spatial_anomalies' in wvar:
           spatial_anomalies = wvar['spatial_anomalies']
           wvar.pop('spatial_anomalies')
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
           vectors_field = 'full_field'
           vectors_options = wvar['vectors'].copy() ; vectors_options.pop('u_comp') ; vectors_options.pop('v_comp')
           if 'context' in vectors_options: vectors_options.pop('context')
           print 'vectors_options = ', vectors_options
           wvar.pop('vectors')
    else:
       variable = var
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    context='full_field'
    if plot_context_suffix: context = context+'_'+plot_context_suffix
    p = plot_params(variable,context,custom_plot_params=custom_plot_params)
    #
    # -- Add the projection
    if not 'proj' in p:
       p.update(dict(proj=proj))
    #
    if isinstance(var, dict):
       if 'options' in wvar:
           options = wvar['options']
           if 'options' in p:
              p['options']=p['options']+'|'+options
           else:
              p.update(dict(options=options))
           wvar.pop('options')
       if 'aux_options' in wvar:
           aux_options = wvar['aux_options']
           if 'aux_options' in p:
              p['aux_options']=p['aux_options']+'|'+aux_options
           else:
              p.update(dict(aux_options=aux_options))
           wvar.pop('aux_options')
    #
    # -- Add the variable and get the dataset
    wdat = dat.copy()
    wdat.update(dict(variable=variable))
    # -- Apply the frequency and time manager (IGCM_OUT)
    frequency_manager_for_diag(wdat, diag='SE')
    get_period_manager(wdat)
    print wdat
    # -- Get the dataset
    ds_dat = ds(**wdat)
    print 'ds_dat',ds_dat
    #
    # -- Compute the seasonal climatology
    climato_dat = clim_average(ds_dat,season)
    #
    # -- If we want to add vectors:
    if add_vectors:
       if 'product' in wdat:
          u_wdat = variable2reference(vectors_u)
          v_wdat = variable2reference(vectors_v)
       else:
          # -- Prepare the dictionaries
          u_wdat = wdat.copy() ; u_wdat.update(dict(variable=vectors_u))
          v_wdat = wdat.copy() ; v_wdat.update(dict(variable=vectors_v))
       # -- Compute the climatologies for model
       climato_u_wdat = clim_average(ds(**u_wdat), season)
       climato_v_wdat = clim_average(ds(**v_wdat), season)
       if vectors_u in ocean_variables:
          climato_u_wdat = regridn(climato_u_wdat, cdogrid='r360x180')
          climato_v_wdat = regridn(climato_v_wdat, cdogrid='r360x180')
       # -- Assign vectors_field_u and vectors_field_v depending on the context
       if vectors_field=='full_field':
          vectors_field_u = climato_u_wdat
          vectors_field_v = climato_v_wdat
    #
    # -- Auxilliary contours
    if add_aux_contours:
       if 'product' in wdat:
          aux_wdat = variable2reference(add_aux_contours['variable'])
       else:
          # -- Get the variable
          aux_wdat = wdat.copy()
          aux_wdat.update(dict(variable=add_aux_contours['variable']))
       climato_aux_dat = clim_average(ds(**aux_wdat), season)
       aux_plot_params = add_aux_contours.copy()
       aux_plot_params.pop('variable')

    # -- Computing the spatial anomalies if needed (notably for zos)
    if spatial_anomalies: climato_dat = fsub(climato_dat,str(cvalue(space_average(climato_dat))))
    #
    # -- If we are working on 3D atmospheric variable, compute the zonal mean
    if is3d(variable) or zonmean_variable: climato_dat = zonmean(climato_dat)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wdat)
    # 
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wdat, None)
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString   = tmp_period,
                  gsnCenterString = variable,
                  gsnRightString  = season))
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable):
       if 'aux_options' in p:
          p.update(dict(aux_options=p['aux_options']+'|cnLineThicknessF=2|cnLineLabelsOn=True'))
       else:
          p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables:
       p.update(dict( mpCenterLonF=200 ))
       climato_dat = regridn(climato_dat, cdogrid=cdogrid, option=regrid_option)
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
       climato_dat = llbox(climato_dat, **domain)
       if 'mpCenterLonF' in p: p.pop('mpCenterLonF')
       if proj=='GLOB': p.pop('proj')
    else:
       if not is3d(variable) and not zonmean_variable:
          if 'options' in p:
             p.update(dict(options=p['options']+'|gsnAddCyclic=True'))
          else:
             p.update(dict(options='gsnAddCyclic=True'))
    if 'proj' in p:
       if proj=='GLOB':
          p.pop('proj')
       else:
          if 'NH' not in p['proj'] and 'SH' not in p['proj']:
             projoptions='mpProjection='+proj
             p.pop('proj')
             if 'options' in p:
                p.update(dict(options=p['options']+'|'+projoptions))
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
           p['options']=p['options']+'|cnMissingValFillColor=gray'
       else:
           p.update(dict(options='cnMissingValFillColor=gray'))
    # -- Call the climaf plot function
    myplot = plot(climato_dat,
                  title = title,
                  gsnStringFontHeightF = StringFontHeight,
                  **p)
    # -- ... and update the dictionary 'p'
    if add_aux_contours and not add_vectors:
       p.update(aux_plot_params)
       # -- Call the climaf plot function
       myplot = plot(climato_dat,climato_aux_dat,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    elif add_vectors and not add_aux_contours:
       p.update(vectors_options)
       # -- Call the climaf plot function
       myplot = plot(climato_dat,None,vectors_field_u,vectors_field_v,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    elif add_vectors and add_aux_contours:
       p.update(vectors_options)
       p.update(aux_plot_params)
       # -- Call the climaf plot function
       myplot = plot(climato_dat,climato_aux_dat,vectors_field_u,vectors_field_v,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    else:
       # -- Call the climaf plot function
       myplot = plot(climato_dat,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)


    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)
#


def plot_diff(var, model, ref, season='ANM', proj='GLOB', domain={}, add_product_in_title=True,
              ocean_variables=ocean_variables, cdogrid='r360x180', add_climato_contours=False, regrid_option='remapbil',
              safe_mode=True, custom_plot_params={}, do_cfile=True, spatial_anomalies=False, shade_missing=False,
              zonmean_variable=False, plot_context_suffix=None, add_vectors=False, add_aux_contours=False):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    print 'var = ',var
    if isinstance(var, dict):
       wvar = var.copy()
       variable = wvar['variable']
       wvar.pop('variable')
       if 'season' in wvar:
           season = wvar['season']
           wvar.pop('season')
       if 'spatial_anomalies' in wvar:
           spatial_anomalies = wvar['spatial_anomalies']
           wvar.pop('spatial_anomalies')
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
       if 'add_aux_contours' in wvar:
           add_aux_contours = wvar['add_aux_contours'].copy()
           wvar.pop('add_aux_contours')
       if 'plot_context_suffix' in wvar:
           plot_context_suffix = wvar['plot_context_suffix']
           wvar.pop('plot_context_suffix')
       if 'vectors' in wvar:
           add_vectors = True
           vectors_u = wvar['vectors']['u_comp']
           vectors_v = wvar['vectors']['v_comp']
           if 'context' in wvar['vectors']:
               vectors_field = wvar['vectors']['context'] # bias, ref or full_field
               wvar['vectors'].pop('context')
           else:
               vectors_field = 'full_field'
           vectors_options = wvar['vectors'].copy() ; vectors_options.pop('u_comp') ; vectors_options.pop('v_comp')
           print 'vectors_options = ', vectors_options
           wvar.pop('vectors')
    else:
       variable = var
    #
    # -- Get the datasets of the model and the ref
    wmodel = model.copy() ; wmodel.update(dict(variable=variable))
    wref = ref.copy() ; wref.update(dict(variable=variable))
    # -- Apply the frequency and time manager (IGCM_OUT)
    frequency_manager_for_diag(wmodel, diag='SE')
    print 'wmodel 1 = ',wmodel
    get_period_manager(wmodel)
    print 'wmodel 2 = ',wmodel
    frequency_manager_for_diag(wref, diag='SE')
    get_period_manager(wref)
    ds_model = ds(**wmodel)
    ds_ref   = ds(**wref)
    #
    # -- Compute the seasonal climatology of the reference
    if 'season' in ref:
       refseason = ref['season']
    else:
       refseason = season
    climato_ref = clim_average(ds_ref  ,refseason)
    if 'season' in model:
        modelseason = model['season']
    else:
        modelseason = season
    #
    #
    # -- If we want to add vectors:
    if add_vectors:
       # -- Prepare the dictionaries
       u_wmodel = wmodel.copy() ; u_wmodel.update(dict(variable=vectors_u))
       v_wmodel = wmodel.copy() ; v_wmodel.update(dict(variable=vectors_v))
       if 'product' in wref:
          u_wref = variable2reference(vectors_u)
          v_wref = variable2reference(vectors_v)
       else:
          u_wref = wref.copy() ; u_wref.update(dict(variable=vectors_u))
          v_wref = wref.copy() ; v_wref.update(dict(variable=vectors_v))
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
       if vectors_field=='full_field':
          vectors_field_u = climato_u_wmodel
          vectors_field_v = climato_v_wmodel
       if vectors_field=='ref':
          vectors_field_u = ref_u_wmodel
          vectors_field_v = ref_v_wmodel
       if vectors_field=='bias':
          vectors_field_u = diff_regrid(climato_u_wmodel, ref_u_wmodel)
          vectors_field_v = diff_regrid(climato_v_wmodel, ref_v_wmodel)
    #
    # -- Auxilliary contours
    if add_aux_contours:
       # -- Get the variable
       aux_wmodel = wmodel.copy()
       aux_wmodel.update(dict(variable=add_aux_contours['variable']))
       climato_aux_model = clim_average(ds(**aux_wmodel), modelseason)
       aux_plot_params = add_aux_contours.copy()
       aux_plot_params.pop('variable')
    #
    # -- Here we treat two cases:
    #       -> the 3D variables: need to compute the zonal means, 
    #          and potentially interpolate on pressure levels with ml2pl
    #       -> the 2D variables:
    #            * only compute the seasonal average for the atmospheric field and regrid the model on the ref (using diff_regrid)
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
           fixed_fields('ml2pl',('press_levels.txt',model['press_levels']))
           ds_pres = ds(variable=(model['press_var'] if 'press_var' in model else 'pres'), **model)
           nds_model = ccdo(ds_model,operator='mulc,1')
           nds_pres = ccdo(ds_pres,operator='mulc,1')
           ds_model = ml2pl(nds_model,nds_pres)
       climato_sim = clim_average(ds_model,modelseason)
       # -- Eventually, compute the zonal mean difference
       if safe_mode:
          try:
             bias = diff_zonmean(climato_sim,climato_ref)
             climato_ref = zonmean(climato_ref)
          except:
             print 'No data found for zonal mean for ',climato_ref,climato_sim
             return ''
       else:
          bias = diff_zonmean(climato_sim,climato_ref)
          climato_ref = zonmean(climato_ref)
    else:
       # -- Alternative: 2D variable ------------------------------------------- #
       climato_sim = clim_average(ds_model,modelseason)
       # -- Particular case of SSH: we compute the spatial anomalies
       if spatial_anomalies:
          try:
             climato_sim = fsub(climato_sim,str(cvalue(space_average(climato_sim))))
             climato_ref = fsub(climato_ref,str(cvalue(space_average(climato_ref))))
          except:
             print '==> Error when trying to compute spatial anomalies for ',climato_ref,climato_sim
             print '==> Check data availability'
             return ''
       # -- If we work on ocean variables, we regrid both the model and the ref on a 1deg grid
       # -- If not, we regrid the model on the ref
       if variable in ocean_variables:
          bias = diff_regridn(climato_sim,climato_ref,cdogrid=cdogrid, option=regrid_option)
       else:
          bias = diff_regrid(climato_sim,climato_ref)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    print 'add_product_title_in_title in plot_diff = ',str(add_product_in_title)
    title = build_plot_title(wmodel,wref,add_product_in_title)
    #
    # -- Check whether the ref is a model or an obs to set the appropriate context
    context = ('model_model' if 'model' in ds_ref.kvp else 'bias')
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    if plot_context_suffix: context = context+'_'+plot_context_suffix
    p = plot_params(variable,context,custom_plot_params=custom_plot_params)
    #
    # -- Add the projection
    if not 'proj' in p:
       p.update(dict(proj=proj))
    #
    if isinstance(var, dict):
       if 'options' in wvar:
           options = wvar['options']
           if 'options' in p:
              p['options']=p['options']+'|'+options
           else:
              p.update(dict(options=options))
           wvar.pop('options')
       if 'aux_options' in wvar:
           aux_options = wvar['aux_options']
           if 'aux_options' in p:
              p['aux_options']=p['aux_options']+'|'+aux_options
           else:
              p.update(dict(aux_options=aux_options))
           wvar.pop('aux_options')
    #
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString   = tmp_period,
                  gsnCenterString = variable,
                  gsnRightString  = modelseason))
    #
    # -- If the variable is 3d, add the plotting parameters that are specific to the
    # -- zonal mean fields
    if is3d(variable):
       if 'aux_options' in p:
          p.update(dict(aux_options=p['aux_options']+'|cnLineThicknessF=2|cnLineLabelsOn=True'))
       else:
          p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
    #
    # -- If the variable is an ocean variable, set mpCenterLonF=200 (Pacific centered)
    if variable in ocean_variables: p.update(dict(mpCenterLonF=200,focus='ocean'))
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    if domain:
       bias = llbox(bias, **domain)
       if 'mpCenterLonF' in p: p.pop('mpCenterLonF')
       if proj=='GLOB': p.pop('proj')
    else:
       if not is3d(variable) and not zonmean_variable:
          if 'options' in p:
             p.update(dict(options=p['options']+'|gsnAddCyclic=True'))
          else:
             p.update(dict(options='gsnAddCyclic=True'))
    if 'proj' in p:
       if p['proj']=='GLOB':
          p.pop('proj')
       else:
          if 'NH' not in p['proj'] and 'SH' not in p['proj']:
             projoptions='mpProjection='+p['proj']
             p.pop('proj')
             if 'options' in p:
                p.update(dict(options=p['options']+'|'+projoptions))
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
           p['options']=p['options']+'|cnMissingValFillColor=gray'
       else:
           p.update(dict(options='cnMissingValFillColor=gray'))
    #
    # -- Get the corresponding plot parameters for the auxillary field (the climatology of the reference)
    refcontext='full_field'
    if plot_context_suffix: refcontext = refcontext+'_'+plot_context_suffix
    ref_aux_params = plot_params(variable,refcontext,custom_plot_params=custom_plot_params)
    # -- ... and update the dictionary 'p'
    if 'colors' in ref_aux_params and add_climato_contours:
       p.update(dict(contours=ref_aux_params['colors']))
       # -- We apply the scale and offset with 'offset_aux' and 'scale_aux' to plot the auxillary field
       if 'offset' in ref_aux_params: p.update({'offset_aux':ref_aux_params['offset']})
       if 'scale' in ref_aux_params: p.update({'scale_aux':ref_aux_params['scale']})
       #
       # -- Call the climaf plot function
       myplot = plot(bias,climato_ref,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    elif add_aux_contours and not add_vectors:
       p.update(aux_plot_params)
       # -- Call the climaf plot function
       myplot = plot(bias,climato_aux_model,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    elif add_vectors and not add_aux_contours:
       p.update(vectors_options)
       # -- Call the climaf plot function
       myplot = plot(bias,None,vectors_field_u,vectors_field_v,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    elif add_vectors and add_aux_contours:
       p.update(vectors_options)
       p.update(aux_plot_params)
       # -- Call the climaf plot function
       myplot = plot(bias,climato_aux_model,vectors_field_u,vectors_field_v,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    else:
       # -- Call the climaf plot function
       myplot = plot(bias,title = title,
                     gsnStringFontHeightF = StringFontHeight,
                     **p)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)



thumbnail_size="300*175"
thumbnail_polar_size="250*250"
thumbnail_size_3d="250*250"


# -- Function to produce a section of 2D maps (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_2D_maps(models, reference, proj, season, variables, section_title, domain,
                    safe_mode=True, add_product_in_title=True, shade_missing=False, zonmean_variable=False,
                    custom_plot_params={}, custom_obs_dict={}, alternative_dir={}, add_line_of_climato_plots=False):
    #
    # -- Upper band at the top of the section
    index = section(section_title, level=4)
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title=None
        print 'var in section_2D_maps = ', var
        if isinstance(var, dict):
           variable = var['variable']
           if 'zonmean_variable' in var:
              zonmean_variable = var['zonmean_variable']
           if 'season' in var:
              season = var['season']
           if 'line_title' in var:
              line_title = var['line_title']
              var.pop('line_title')
        else:
           variable = var
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        if not isinstance(reference,list): reference = [reference]
        for ref in reference:
            if ref=='default':
                   var_references.append(ref)
            else:
                if isinstance(ref,dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable']==variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list,list): ref_list = [ref_list]
                                var_references = var_references + ref_list
        
        #
        print 'var_references = ',var_references
        for wref in var_references:
           #
           print 'Reference wref = ',wref
           # -- Get the reference (model or obs, reanalysis)
           if wref=='default':
              ref = variable2reference(variable, my_obs = custom_obs_dict)
              if not ref: ref = dict(project='ref_climatos')
              if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']: ref.update(dict(product='CERES'))
           else:
              ref = wref
           #
           # -- Open the html table of this section
           index += open_table()
           #
           # -- Start the line with the title
           if not line_title:
              wline_title = varlongname(variable)+' ('+variable+') ; season = '+season
           else:
              wline_title = line_title
           # -- Add the reference to the title of the line:
           wline_title+=' ; REF = '+build_plot_title(ref, None)
           index += open_line(wline_title) + close_line()+ close_table()
           #
           index += open_table()
           index += open_line('')
           #
           # -- Set the size of the thumbnail
           # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size (from params.py)
           # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
           # -> And for the other cases, we set thumbN_size to thumbnail_size
           thumbN_size = ( thumbnail_size_3d if is3d(variable) or zonmean_variable else thumbnail_size )
           if 'SH' in proj or 'NH' in proj: thumbN_size = thumbnail_polar_size
           if 'Satellite' in proj: thumbN_size = '325*300'
           #
           #
           # -- Plot the climatology of the reference and add it to the line
           print 'Computing climatology map for '+variable+' '+proj+' '+season+' of ', ref
           ref_climato   = plot_climato(var, ref, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                        safe_mode=safe_mode, shade_missing=shade_missing)
           print 'ref_climato = ',ref_climato
           index+=cell("", ref_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           #
           # -- Loop on the models and compute the difference against the reference
           for model in models:
               print 'Computing bias map for '+variable+' '+proj+' '+season+' of ', model
               model_diff = plot_diff(var, model, ref, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                   safe_mode=safe_mode, add_product_in_title=add_product_in_title, shade_missing=shade_missing)#, remapping=remapping)
               index+=cell("", model_diff, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           #
           # -- Close the line
           close_line()
           index += close_table()
        #
        # -- Add a line with the climatology plots
        if add_line_of_climato_plots:
           index+= open_table() + open_line('')
           # -- Add a blank space to match the columns
           index+=cell("", blank_cell, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           for model in models:
               climato_plot = plot_climato(var, model, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                           safe_mode=safe_mode, shade_missing=shade_missing)#, remapping=remapping)
               index+=cell("", climato_plot, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           close_line()
           index += close_table()
        #
    #
    # -- Close the table of the section
    #index += close_table()
    return index



# -- Function to produce a section of 2D maps climatologies (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_climato_2D_maps(models, reference, proj, season, variables, section_title, domain,
                    safe_mode=True, add_product_in_title=True, shade_missing=False, zonmean_variable=False,
                    custom_plot_params={}, custom_obs_dict={}, alternative_dir={}, add_line_of_climato_plots=False):
    #
    # -- Upper band at the top of the section
    index = section(section_title, level=4)
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title=None
        print 'var in section_climato_2D_maps = ', var
        if isinstance(var, dict):
           variable = var['variable']
           if 'zonmean_variable' in var:
              zonmean_variable = var['zonmean_variable']
           if 'season' in var:
              season = var['season']
           if 'line_title' in var:
              line_title = var['line_title']
              var.pop('line_title')
        else:
           variable = var
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        if not isinstance(reference,list): reference = [reference]
        for ref in reference:
            if ref=='default':
                   var_references.append(ref)
            else:
                if isinstance(ref,dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable']==variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list,list): ref_list = [ref_list]
                                var_references = var_references + ref_list
        #
        for wref in var_references:
           #
           print 'Reference wref = ',wref
           # -- Get the reference (model or obs, reanalysis)
           if wref=='default':
              ref = variable2reference(variable, my_obs = custom_obs_dict)
              if not ref: ref = dict(project='ref_climatos')
              if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']: ref.update(dict(product='CERES'))
           else:
              ref = wref
           #
           # -- Open the html table of this section
           index += open_table()
           #
           # -- Start the line with the title
           if not line_title:
              wline_title = varlongname(variable)+' ('+variable+') ; season = '+season
           else:
              wline_title = line_title
           # -- Add the reference to the title of the line:
           wline_title+=' ; REF = '+build_plot_title(ref, None)
           index += open_line(wline_title) + close_line()+ close_table()
           #
           # -- Start the line with the title
           # -- Open the html table of this section
           #index += open_table()
           #if not line_title: line_title = varlongname(variable)+' ('+variable+') ; season = '+season
           #index += open_line(line_title) + close_line()+ close_table()
           #
           index += open_table()
           index += open_line('')
           #
           # -- Set the size of the thumbnail
           # -> If we look at a polar stereographic projection, we set thumbN_size to thumbnail_polar_size (from params.py)
           # -> For a zonal mean field, we set thumbN_size to thumbnail_size_3d (from params.py)
           # -> And for the other cases, we set thumbN_size to thumbnail_size
           thumbN_size = ( thumbnail_size_3d if is3d(variable) or zonmean_variable else thumbnail_size )
           if 'SH' in proj or 'NH' in proj: thumbN_size = thumbnail_polar_size
           if 'Satellite' in proj: thumbN_size = '325*300'
           #
           #if reference:
           #   # -- Get the reference (model or obs, reanalysis)
           #   if reference=='default':
           #      ref = variable2reference(variable, my_obs = custom_obs_dict)
           #      if not ref: ref = dict(project='ref_climatos')
           #      if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']: ref.update(dict(product='CERES'))
           #else:
           #   ref = reference
           #
           # -- Plot the climatology of the reference and add it to the line
           print 'Computing climatology map for '+variable+' '+proj+' '+season+' of ', ref
           ref_climato   = plot_climato(var, ref, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                        safe_mode=safe_mode, shade_missing=shade_missing)
           print 'ref_climato = ',ref_climato
           index+=cell("", ref_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           #
           # -- Loop on the models and compute the difference against the reference
           for model in models:
               print 'Computing bias map for '+variable+' '+proj+' '+season+' of ', model
               model_climato = plot_climato(var, model, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                   safe_mode=safe_mode, shade_missing=shade_missing)#, remapping=remapping)
               index+=cell("", model_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
           #
           # -- Close the line
           close_line()
           index += close_table()
    #
    # -- Close the table of the section
    #index += close_table()
    return index



# -- Function to produce a section of 2D maps (both atmosphere and ocean variables)
# -----------------------------------------------------------------------------------
def section_2D_maps_climobs_bias_modelmodeldiff(models, reference, proj, season, variables, section_title, domain,
                                                safe_mode=True, add_product_in_title=True, shade_missing=False, 
                                                custom_plot_params={}, custom_obs_dict={}, alternative_dir={}):
    #
    # -- Upper band at the top of the section
    index = section(section_title, level=4)
    #
    # -- Open the html table of this section
    #index += open_table()
    #
    # -- Line of titles above the plot
    #index+=open_line('Climatology '+season)+cell('Bias map (first simulation)')+cell('Diff. with first simulation')+close_line()
    #
    # -- Loop on the atmospheric variables (can also include ocean variables)
    for var in variables:
        line_title=None
        print 'var in section_2D_maps = ', var
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
        thumbN_size = ( thumbnail_size_3d if is3d(variable) else thumbnail_size)
        if 'SH' in proj or 'NH' in proj: thumbN_size = thumbnail_polar_size
        #
        ## -- Get the reference (model or obs, reanalysis)
        #if reference=='default':
        #   ref = variable2reference(variable, my_obs = custom_obs_dict)
        #   if not ref: ref = dict(project='ref_climatos')
        #   if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']: ref.update(dict(product='CERES'))
        #else:
        #   ref = reference
        #
        # -- Loop on the references => the user can provide multiple references per variable
        var_references = []
        if not isinstance(reference,list): reference = [reference]
        for ref in reference:
            if ref=='default':
                   var_references.append(ref)
            else:
                if isinstance(ref,dict):
                    if 'variable' not in ref:
                        var_references.append(ref)
                    else:
                        if ref['variable']==variable:
                            if 'reference' in ref:
                                ref_list = ref['reference']
                                if not isinstance(ref_list,list): ref_list = [ref_list]
                                var_references = var_references + ref_list

        #
        print 'var_references = ',var_references
        for wref in var_references:
           #
           print 'Reference wref = ',wref
           # -- Get the reference (model or obs, reanalysis)
           if wref=='default':
              ref = variable2reference(variable, my_obs = custom_obs_dict)
              if not ref: ref = dict(project='ref_climatos')
              if variable in ['albt', 'albs', 'crest', 'crelt', 'crett', 'cress']: ref.update(dict(product='CERES'))
           else:
              ref = wref
           #
           # -- Plot the climatology of the reference and add it to the line
           print 'Computing climatology map for '+variable+' '+proj+' '+season+' of ', ref
           ref_climato   = plot_climato(var, ref, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                        safe_mode=safe_mode, shade_missing=shade_missing)
           if ref_climato:
              # -- Open the html table of this section
              index += open_table()
              #
              # -- Start the line with the title
              if not line_title:
                 wline_title = varlongname(variable)+' ('+variable+') ; season = '+season
              else:
                 wline_title = line_title
              # -- Add the reference to the title of the line:
              wline_title+=' ; REF = '+build_plot_title(ref, None)
              index += open_line(wline_title) + close_line()+ close_table()
              #
              # -- Start the line with the title
              #index += open_table()
              #line_title = varlongname(variable)+' ('+variable+')'
              #index += open_line(line_title) + close_line() + close_table()
              #
              index += open_table()
              index += open_line()
              #
              index+=cell("", ref_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
              #
              # -- Plot the bias map of the first model
              bias_first_model = plot_diff(var, models[0], ref, season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                           safe_mode=safe_mode, add_product_in_title=add_product_in_title, shade_missing=shade_missing)#, remapping=remapping)
              index+=cell("", bias_first_model, thumbnail=thumbN_size, hover=hover, **alternative_dir)
              # -- Loop on the models and compute the difference against the reference
              if len(models)>1:
                 for model in models[1:len(models)]:
                     print 'Computing bias map for '+variable+' '+proj+' '+season+' of ', model
                     model_diff = plot_diff(var, model, models[0], season, proj=proj, domain=domain, custom_plot_params=custom_plot_params,
                                            safe_mode=safe_mode, add_product_in_title=add_product_in_title, shade_missing=shade_missing)#, remapping=remapping)
                     index+=cell("", model_diff, thumbnail=thumbN_size, hover=hover, **alternative_dir)
              #
              # -- Close the line
              close_line()
              index += close_table()
              #
           else:
              # -- Start the line with the title
              line_title = "No ref available for "+varlongname(variable)+' ('+variable+')'
              index += open_table()
              index += open_line(line_title)
              close_line()
              index += close_table()
    #
    # -- Close the table of the section
    index += close_table()
    return index



