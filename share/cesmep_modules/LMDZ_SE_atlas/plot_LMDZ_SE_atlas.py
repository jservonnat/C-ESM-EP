from climaf.api import *
from lmdz_SE import *
#from reference import *

StringFontHeight=0.019




# -----------------------------------------------------------------------
# -- J. Servonnat
# -- 2D Maps
def plot_atmos_climato(variable,dat,season,proj,custom_plot_params={}):
    #
    # -- Add the variable and get th the dataset
    wdat = dat.copy()
    wdat.update(dict(variable=variable))
    print wdat
    ds_dat = ds(**wdat)
    print 'ds_dat',ds_dat
    #
    try:
       # -- Compute the seasonal climatology
       climato_dat = clim_average(ds_dat,season)
       #
       if is3d(variable):
          climato_dat = zonmean(climato_dat)
       #
       if 'clim_period' in dat:
           tmp_period = dat['clim_period']
       elif 'years' in dat:
           tmp_period = dat['years']
       else:
           tmp_period = str(ds_dat.period)
       # -- Plot the field
       if 'customname' in dat:
          title = dat['customname']
       else:
           if 'product' in dat:
              title = ds_dat.kvp['product']
           elif dat['project']=='LMDZ_OBS':
              title = 'OBS '+variable
           else:
              title = ds_dat.kvp['model']+' '+ds_dat.kvp['simulation']
       #
       LeftString = tmp_period
       CenterString = variable
       RightString = season
       p = plot_params(variable,'full_field',custom_plot_params=custom_plot_params)
       if is3d(variable):
          p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
       print 'p = ',p
       myplot = plot(climato_dat,
                     title = title,
                     proj=proj,
                     options='gsnAddCyclic=True',
                     gsnStringFontHeightF = StringFontHeight,
                     gsnRightString  = RightString,
                     gsnCenterString = CenterString,
                     gsnLeftString   = LeftString,
                     **p)
       cfile(myplot)
       return myplot
    except:
       print 'No data for '+variable+' ',dat
       return ''


def plot_atmos_bias(variable,model,ref,season='ANM',proj='GLOB', add_product_in_title=True,
                    custom_plot_params={}, **kwarsg):
    # -- Get the datasets of the model and the ref
    ds_model = ds(variable=variable, **model)
    wref = ref.copy() ; wref.update(dict(variable=variable))
    ds_ref   = ds(**wref)
    # -- Test the availability of the model
    try:
       # -- Compute the seasonal climatology
       climato_ref = clim_average(ds_ref  ,season)
       #
       if is3d(variable):
          # -- Vertical remapping
          if 'press_levels' in model:
             fixed_fields('ml2pl',('press_levels.txt',model['press_levels']))
             ds_pres = ds(variable=(model['press_var'] if 'press_var' in model else 'pres'), **model)
             nds_model = ccdo(ds_model,operator='mulc,1')
             nds_pres = ccdo(ds_pres,operator='mulc,1')
             ds_model = ml2pl(nds_model,nds_pres)
          climato_sim = clim_average(ds_model,season)
          bias = diff_zonmean(climato_sim,climato_ref)
       else:
          # -- Compute the bias map
          climato_sim = clim_average(ds_model,season)
          bias = diff_regrid(climato_sim,climato_ref)
       #
       if 'clim_period' in model:
           tmp_period = model['clim_period']
       elif 'years' in model:
           tmp_period = model['years']
       else:
           tmp_period = str(ds_model.period)
       # -- Plot the field
       if 'customname' in model:
          title = model['customname']
       else:
          title = ds_model.kvp['model']+' '+ds_model.kvp['simulation']
       if add_product_in_title:
          print 'ref = ',ref
          if 'model' in ds_ref.kvp:
              ref_in_title = (ref['customname'] if 'customname' in ref else ds_ref.kvp['model']+' '+ds_ref.kvp['simulation']) 
          else:
              ref_in_title = ('OBS' if ref['project']=='LMDZ_OBS' else ref["product"])
          title = title+' (vs '+ref_in_title+')'
       #
       LeftString = tmp_period
       CenterString = variable
       RightString = season
       # -- Check whether the ref is a model or an obs to set the appropriate context
       context = ('model_model' if 'model' in ds_ref.kvp else 'bias')
       p = plot_params(variable,context,custom_plot_params=custom_plot_params)
       ref_aux_params = plot_params(variable,'full_field',custom_plot_params=custom_plot_params)
       p.update(dict(contours=ref_aux_params['colors']))
       if is3d(variable):
          p.update(dict(aux_options='cnLineThicknessF=2|cnLineLabelsOn=True'))
       # -- We apply the scale and offset with apply_scale_offset()
       if 'offset' in ref_aux_params:
           p.update({'offset_aux':ref_aux_params['offset']})
       if 'scale' in ref_aux_params:
           p.update({'scale_aux':ref_aux_params['scale']})
       myplot = plot(bias,climato_ref,
                  title = title,
                  proj=proj,
                  options='gsnAddCyclic=True',
                  gsnStringFontHeightF = StringFontHeight,
                  gsnRightString  = RightString,
                  gsnCenterString = CenterString,
                  gsnLeftString   = LeftString,
                  **p)
       cfile(myplot)
       return myplot
    except:
       print 'No data for '+variable+' ',model
       return '' 


