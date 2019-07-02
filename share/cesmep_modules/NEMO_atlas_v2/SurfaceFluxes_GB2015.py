from climaf.api import *
from CM_atlas.plot_CM_atlas import *



def get_product(file):
    dum = str.split(file,'/') ; filename = dum[len(dum)-1] ; dum2 = str.split(filename,'_')
    product = dum2[2]
    return product


def ref_ensemble_GB2015(var):
    """
    Ree products defined in
    Gainusa-Bogdan et al. (2015)

    Default values are:
    - season = 'annual_cycle'
    - statistic = 'mean'

    For 'climatology', the user can choose among the values handled by clim_average (see help(clim_average))
    For 'statistic', the user can choose among 'mean' (uses 'avg' in cdo), 'min' and 'max'
    """
    # -- We get the list of files available in the ref_climatos project for variable var
    # -- From this list, we extract the names (ens_products) of the products to construct an ensemble with eds()
    if region == 'Tropics':
        list_of_ref_files = ['OAFlux','NCEP','NCEP2','CORE2','FSU3','NOCS-v2','J-OFURO2','GSSTFM3','IFREMER',
                             'DFS4.3','TropFlux','DASILVA','HOAPS3','ERAInterim']
    else:
        list_of_ref_files = ['OAFlux','NCEP','NCEP2','CORE2','NOCS-v2','GSSTFM3','J-OFURO2','IFREMER',
                             'DFS4.3','DASILVA','HOAPS3','ERAInterim']
    available_products = ds(project='ref_climatos', variable=var).explore("choices")["product"]

    ens_products = sorted(list(set(list_of_ref_files)&set(available_products)))

    print 'list_of_ref_files => ',list_of_ref_files
    print 'ens_products => ',ens_products
    #
    # -- Get the ensemble of products on project ref_climatos
    ens = eds(project='ref_climatos',product=ens_products, variable=var)



def stat_ref_ensemble_GB2015(var,climatology='annual_cycle',statistic='mean', region='Tropics'):
    """
    Returns a statistic on the ensemble of turbulent fluxes reference products defined in
    Gainusa-Bogdan et al. (2015)
    
    Default values are:
    - season = 'annual_cycle'
    - statistic = 'mean'
    
    For 'climatology', the user can choose among the values handled by clim_average (see help(clim_average))
    For 'statistic', the user can choose among 'mean' (uses 'avg' in cdo), 'min' and 'max'
    """
    # -- We get the list of files available in the ref_climatos project for variable var
    # -- From this list, we extract the names (ens_products) of the products to construct an ensemble with eds()
    if region == 'Tropics':
        list_of_ref_files = ['OAFlux','NCEP','NCEP2','CORE2','FSU3','NOCS-v2','J-OFURO2','GSSTFM3','IFREMER',
                             'DFS4.3','TropFlux','DASILVA','HOAPS3','ERAInterim']
    else:
        list_of_ref_files = ['OAFlux','NCEP','NCEP2','CORE2','NOCS-v2','GSSTFM3','J-OFURO2','IFREMER',
                             'DFS4.3','DASILVA','HOAPS3','ERAInterim']
    available_products = ds(project='ref_climatos', variable=var).explore("choices")["product"]

    ens_products = sorted(list(set(list_of_ref_files)&set(available_products)))

    print 'list_of_ref_files => ',list_of_ref_files
    print 'ens_products => ',ens_products
    #
    # -- Get the ensemble of products on project ref_climatos
    ens = eds(project='ref_climatos',product=ens_products, variable=var)
    #
    # -- Computes the climatologies on each ensemble member for the climatology specified by the user
    if climatology=='annual_cycle':
        ens_clim = ens
    else:
        ens_clim = clim_average(ens,climatology)
    #
    # -- Remapping all the datasets on a 360x180 grid
    rgrd_ens_clim = regridn(ens_clim,cdogrid='r360x180')
    #
    # -> Return the ensemble statistic
    if statistic=='mean':
        return ccdo_ens(rgrd_ens_clim,operator='ensavg')
    if statistic=='min':
        return ccdo_ens(rgrd_ens_clim,operator='ensmin')
    if statistic=='max':
        return ccdo_ens(rgrd_ens_clim,operator='ensmax')


def plot_bias_TurbFlux_vs_GB2015(variable, dat, climatology='ANM', region = 'Tropics', add_product_in_title=True,
                                 custom_plot_params={}, do_cfile=True, safe_mode=True, apply_period_manager=True, **kwargs):
    #
    # -- Add the variable and get the dataset
    print 'function -- dat = ',dat
    wdat = dat.copy()
    wdat.update(dict(variable=variable))
    print wdat
    # -- Apply the frequency and time manager (IGCM_OUT)
    if apply_period_manager:
       frequency_manager_for_diag(wdat, diag='SE')
       get_period_manager(wdat)
    ds_dat = ds(**wdat)
    print 'ds_dat',ds_dat
    #
    var = variable
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    period = build_period_str(wdat)
    #
    # -- Reference mean
    ref_clim = stat_ref_ensemble_GB2015(var,climatology=climatology, region=region)
    #
    # -- Upper and lower ensemble boundary
    max_clim = stat_ref_ensemble_GB2015(var,statistic='max',climatology=climatology, region=region)
    min_clim = stat_ref_ensemble_GB2015(var,statistic='min',climatology=climatology, region=region)
    #
    # -- Regridding and computing the climatological average
    sim_clim = regrid(clim_average(ds_dat,climatology),ref_clim)
    #
    # -- Add a potential offset and scale 
    if 'offset' in kwargs:
        offset = kwargs['offset']
    else:
        offset = 0
    if 'scale' in kwargs:
        scale = kwargs['scale']
    else:
        scale = 1
    wsim_clim = apply_scale_offset(sim_clim,scale,offset)
    #
    # -- Calcul du biais
    bias_clim = minus(wsim_clim,ref_clim)
    #
    # -- Find where the bias is out of the boundaries of the observational spread
    test_sup = ccdo2(wsim_clim,max_clim,operator='gt')
    test_inf = ccdo2(wsim_clim,min_clim,operator='lt')
    test = plus(test_sup,test_inf)
    #
    # -- On fait un mask a partir de la moyenne d'ensemble des obs
    mask = divide(ref_clim,ref_clim)
    #
    # -- Get the plotting parameters with plot_params
    plot_specs = plot_params(var,'bias')
    #
    # -- Build the title
    if 'customname' in dat:
        title = dat['customname']
    else:
        title = ds_dat.model+' '+ds_dat.simulation
    if add_product_in_title:
        title = title+' (vs GB2015)'
    #
    # -- Manage two cases => 1. region=='Tropics' 2. anything else
    if region=='Tropics':
        res   = llbox(multiply(bias_clim,mask),lonmin=0,lonmax=360,latmin=-30,latmax=30)
        ptest = llbox(multiply(test,mask),lonmin=0,lonmax=360,latmin=-30,latmax=30)
        plot_specs.update(dict(title=''))
    else:
        res   = multiply(bias_clim,mask)
        ptest = multiply(test,mask)
        plot_specs.update(dict(title=title))
    #
    # -- options that will be added to plot by the argument 'options'
    options='pmLabelBarWidthF=0.065|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.01|tmXBLabelFontHeightF=0.01|tmYLLabelFontHeightF=0.01'
    #
    # -- Add plotting specifications
    plot_specs.update( dict(focus='ocean', mpCenterLonF=200,
                            tiMainFontHeightF=0.015, shade_above=0.5, aux_options='cnLineThicknessF=3',
                            contours=0.5, shading_options='gsnShadeHigh=17', options=options,
                            gsnStringFontHeightF=0.018,
                            gsnLeftString=period, gsnRightString=climatology, gsnCenterString=var) )

    #
    # -- Do the plot and return with safe_mode_cfile_plot
    myplot = plot(res, ptest, **plot_specs)
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


def plot_climato_TurbFlux_GB2015(variable, dat, climatology='ANM', region='Tropics', 
                                 do_cfile=True, safe_mode=True, custom_plot_params={}, apply_period_manager=True, **kwargs):
    #
    # -- Compute the climatology
    if dat=='GB2015':
        period='1979-2005'
        dat_clim = stat_ref_ensemble_GB2015(variable,climatology=climatology, region=region)
        title='GB2015 ensemble mean'
    else:
        # -- Add the variable and get the dataset
        wdat = dat.copy()
        wdat.update(dict(variable=variable))
        print wdat
        # -- Apply the frequency and time manager (IGCM_OUT)
        if apply_period_manager:
           frequency_manager_for_diag(wdat, diag='SE')
           get_period_manager(wdat)
        print '====> wdat = ',wdat
        ds_dat = ds(**wdat)
        print 'ds_dat',ds_dat
        # -- Get the period for display in the plot: we build a tmp_period string
        # -- Check whether the period is described by clim_period, years or period (default)
        # -- and make a string with it
        period = build_period_str(wdat)
        #
        # -- Compute the climatological average
        dat_clim = clim_average(ds_dat,climatology)
        #
        # -- Build the title
        if 'customname' in dat:
           title = dat['customname']
        else:
           title = ds_dat.model+' '+ds_dat.simulation
    #
    if 'offset' in kwargs:
        offset = kwargs['offset']
    else:
        offset = 0
    if 'scale' in kwargs:
        scale = kwargs['scale']
    else:
        scale = 1
    wdat_clim = apply_scale_offset(dat_clim,scale,offset)
    #
    #
    if region=='Tropics':
        res   = llbox(dat_clim,lonmin=0,lonmax=360,latmin=-30,latmax=30)
        options='pmLabelBarWidthF=0.065|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.01|tmXBLabelFontHeightF=0.01|tmYLLabelFontHeightF=0.01'
        common_plot_specs={'title':'','focus':'ocean','mpCenterLonF':200,
                       'tiMainFontHeightF':0.015,'shade_above':0.5,'aux_options':'cnLineThicknessF=3',
                       'contours':'0.5','shading_options':'gsnShadeHigh=17','options':options,
                       'gsnStringFontHeightF':0.018,
                       'gsnLeftString':period,'gsnRightString':climatology,'gsnCenterString':variable}
    else:
        res   = dat_clim
        options='pmLabelBarWidthF=0.065|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.01|tmXBLabelFontHeightF=0.01|tmYLLabelFontHeightF=0.01'
        common_plot_specs={'title':title,'focus':'ocean','mpCenterLonF':200,
                       'tiMainFontHeightF':0.015,'shade_above':0.5,'aux_options':'cnLineThicknessF=3',
                       'contours':'0.5','shading_options':'gsnShadeHigh=17','options':options,
                       'gsnStringFontHeightF':0.018,
                       'gsnLeftString':period,'gsnRightString':climatology,'gsnCenterString':variable}
    #
    # -- Add the plotting parameters from plot_params
    common_plot_specs.update(plot_params(variable,'full_field', custom_plot_params=custom_plot_params))
    #
    # -- Do the plot and return with safe_mode_cfile_plot
    myplot = plot(res, **common_plot_specs)
    return safe_mode_cfile_plot(myplot, do_cfile, safe_mode)


