from climaf.api import *
from CM_atlas.plot_CM_atlas import *
from CM_atlas.time_manager import *

StringFontHeight = 0.019


def plot_curl(tauu_variable, tauv_variable, curl_variable, dat, season, proj='GLOB', domain={}, custom_plot_params={},
              do_cfile=True, mpCenterLonF=None,
              cdogrid='r360x180', regrid_option='remapbil', safe_mode=True,
              shade_missing=False, plot_context_suffix=None):
    #
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    # -- Processing the variable: if the variable is a dictionary, need to extract the variable
    #    name and the arguments
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    context = 'full_field'
    if plot_context_suffix:
        context = context + '_' + plot_context_suffix
    p = plot_params(curl_variable, context, custom_plot_params=custom_plot_params)
    #
    # -- Add the projection
    if 'proj' not in p:
        p.update(dict(proj=proj))
    #
    # -- Add the variable and get the dataset
    wdat = dat.copy()
    wdat.update(dict(variable=tauu_variable))
    # -- Apply the frequency and time manager (IGCM_OUT)
    wdat = get_period_manager(wdat, diag='clim')
    wdat.pop('variable')
    print wdat
    # -- Get the dataset
    if wdat['frequency'] in ['yearly', '1Y'] and season not in ['ANM']:
        print ' !!! -> Cannot compute seasonal average on yearly data for wdat = ', wdat
        print ' ==> Try with frequency=monthly '
        wdat.update({'frequency': 'monthly'})
    tauu_dat = ds(variable=tauu_variable, **wdat)
    tauv_dat = ds(variable=tauv_variable, **wdat)
    #
    # -- Compute the seasonal climatology
    climato_tauu = clim_average(tauu_dat, season)
    climato_tauv = clim_average(tauv_dat, season)
    #
    mesh_hgr = None
    if 'mesh_hgr' in wdat:
        mesh_hgr = wdat['mesh_hgr']
    elif 'mesh_mask' in wdat:
        print ' --> mesh_hgr not found in wdat; trying mesh_mask '
        mesh_hgr = wdat['mesh_mask']
    elif 'grid' in wdat:
        print ' --> mesh_mask not found in wdat; trying grid '
        mesh_hgr = wdat['grid']
    elif 'gridfile' in wdat:
        print ' --> grid not found in wdat; trying gridfile '
        mesh_hgr = wdat['gridfile']
    else:
        print ' !!! No file found in wdat that can be provided to ccdfcurl as mesh_hgr : ', wdat
    climato_curl = ccdo(ccdfcurl(climato_tauu, climato_tauv, mesh_hgr=mesh_hgr), operator='setvrange,-1000,1000')
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
    p.update(dict(gsnLeftString=tmp_period,
                  gsnCenterString=curl_variable,
                  gsnRightString=season))
    #
    # -- Select a lon/lat box and discard mpCenterLonF (or get it from var)
    climato_curl = regridn(climato_curl, option='remapdis', cdogrid='r360x180')
    if domain:
        climato_curl = llbox(climato_curl, **domain)
        if 'mpCenterLonF' in p:
            p.pop('mpCenterLonF')
        if proj == 'GLOB':
            p.pop('proj')
    else:
        if 'options' in p:
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
    # -- Add gray for the missing values
    if shade_missing:
        if 'options' in p:
            p['options'] = p['options'] + '|cnMissingValFillColor=gray'
        else:
            p.update(dict(options='cnMissingValFillColor=gray'))
    # -- Call the climaf plot function
    myplot = plot(climato_curl,
                  title=title,
                  gsnStringFontHeightF=StringFontHeight,
                  **p)
    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


#


# -- Sea Ice Plots
def plot_sic_climato_with_ref(variable, model, ref, season, proj, add_product_in_title=True,
                              safe_mode=True, custom_plot_params={}, do_cfile=True):
    # -- Get the datasets of the model and the ref
    wmodel = model.copy()
    wmodel['variable'] = variable
    if 'table' not in wmodel:
        if wmodel['project'] in ['CMIP5']:
            wmodel.update(dict(variable=variable, table='OImon'))
        if wmodel['project'] in ['CMIP6','CMIP6CERFACS']:
            wmodel.update(dict(variable=variable, table='SImon'))
    # wmodel.update(dict(variable=variable, table='OImon'))
    wref = ref.copy()
    if wref['project'] in ['CMIP6','CMIP6CERFACS']:
        wref.update(dict(variable=variable, table='SImon'))
    else:
        wref.update(dict(variable=variable, table='OImon'))
    #
    # -- Get the datasets of the model and the ref
    if wmodel['frequency'] in ['yearly', '1Y']:
        wmodel.update(dict(frequency='monthly'))
    # -- Apply the frequency and time manager (IGCM_OUT)
    print 'wmodel in plot_sic_climato_with_ref = ', wmodel
    wmodel = get_period_manager(wmodel, diag='clim')
    wref = get_period_manager(wref, diag='clim')
    # -- Get the datasets
    ds_model = ds(**wmodel)
    ds_ref = ds(**wref)
    #
    # -- Compute the seasonal climatology
    if 'meshmask_for_navlon_navlat' in wmodel:
        climato_sim = regridn(add_nav_lon_nav_lat_from_mesh_mask(clim_average(ds_model, season),
                                                                 mesh_mask_file=wmodel['meshmask_for_navlon_navlat']),
                              cdogrid='r720x360', option='remapdis')
    else:
        climato_sim = regridn(clim_average(ds_model, season), cdogrid='r360x180', option='remapdis')
    # climato_sim = regridn(clim_average(ds_model,season),cdogrid='r180x90')
    climato_ref = clim_average(ds_ref, season)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, wref, add_product_in_title)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    p = plot_params(variable, 'full_field', custom_plot_params=custom_plot_params)
    #
    # -- Add the contour of the ref (sic = 15)
    p.update(dict(contours=15))
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnLeftString=tmp_period,
                  gsnCenterString=variable,
                  gsnRightString=season))
    # -- Do the plot 
    myplot = plot(climato_sim, climato_ref,
                  title=title,
                  proj=proj,
                  gsnStringFontHeightF=StringFontHeight,
                  options='gsnAddCyclic=True',
                  aux_options='cnLineThicknessF=10',
                  **p)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    #
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


def plot_SIV(models, pole, safe_mode=True, do_cfile=True, maxvalNH=4 * 1e4, maxvalSH=2.6 * 1e4, minvalNH=0, minvalSH=0):
    #
    siv_ens_dict = {}
    # -- We loop on the simulations to build an 'ensemble climaf object'
    # -- that will be passed to 'curves'
    for model in models:
        wmodel = model.copy()
        wmodel.update({'table': 'OImon'})
        if wmodel['frequency'] in ['yearly', '1Y']:
            wmodel.update(dict(frequency='monthly'))
        # -- Dealing with the area of the grid cells
        model4area = model.copy()
        model4area.update({'period': 'fx'})
        areavar = 'areacello'
        if 'gridfile' in wmodel:
            if 'varname_area' in wmodel:
                areavar = wmodel['varname_area']
            area = fds(wmodel['gridfile'], variable=areavar, period='fx')
        else:
            area = ds(variable=areavar, **model4area)
        # -- Apply the frequency and time manager (IGCM_OUT)
        wmodel.update(dict(variable='sic'))
        wmodel = get_period_manager(wmodel, diag='clim')
        wmodel.pop('variable')
        # -- Get the sea ice concentration (sic) and sea ice thickness (sit)
        sic = ds(variable='sic', **wmodel)
        sit = ds(variable='sit', **wmodel)
        # -- Multiply sit by sic (after changing sic from % to ratio [0,1])
        tmp_siv = multiply(sit, ccdo(sic, operator='divc,100'))
        # -- Compute the annuel cycle, and multiply by the area of the grid cells
        siv = multiply(annual_cycle(tmp_siv), area)
        # -- Extract the hemispheres and compute the sum
        if pole == 'NH':
            region = dict(lonmin=0, lonmax=360, latmin=30, latmax=90)
        if pole == 'SH':
            region = dict(lonmin=0, lonmax=360, latmin=-90, latmax=-30)

        scyc_siv = ccdo(llbox(siv, **region), operator='fldsum')
        #
        # -- In case you specify a 'customname' for your simulation, it will be used in the plot
        # -- Otherwise we will use the name of the simulation
        # if 'customname' in wmodel:
        #   name_in_plot = wmodel['customname']
        # else:
        #   name_in_plot = wmodel['simulation']
        name_in_plot = build_plot_title(wmodel, None)
        # -- Build the ensemble (update the python dictionnaries that will be given to cens)
        if safe_mode:
            try:
                cfile(scyc_siv)
                siv_ens_dict.update({name_in_plot: scyc_siv})
            except:
                print 'No data to compute SIV for ', model
        else:
            cfile(scyc_siv)
            siv_ens_dict.update({name_in_plot: scyc_siv})

    #
    # -- We check if we have found the data to compute SIV for at least one model
    if not siv_ens_dict:
        print 'No data for any model to compute SIV'
        return ''
    else:
        # -- Build the climaf ensembles
        siv_ensemble = cens(siv_ens_dict)
        # cfile(siv_ensemble)
        # -- First, some options used for both hemispheres
        plot_options = 'vpXF=0|' + \
                       'vpWidthF=0.66|' + \
                       'vpHeightF=0.43|' + \
                       'tmXBLabelFontHeightF=0.016|' + \
                       'tmYLLabelFontHeightF=0.014|' + \
                       'lgLabelFontHeightF=0.016|' + \
                       'tmXMajorGrid=True|' + \
                       'tmYMajorGrid=True|' + \
                       'tmXMajorGridLineDashPattern=2|' + \
                       'tmYMajorGridLineDashPattern=2|' + \
                       'pmLegendSide=Bottom|' + \
                       'xyLineThicknessF=12|' + \
                       'tiYAxisString=Sea Ice Volume|' + \
                       'gsnStringFontHeightF=0.017'
        print 'Plot the Sea Ice Volume for ', models
        # -- And then, do the plots with 'curves'
        if pole == 'NH':
            title = 'Sea Ice Volume Northern Hemisphere'
            minval = minvalNH
            maxval = maxvalNH
        if pole == 'SH':
            title = 'Sea Ice Volume Southern Hemisphere'
            minval = minvalSH
            maxval = maxvalSH
        plot_siv = curves(siv_ensemble, title=title, options=plot_options, scale=1 / 1e9, scale_aux=1 / 1e9, lgcols=1,
                          X_axis='aligned', min=minval, max=maxval)
    #
    # -- If the user doesn't want to do the cfile within plot_diff, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(plot_siv, do_cfile, safe_mode)
