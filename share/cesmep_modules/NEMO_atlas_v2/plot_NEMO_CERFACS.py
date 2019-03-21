from CM_atlas import *
from climaf.netcdfbasics import fileHasVar, fileHasDim, dimsOfFile
#from time_manager import *
#from climaf import cachedir

#########################################################################
# 
# DATE/AUTHOR:
##############
#
# - Original: S. Senesi    CNRM    (10-03-2016)
#      * first atlas template
#      * integration of model_vs_obs_profile_oce, plot_atl_moc, moc_profile_vs_obs_rapid
# - Update:   M.-P. Moine  CERFACS (26-05-2016)
#     * model_profile_vs_obs (prev. model_vs_obs_profile_oce): add box option
#     * new functions: maxmoc_time_serie, hovmoller_drift_profile, index_timeserie
#
# - Update:   M.-P. Moine  CERFACS (22-07-2016)
#     * new functions: region2basin, set_fixed_fields, zonal_mean_slice
#     * vertical_profile (prev. model_profile_vs_obs), index_timeserie, zonal_mean_slice : add 'obs' option

# AMELIORATIONS:
################
#
#  - prevoir l'argument membre
#  - gerer automatiquement pos_grid="T" (depend de la variable)
#  - blinder le fait que certains diags (ex. hovmoller) ont besoin d'un min d'echeances.
#  - arranger les ranges min-max, unites, titres des plots
#  - manque comparaisons aux obs par sous-basin (interpol sur ORCA + cdo/mersh_mask)
#  - ecrire la doc des fonctions
#
#########################################################################



#########################################################################
# Some settings about data used (model and obs)
#########################################################################

# Scaling de la MOC modele pour homogeneite avec obs RAPID
calias("CMIP5","msftmyz",scale=1.e-3)

# Obs de MOC RAPID (Il a fallu bricoler les donnees d'origine pour la dimension time au debut et unlim)
#dataloc(project="ref_climatos",organization="generic",
#        url='/home/esanchez/data_climaf/${variable}_vertical_unlim.nc')
calias(project='ref_climatos',variable='moc',fileVariable='stream_function_mar',filenameVar='moc')

# Useful observations
# (1) Annual Cycles (12 years, 2D fields)
levitus_ac=dict(project="ref_climatos",product='NODC-Levitus',clim_period='*')
woa13_ac=dict(project="ref_climatos",product='WOA13-v2',clim_period='*')
rapid_ac=dict(project="ref_climatos",variable='moc')
# (2) Time Series (N months, 2D fields)
hadisst_ts=dict(project="ref_ts",product='HadISST')#,period=opts.period)
aviso_ts=dict(project="ref_ts",product='AVISO-L4')#,period=opts.period)
oras4_ts=dict(project="ref_ts",product='ORAS4')#,period=opts.period)



# Useful boxes
boxes=dict(gibraltar=dict(name="Gibraltar",domain={"lonmin":-14.,"lonmax":-10.,"latmin":35.4,"latmax":39.}))

#########################################################################
# Useful functions
#########################################################################
def whichORCAGrid(file):
    from climaf.anynetcdf import ncf
    fileobj=ncf(file)
    dims=fileobj.dimensions
    # -- First, scan and try to find y (or Y)
    dimY = None
    if 'y' in dims: dimY = 'y'
    if 'Y' in dims: dimY = 'Y'
    if dimY:
        y_size = dims[dimY].size
    else:
        return 'no y/Y dimension found in '+file
    #
    # -- Identify ORCA grid
    if y_size==149: return 'ORCA2'
    if y_size==292: return 'ORCA1'
    if y_size==332: return 'eORCA1'

def nav_lat_zovarbasin_file(grid, basin=None):
    if onCiclad:
       if basin:
          if grid=='ORCA2': return '-- nav_lat for zonal means TBD for ORCA2 --'
          if grid=='eORCA1': return '/data/igcmg/database/grids/eORCA1.2_nav_lat_zovar'+basin.lower()+'.nc'
       else:
          if grid=='ORCA2': return '-- nav_lat for zonal means TBD for ORCA2 --'
          if grid=='eORCA1': return '/data/igcmg/database/grids/eORCA1.2_nav_lat_zovarbasins.nc'
    else:
       return '-- nav_lat_zovarbasin files have to be defined on this server --'

def build_coordinates_zovarbasin(file):
    dims = dimsOfFile(file)
    for dim in dims[::-1]:
        print dim
        if dim==dims[-1]:
            coordinates = dim
        else:
            if dim.lower() in ['x']: coordinates = coordinates+' nav_lon'
            if dim.lower() in ['y']: coordinates = coordinates+' nav_lat'
            if dim.lower() not in ['x','y']: coordinates = coordinates+' '+dim
    return coordinates

def title_region(region):
    if region=='GLO': return 'Global'
    if region=='ATL': return 'Atlantic'
    if region=='PAC': return 'Pacific'
    if region=='IND': return 'Indian'


#########################################################################
# Basic Climaf scripts
#########################################################################

cscript("rename_depth","ncrename -O -d lev,deptht -v lev,deptht ${in} ${out}")

#########################################################################
# Basic functions
#########################################################################

curves_options = 'vpXF=0|'+\
                 'vpWidthF=0.66|'+\
                 'vpHeightF=0.43|'+\
                 'tmXBLabelFontHeightF=0.016|'+\
                 'tmYLLabelFontHeightF=0.014|'+\
                 'lgLabelFontHeightF=0.016|'+\
                 'tmXMajorGrid=True|'+\
                 'tmYMajorGrid=True|'+\
                 'tmXMajorGridLineDashPattern=2|'+\
                 'tmYMajorGridLineDashPattern=2|'+\
                 'xyLineThicknessF=12|'+\
                 'gsnStringFontHeightF=0.017'


def basename():
    from sys import _getframe
    return (_getframe(1).f_code.co_name)

def region2basin(modelname,region):
	#
    print "=> Calling ***"+basename()+"*** in region "+region+"."
    #
    if modelname=="CNRM-CM5":
	    if region=="ATL": basin=1
	    if region=="PAC": basin=2
	    if region=="GLO": basin=3
    else:
        if region=="GLO": basin=1
        if region=="SOU": basin=2
        if region=="ATL": basin=3
        if region=="PAC": basin=4
        if region=="ARC": basin=5
        if region=="IND": basin=6
        if region=="MED": basin=7
        if region=="BLA": basin=8
        if region=="HUD": basin=9
        if region=="RED": basin=10
    print "=> corresp. region<->basin found:"+region+"<->"+str(basin)
    return(basin)

def set_fixed_fields(cdftool,region,model):
    #
    print "=> Calling ***"+basename()+"*** in region "+region+"."
    #
    # Path des mesh_mask pour les cdftools
    print "set_fixed_fields = "
    print "mask.nc => ",model["path_mesh_mask"]+model["mesh_masks"][region]
    print "mesh_hgr.nc => ",model["path_mesh_mask"]+model["mesh_masks"][region]
    print "mesh_zgr.nc => ",model["path_mesh_mask"]+model["mesh_masks"][region]
    print "new_maskglo.nc => ",model["path_mesh_mask"]+model["mesh_masks"]['ALLBAS']
    fixed_fields(cdftool,\
                ('mask.nc',    model["path_mesh_mask"]+model["mesh_masks"][region]),\
                ('mesh_hgr.nc',model["path_mesh_mask"]+model["mesh_masks"][region]),\
                ('mesh_zgr.nc',model["path_mesh_mask"]+model["mesh_masks"][region]),\
    			('new_maskglo.nc',model["path_mesh_mask"]+model["mesh_masks"]['ALLBAS']))
    return()

def vertical_profile(model,variable,region,obs=None,box=None, apply_period_manager=True): #mpm_note: new in this function: add box option)
    """
    Given two dataset specifications,and an oceanic variable name,
    create a figure for profile for the variable in both sources

    dataset specifications are dictionnaries
    
    specifics: 
     - space averaging uses cdftools for model variable,on grid T
     - obs data are supposed to be an annual cycle

    Example:
    => model=dict(project="CMIP5",model='CNRM-CM5',frequency='mon',
    =>       realm='ocean',table='Omon',
    =>       experiment='historical',period='1980-1981')
    => obs=dict(project="ref_climatos",product='NODC-Levitus',clim_period='*')
    => fig=vertical_profile('thetao',model,obs)

    """
    #
    if obs:
        print "=> Calling ***"+basename()+"*** for "+variable+" from "+model.get("model") \
                              +"/"+model.get("experiment")+"/"+model.get("simulation") \
                              +" and obs "+obs.get("product")+" in "+region+" and box:"
    else:
        print "=> Calling ***"+basename()+"*** for "+variable+" from "+model.get("model") \
                              +"/"+model.get("experiment")+"/"+model.get("simulation") \
                              +" in "+region+" and box:"
    print box
    #
    # -- Apply the frequency and time manager (IGCM_OUT)
    wmodel=model.copy() ; wmodel.update(dict(variable=variable))
    if apply_period_manager:
       frequency_manager_for_diag(wmodel, diag='SE')
       get_period_manager(wmodel)
    #modvar=ds(variable=variable,**model)
    # definir les datasets
    modvar=ds(**wmodel)
    if obs:
        obsvar=ds(**obs)
    # compute temporal means 
    tmean_modvar=ccdo(modvar,operator='timavg -yearmonmean')
    if obs:
        tmean_obsvar=ccdo(obsvar,operator='yearmonmean') 
        tmean_obsvar_interp=regrid(tmean_obsvar,tmean_modvar, option='remapdis')
    # definir les mesh-mask pour les cdftools
    set_fixed_fields(['ccdfmean_profile','ccdfmean_profile_box'],region,model)
    # compute the vertical profiles 
    if not box:
        vertprof_modvar=ccdfmean_profile(tmean_modvar,pos_grid='T')
        if obs:
            vertprof_obsvar=ccdo(tmean_obsvar,operator='mermean -zonmean') # obs profile is simpler to compute,thanks to a regular grid
            #mpm_nok#vertprof_obsvar=ccdfmean_profile(tmean_obsvar_interp,pos_grid='T')
    else:
        domain=box['domain']
        vertprof_modvar=ccdfmean_profile_box(tmean_modvar,pos_grid='T',**domain)
        if obs:
            tmean_obsvar_box=llbox(tmean_obsvar,**domain)
            vertprof_obsvar=ccdo(tmean_obsvar_box,operator='mermean -zonmean')
    # plot 
    if obs:
        if not box:
            plot_profile=plot(vertprof_obsvar,vertprof_modvar,title=region+" "+variable+" .vs. "+obs['product'],
                              y="index",options="gsnLeftString= | tiXAxisString= ",aux_options="xyLineColor='red'",invXY=False,
                              contours=1,color='BlueWhiteOrangeRed')
        else:
            plot_profile=plot(vertprof_obsvar,vertprof_modvar,title=box['name']+" "+variable+" .vs. "+obs['product'], contours=1,color='BlueWhiteOrangeRed', \
                                                              y="index",options="gsnLeftString= | tiXAxisString= ",aux_options="xyLineColor='red'",invXY=False)
    else:
        if not box:
            plot_profile=plot(vertprof_modvar,title=region+" "+variable, contours=1,color='BlueWhiteOrangeRed', \
                                              y="index",options="gsnLeftString= | tiXAxisString= ",aux_options="xyLineColor='red'",invXY=False)
        else:
            plot_profile=plot(vertprof_modvar,title=box['name']+" "+variable, contours=1,color='BlueWhiteOrangeRed', \
                                              y="index",options="gsnLeftString= | tiXAxisString= ",aux_options="xyLineColor='red'",invXY=False)

    return cfile(plot_profile,deep=True)

# Plot un slice de MOC par bassin
def moc_slice(model, region, variable="msftmyz", y='lin', do_cfile=True, safe_mode=True, apply_period_manager=True):
    """ 
    Model is a dict defining the model dataset (except variable)
    """
    #
    #print "=> Calling ***"+basename()+"*** for "+variable+" from "+model.get("model")+"/" \
    #                      +model.get("experiment")+"/"+model.get("simulation")+" in "+region+" region."
    #
    mocvar = 'zomsf'+region.lower()
    # -- Apply the frequency and time manager (IGCM_OUT)
    wmodel=model.copy() ; wmodel.update(dict(variable=mocvar))
    if apply_period_manager:
       frequency_manager_for_diag(wmodel, diag='TS')
       get_period_manager(wmodel)
    tmp = ds(**wmodel)
    if tmp.baseFiles():
       wmoc = regridn( time_average(tmp), cdogrid='r1x90', option='remapdis' )
    else:
       #if isaliased('mocatl')
       # definir le dataset
       # -- Apply the frequency and time manager (IGCM_OUT)
       wmodel=model.copy() ; wmodel.update(dict(variable=variable))
       if apply_period_manager:
          frequency_manager_for_diag(wmodel, diag='TS')
          get_period_manager(wmodel)
       moc_model = ds(**wmodel)
       #
       # calculer la moyenne temporelle
       moc_model_mean = time_average(moc_model)
       #
       # faire la correpondance region<->numero de basin
       basin = region2basin(model['model'], region)
       #
       # extraire le bassin de rang 'basin'
       wmoc = slice(moc_model_mean,dim='x',min=basin,max=basin)
       #
       #options="trXMinF=-30.|"
    #
    # masquer les valeurs 
    wmoc_mask=mask(wmoc,miss=0.0)
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, None)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    #p = plot_params('MOC','full_field',custom_plot_params=custom_plot_params)
    if region.lower()=='glo':
       trXMinF='-85.'
    else:
       trXMinF='-30.'
    p = dict(colors='-20 -18 -16 -14 -12 -10 -8 -6 -4 -3 -2 -1 1 2 3 4 6 8 10 12 14 16 18 20',
             units="Sv", y=y,
             contours=1, color='nrl_sirkes',
             tiMainFontHeightF=0.023,tiMainFont="helvetica-bold",
             gsnStringFontHeightF=0.019,
             options="trXMinF="+trXMinF+"|cnMissingValFillColor=gray|"+\
                     "vpHeightF=0.4|vpWidthF=0.8|"+\
                     "pmLabelBarWidthF=0.075|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.012"
             
             )
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnRightString = tmp_period,
                  gsnLeftString  = "MOC "+region))
    #
    # -- Do the plot
    plot_moc_slice=plot(wmoc, title=title, focus='ocean', **p)
    #
    #return cfile(plot_moc_slice,deep=True)
    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(plot_moc_slice, do_cfile, safe_mode)
    

# Profil de MOC dans un bassin,a une latitude donnee (ex. 26N). Comparaison avec les obs (ex. RAPID)
def moc_profile_vs_obs(model, obs, region, latitude, variable="msftmyz", y='lin', model_color='blue', obs_color='black',
                       xmin=-5, xmax=20, do_cfile=True, safe_mode=True, apply_period_manager=True): 
    """ 
    Model is a dict defining the model dataset (except variable)
    """
    #
    #print "=> Calling ***"+basename()+"***  for "+variable+" from "+model.get("model")+"/"+model.get("experiment") \
    #                                 +"/"+model.get("simulation")+" in "+region+" region."
    #
    # Obs
    moc_obs=ds(**obs)
    # calculer les moyennes temporelles
    moc_obs_mean=time_average(moc_obs)
    #
    # definir les datasets
    # -- Apply the frequency and time manager (IGCM_OUT)
    wmodel=model.copy() ; wmodel.update(dict(variable='zomsfatl'))
    if apply_period_manager:
       frequency_manager_for_diag(wmodel, diag='TS')
       get_period_manager(wmodel)
    tmp = ds(**wmodel)
    #
    work_on_zomsfatl = ( True if tmp.baseFiles() else False )
    if work_on_zomsfatl:
       print '-- Working on variable zomsfatl'
       # --> Fix to add nav_lat to the file
       if not fileHasDim(cfile(tmp),'nav_lat'):
           moc_model = add_nav_lat(tmp, nav_lat_file=nav_lat_zovarbasin_file(grid=whichORCAGrid(cfile(tmp))),
                                   coordinates=build_coordinates_zovarbasin(cfile(tmp)))
       else:
           moc_model = tmp
       # calculer les moyennes temporelles
       moc_model_mean_basin=regridn(time_average(moc_model), cdogrid='r1x360')
       moc_model_mean_basin_mask=mask(moc_model_mean_basin,miss=0.0)
       #moc_model_lat=slice(moc_model_mean_basin_mask,dim='y',min=229,max=229)
    else:
       # -- Apply the frequency and time manager (IGCM_OUT)
       wmodel=model.copy() ; wmodel.update(dict(variable=variable))
       if apply_period_manager:
          frequency_manager_for_diag(wmodel, diag='TS')
          get_period_manager(wmodel)
       moc_model=ds(**wmodel)
       # calculer les moyennes temporelles
       moc_model_mean=time_average(moc_model)
       # faire la correpondance region<->numero de basin
       basin=region2basin(model['model'],region)
       # extraire le bassin Atlantique de la MOC modele
       moc_model_mean_basin=slice(moc_model_mean,dim='x',min=basin,max=basin)
       moc_model_mean_basin_mask=mask(moc_model_mean_basin,miss=0.0)
       #moc_model_lat=slice(moc_model_mean_basin_mask,dim='lat',min=latitude,max=latitude)
    moc_model_lat=slice(moc_model_mean_basin_mask,dim='lat',min=latitude,max=latitude)
    # plot
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, None)+' ('+model_color+')'
    #
    curves_options2 = 'vpXF=0|'+\
                 'vpWidthF=0.66|'+\
                 'vpHeightF=0.43|'+\
                 'tmXBLabelFontHeightF=0.016|'+\
                 'tmYLLabelFontHeightF=0.014|'+\
                 'lgLabelFontHeightF=0.016|'+\
                 'tmXMajorGrid=True|'+\
                 'tmYMajorGrid=True|'+\
                 'tmXMajorGridLineDashPattern=2|'+\
                 'tmYMajorGridLineDashPattern=2|'+\
                 'trXMinF='+str(xmin)+'.|trXMaxF='+str(xmax)+'.|'+\
                 'xyMonoLineThickness=True|xyLineThicknessF=12.|'+\
                 'gsnStringFontHeightF=0.017'

    p = dict(units="Sv", y=y,
             tiMainFontHeightF=0.023,tiMainFont="helvetica-bold",
             gsnStringFontHeightF=0.019,
             options=curves_options2+'|xyMonoLineColor=True|xyLineColor='+model_color,
             aux_options=curves_options2+'|xyMonoLineColor=True|xyLineColor='+obs_color
             )
    #
    #xyLineColor="red"',
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnRightString = tmp_period,
                  gsnLeftString  = region+' MOC at Lat. '+str(latitude)+' .vs. OBS ('+obs_color+')'))

    plot_moc_profile=plot(moc_model_lat, moc_obs_mean, title=title, **p)
    #
    return safe_mode_cfile_plot(plot_moc_profile, do_cfile, safe_mode)

# Time-Serie du max de la MOC demandee dans un bassin,a un latitude donnee (mpm_note: new function)
def maxmoc_time_serie(model, region, latitude, variable="msftmyz", do_cfile=True, safe_mode=True, apply_period_manager=True): 
    """ 
    Model is a dict defining the model dataset (except variable)
    """
    #
    print "model = ",model
    print "region = ",region
    #print "=> Calling ***"+basename()+"***  for "+variable+" from "+model.get("model")+"/"+model.get("experiment") \
    #                                 +"/"+model.get("simulation")+" in "+region+" region."
    # MOC obs
    moc_obs=ds(project="ref_climatos",variable='moc') #mpm_note: emilia ne fait rien des obs ? 
    #
    # definir les datasets
    #
    mocvar = 'zomsf'+region.lower()
    # -- Apply the frequency and time manager (IGCM_OUT)
    wmodel=model.copy() ; wmodel.update(dict(variable=mocvar))
    if apply_period_manager:
       frequency_manager_for_diag(wmodel, diag='TS')
       get_period_manager(wmodel)
    tmp = ds(**wmodel)
    if tmp.baseFiles():
       print '-- Working on variable '+mocvar
       #moc_model_basin = regridn( tmp, cdogrid='r1x360' )
       if not fileHasDim(cfile(tmp),'nav_lat'):
           #tmp_ok = add_nav_lat(tmp,nav_lat_file=nav_lat_zovarbasin_file(grid=whichORCAGrid(cfile(tmp))))
           tmp_ok = add_nav_lat(tmp, nav_lat_file=nav_lat_zovarbasin_file(grid=whichORCAGrid(cfile(tmp))),
                                   coordinates=build_coordinates_zovarbasin(cfile(tmp)))
       else:
           tmp_ok = tmp
       #   latmodel = model.copy()
       #   latmodel.update(dict(frequency='seasonal', clim_period=model['period'].replace('-','_')))
       #   tmplatmodel = ds(variable = mocvar, **latmodel)
       #   if fileHasVar(tmplatmodel,'nav_lat'):
       #      fixed_fields('regridn',('coordinates',tmplatmodel.baseFiles()))
       print ''
       print ''
       print ''
       print 'tmp_ok = ',cfile(tmp_ok)
       print ''
       print ''
       print ''
       moc_model_basin = regridn(tmp_ok, cdogrid='r1x360', option='remapdis')
    else:
       # -- Apply the frequency and time manager (IGCM_OUT)
       wmodel=model.copy() ; wmodel.update(dict(variable='zomsfatl'))
       if apply_period_manager:
          frequency_manager_for_diag(wmodel, diag='TS')
          get_period_manager(wmodel)
       moc_model=ds(**wmodel)
       # faire la correpondance region<->numero de basin
       basin=region2basin(wmodel['model'],region)
       #extraire le bassin Atlantique de la MOC modele
       moc_model_basin=slice(moc_model,dim='x',min=basin,max=basin)
    #extraire la latitude demandee
    moc_model_basin_lat=slice(moc_model_basin,dim='lat',min=latitude,max=latitude)
    #calculer la moyenne annuelle
    moc_model_yr=ccdo(moc_model_basin_lat,operator='yearmean')
    #calculer le max de la MOC a cette latitude
    maxmoc_model_yr=ccdo(moc_model_yr,operator='vertmax')
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, None)
    #
    p = dict(options=curves_options+"|"+\
                     "tiMainFontHeightF=0.023|tiMainFont=helvetica-bold|"+\
                     "gsnStringFontHeightF=0.019|"+\
                     "gsnCenterString=MAX_MOC_at_Lat"+str(latitude)+" "+tmp_period+"|"+\
                     "gsnRightString= |gsnLeftString=Sv "
             )
    plot_maxmoc = curves(maxmoc_model_yr, title=title, **p)
    #
    return safe_mode_cfile_plot(plot_maxmoc, do_cfile, safe_mode)

# Hovmoller des profils de derive d'une varialbe 3D (mpm_note: new function)
def hovmoller_drift_profile(model, variable, region, y='lin', do_cfile=True, safe_mode=True, custom_plot_params={}, apply_period_manager=True): 
    """ 
    Model is a dict defining the model dataset (except variable)
    """
    #
    print "=> Calling ***"+basename()+"*** for "+variable+" from "+model.get("model")+"/"+model.get("experiment") \
                          +" in region "+region+"."
    #
    # definir le dataset
    mod=model.copy()
    mod.update({'variable': variable})
    # -- Apply the frequency and time manager (IGCM_OUT)
    if apply_period_manager:
       frequency_manager_for_diag(mod, diag='TS')
       get_period_manager(mod)
    var_model=ds(**mod)
    # extraire la valeur a t=0
    var_model_t0=slice(var_model,dim='time',min=1,max=1)
    # calculer la moyenne annuelle
    var_model_yr=ccdo(var_model,operator='yearmean')
    # calculer l'anomalie par rapport a t=0
    var_model_yr_anom=minus(var_model_yr,var_model_t0)
    # definir les mesh-mask pour les cdftools
    set_fixed_fields('ccdfmean_profile',region,model)
    print "=> check fixed_fields:"
    print cscripts['ccdfmean_profile'].fixedfields
    # calculer les profils verticaux pour chaque pas de temps
    vertprof_var_model=ccdfmean_profile(var_model_yr_anom,pos_grid='T')
    # plot
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, None)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    #p = plot_params('MOC','full_field',custom_plot_params=custom_plot_params)
    p = dict(min=-0.2,max=0.2,delta=0.02,
             invXY=True,fmt="%Y",
             y=y, contours=1, color='posneg_2',
             tiMainFontHeightF=0.023,tiMainFont="helvetica-bold",
             gsnStringFontHeightF=0.019,
             options=
                     "cnMissingValFillColor=gray|"+\
                     "vpHeightF=0.4|vpWidthF=0.8|"+\
                     "pmLabelBarWidthF=0.075|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.012"
             )
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnRightString = tmp_period,
                  gsnLeftString  = region+" "+variable+" DRIFT (rel. to t0)"))
    #
    # -- Do the plot
    plot_drift=plot(vertprof_var_model, title=title, **p)
    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(plot_drift, do_cfile, safe_mode)



#--- Serie temporelle d'un indice (moyenne 2D ou 3D) (mpm_note: new function)
def index_timeserie(model, variable, region, obs=None, prang=None, do_cfile=True, safe_mode=True, X_axis='real', apply_period_manager=True):
    """ 
    Model is a dict defining the model dataset (except variable)
    """
    #
    if obs:
        print "=> Calling ***"+basename()+"***  for "+variable+" of "+model.get("model")+"/"+model.get("experiment") \
                              +" and obs "+obs.get("product")+" in region "+region+"."
    else:
        print "=> Calling ***"+basename()+"***  for "+variable+" of "+model.get("model")+"/"+model.get("experiment") \
                              +" in region "+region+"."
    #
    # Definir les datasets
    mod=model.copy()
    mod.update({'variable': variable})
    # -- Apply the frequency and time manager (IGCM_OUT)
    if apply_period_manager:
       frequency_manager_for_diag(mod, diag='TS')
       get_period_manager(mod)
    var_model=ds(**mod)
    if obs:
        obse=obs.copy()
        # -- Get the period covered by the model
        model_period = str(var_model.period)
        print 'model_period = ', model_period
        sep_model_period = ( '-' if '-' in model_period else '_' )
        start_year_model = int(str.split(model_period, sep_model_period)[0][0:4])
        end_year_model   = int(str.split(model_period, sep_model_period)[1][0:4])
        # -- Get the period covered by the obs
        obs_period = obse['period']
        sep_obs_period = ( '-' if '-' in model_period else '_' )
        start_year_obs = int(str.split(obs_period, sep_obs_period)[0][0:4])
        end_year_obs   = int(str.split(obs_period, sep_obs_period)[1][0:4])
        # -- Set the commmon period
        if start_year_model>=start_year_obs and end_year_model<=end_year_obs:
           new_obs_period = model_period
        if start_year_model<=start_year_obs and end_year_model>=end_year_obs:
           new_obs_period = model_period
        if start_year_model<=start_year_obs and end_year_model<=end_year_obs:
           new_obs_period = str(start_year_obs)+'-'+str(end_year_model)
        if start_year_model>=start_year_obs and end_year_model>=end_year_obs:
           new_obs_period = str(start_year_model)+'-'+str(end_year_obs)
        if start_year_model>=end_year_obs or end_year_model<=start_year_obs:
           new_obs_period = obs_period
           X_axis='aligned'
        #
        obse.update({'variable': variable, 'period':new_obs_period})
        var_obs=ds(**obse)
    #calculer la moyenne annuelle
    var_model_yr=ccdo(var_model,operator='yearmean')
    if obs: 
        var_obs_yr=ccdo(var_obs,operator='yearmean')
        # interpolation sur la grille modele pour beneficier des masques par bassin et des cdftools
        var_obs_yr_interp=regrid(var_obs_yr,var_model_yr)
    # definir les mesh-mask pour les cdftools
    set_fixed_fields('ccdfmean',region,model)
    #calculer la moyenne spatiale pour chaque pas de temps
    index_model=ccdfmean(var_model_yr,pos_grid='T')
    if obs: 
        #index_obs=ccdo(var_obs_yr,operator='mermean -zonmean')
        index_obs=ccdfmean(var_obs_yr,pos_grid='T')
    #
    # -- Build an ensemble for the multiplot
    if 'customname' in model:
       name_in_plot = model['customname']
    else:
       name_in_plot = model['simulation']
    # plot
    if obs:
        index_to_plot = cens({obse['product']:index_obs, name_in_plot:index_model})
        if prang:
            #plot_index_ts = curves(index_obs, index_model, min=prang["min"], max=prang["max"], X_axis=X_axis,
            plot_index_ts = curves(index_to_plot, min=prang["min"], max=prang["max"], X_axis=X_axis,
                                 title=region+" "+variable+" Index .vs. "+obs['product'],fmt="%Y",
                                 options=curves_options)
        else:
            #plot_index_ts = curves(index_obs, index_model, title=region+" "+variable+" Index  .vs. "+obs['product'],X_axis=X_axis,
            plot_index_ts = curves(index_to_plot, title=region+" "+variable+" Index  .vs. "+obs['product'],X_axis=X_axis,
                                 fmt="%Y", options=curves_options)
    else:
        if prang:
            plot_index_ts = curves(index_model, min=prang["min"],max=prang["max"], X_axis=X_axis,
                                   title=region+" "+variable+" Index",fmt="%Y",
                                   options=curves_options)
        else:
            plot_index_ts = curves(index_model, title=region+" "+variable+" Index", fmt="%Y", X_axis=X_axis,
                                   options=curves_options)
    #
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(plot_index_ts, do_cfile, safe_mode)



# -- Si on utilise les zovarblabla, on doit avoir les obs pretraitees, quelque part...
# -> On ne les utilise que pour zomsfatl
# -> Sinon, on doit avoir exactement les memes moyennes selon i; donc, on pourrait regriller
#    les obs a la volee sur le modele, puis utiliser les CDFtools pour faire la moyenne.
#    Pour cela, il faut identifier la grille
#      - -> soit on propose les obs regrillees => comment est-ce qu'on identifie depuis CliMAF? Un projet a part, ou une modif de ref_climatos?
#           necessite d'identifier automatiquement la grille => faisable
#      - -> 
# -> Salinite et temperature, pour ORCA2, ORCA1, eORCA1, eORCA025 (masks = ceux utilises pour le model)
#
# -> pour le model regrille sur les obs, on fait:
#      - climato sur grille modele + masking + regridding sur obs
#      - climato sur grille obs + masking (mask obs)
#




def zonal_mean_slice(model, variable, basin, season, ref=None, add_product_in_title=True, method='regrid_model_on_ref',
                     custom_plot_params={}, safe_mode=True, do_cfile=True, y='lin', ymin=None, plot_on_latitude=False, horizontal_regridding=True,
                      apply_period_manager=True):
    # -----------------------------------------------------------------------------------------------------------------------------
    # -- 1/ Moyenne zonale du modele:
    #        -> soit on a la variable en moyenne zonale deja calculee (zoblabla)
    #        -> soit on la calcule a partir des masks de bassin definis dans model:
    #              * path_mesh_mask donne le path vers les fichiers
    #              * mesh_masks est un dictionnaire qui pointe le fichier de mask pour chaque bassin (GLO, ATL, PAC, IND et ALLBAS)
    # -- Test pour voir si on a deja les moyennes zonales par bassin dans les variables dispos
    context = 'full_field'
    # -- Si method=='regrid_model_on_obs', on regrille le modele sur la grille de la reference, et on utilisera
    #    les masks de bassin de la reference qui sont dans son repertoire ($bassin_mask.nc)
    #    Cette methode favorise la structure latitudinale de la section (=> gradient eq/pole)
    if method=='regrid_model_on_ref':
       # -- Apply the frequency and time manager (IGCM_OUT)
       wmodel=model.copy() ; wmodel.update(dict(variable=variable))
       if apply_period_manager:
          frequency_manager_for_diag(wmodel, diag='clim')
          get_period_manager(wmodel)
       # -- Get the model data
       model_dat = ds(**wmodel)
       # -- Compute the climatology on the model grid and mask the zeros
       clim_model = clim_average( mask(model_dat, miss=0.0), season)
       #
       # -- Get the reference
       if ref:
          ref.update(dict(variable=variable))
          # -- Get the reference data
          ref_dat = ds(**ref)
          #
          # -- Get the context => model_model or bias
          context = ('bias' if 'product' in ref_dat.kvp else 'model_model')
          #
          # -- Compute the climatology
          clim_ref = clim_average(ref_dat, season)
          #
          # -- Regrid the model on the obs
          if safe_mode:
             try:
                rgrd_clim_model = lonlatvert_interpolation( regrid(clim_model, clim_ref, option='remapdis'), clim_ref, horizontal_regridding=False )
             except:
                print '--> Error in lonlatvert_interpolation( regrid(clim_model, clim_ref, option="remapdis"), clim_ref, horizontal_regridding=False )'
                print '--> Set safe_mode=False to see the error'
                rgrd_clim_model = clim_model
          else:
             rgrd_clim_model = lonlatvert_interpolation( regrid(clim_model, clim_ref, option='remapdis'), clim_ref, horizontal_regridding=False )
             print '----'
             print '----'
             print '----'
             print 'rgrd_clim_model = ',cfile(rgrd_clim_model)
             print 'clim_model = ', cfile(clim_model)
             print 'clim_ref = ', cfile(clim_ref)
             print '----'
             print '----'
             print '----'
          #
          # -- Get the reference mask
          if 'path_mesh_mask' in ref:
             mask_file = ref['path_mesh_mask'] + ref['mesh_masks'][basin]
          else:
             mask_file = os.path.dirname(str.split(ref_dat.baseFiles(),' ')[0])+'/'+basin.lower()+'_mask.nc'
          print '----'
          print '----'
          print '----'
          print '---> mask_file = ', mask_file
          print '----'
          print '----'
          print '----'
          mask_dat = fds( mask_file, variable='mask', period='fx')
          basin_mask = mask( mask_dat, miss=0.0)
          #
          # -- Apply the mask to the model and the ref
          masked_model = multiply(rgrd_clim_model, basin_mask)
          masked_ref   = multiply(clim_ref,   basin_mask)
          #
          if 'product' not in ref:
             masked_model = regridn(masked_model, cdogrid='r360x180', option='remapdis')
             masked_ref   = regridn(masked_ref, cdogrid='r360x180', option='remapdis')
          # -- Compute the zonal means
          ZM_MODEL = zonmean(masked_model)
          ZM_REF   = zonmean(masked_ref)
          #
          #print '==='
          #print '==='
          #print '==='
          #print '=== ZM_MODEL = ',cfile(ZM_MODEL)
          #print '=== ZM_REF = ',cfile(ZM_REF)
          #print '==='
          #print '==='
          #print '==='

          # -- Interpolate vertically and compute the difference
          if safe_mode:
             try:
                ZM_bias = diff_zonmean(ZM_MODEL, ZM_REF)
             except:
                print '--> Error in diff_zonmean(ZM_MODEL, ZM_REF)'
                print '--> Set safe_mode=False to track the error'
                ZM_bias = minus(ZM_MODEL, ZM_REF)
          else:
             ZM_bias = diff_zonmean(ZM_MODEL, ZM_REF)
          # -- Compute the zonal mean for the basin using the obs masks
       else:
          print 'No reference (obs) provided in zonal_mean_slice for method regrid_model_on_obs'
          # -- Get the reference mask
          if 'path_mesh_mask' in model:
             mask_file = model['path_mesh_mask'] + model['mesh_masks'][basin]
          else:
             mask_file = os.path.dirname(str.split(model_dat.baseFiles(),' ')[0])+'/'+basin.lower()+'_mask.nc'
          print 'mask_file = ', mask_file
          mask_dat = fds( mask_file, variable='mask', period='fx')
          basin_mask = mask( mask_dat, miss=0.0)
          #
          # -- Apply the mask to the model and the ref
          masked_model = multiply(clim_model, basin_mask)
          #
          if 'product' not in model:
             masked_model = regridn(masked_model, cdogrid='r360x180', option='remapdis')
          # -- Compute the zonal means
          ZM_MODEL = zonmean(masked_model)
      #
    if method=='regrid_ref_on_model':   
       #
       # -> Cette methode 
       #if variable=='thetao': tmpzonmvar = 'zotem'+region.lower()
       #if variable=='so':     tmpzonmvar = 'zosal'+region.lower()
       # -- Apply the frequency and time manager (IGCM_OUT)
       #wmodel=model.copy() #; wmodel.update(dict(variable=tmpzonmvar))
       #wmodel.update(dict(variable=variable))
       #frequency_manager_for_diag(wmodel, diag='clim')
       #get_period_manager(wmodel)
       #model_dat = ds(**wmodel)  # -> on regarde si ds() trouve un fichier qui correspondn a la variable
       #if tmp.baseFiles():
       #   # --> Fix to add nav_lat to the file
       #   if not fileHasDim(cfile(tmp),'nav_lat'):
       #      zonmean_model = add_nav_lat(tmp, nav_lat_file=nav_lat_zovarbasin_file(grid=whichORCAGrid(cfile(tmp))),
       #                                  coordinates=build_coordinates_zovarbasin(cfile(tmp)))
       #   else:
       #      zonmean_model = tmp
       #   modvar_climato_zonmean_basin = mask(clim_average(zonmean_model, season), miss=0.0)
       #else:
       #
       # -- Apply the frequency and time manager (IGCM_OUT)
       wmodel=model.copy() ; wmodel.update(dict(variable=variable))
       if apply_period_manager:
          frequency_manager_for_diag(wmodel, diag='SE')
          get_period_manager(wmodel)
       model_dat = ds(**wmodel)
       model_clim = ccdo(clim_average(model_dat,season), operator='setctomiss,0')
       if fileHasVar(cfile(model_clim), 'lev'):
          model_clim_ok = rename_depth(model_clim)
       else:
          model_clim_ok = model_clim
       # 
       #   if method=='regrid_model_on_1deg_grid':
       #   # --> In this case, we regrid the model on the obs
       #maskfile = model['path_mesh_mask'] + model['mesh_masks'][basin]
       #wmask = ccdo(fds(maskfile, variable='tmask', period='fx'), operator='setctomiss,0')
       #modvar_climato_masked = multiply(model_clim_ok, wmask)
       #   modvar_rgrd = regridn(modvar_climato_masked, cdogrid='r360x180',option='remapdis')
       #   modvar_climato_zonmean_basin = zonmean(modvar_rgrd)
       #   #
       #else:
       set_fixed_fields('ccdfzonalmean_bas', basin, model)
       # calculer la moyenne zonale pour le bassin choisi
       model_clim_zonmean_basin = ccdfzonalmean_bas(model_clim_ok, point_type='T', basin=str(basin).lower())
       # -- Ajouter les latitudes ici??
       #else:
       ZM_MODEL = model_clim_zonmean_basin
       print '--'
       print '--'
       print '--'
       print 'cfile(ZM_MODEL) = ',cfile(ZM_MODEL)
       print '--'
       print '--'
       print '--'
       #
       # -----------------------------------------------------------------------------------------------------------------------------
       # -- 2/ Moyenne zonale de la ref:
       # --    -> les refs sont fournies avec les masks de bassins; si la ref est un modele,
       #          on peut recuperer path_mesh_mask et mesh_masks (et donc les fichiers de masks de bassins)
       if ref:
          # calculer la climatologie pour la saison choisie
          if 'variable' not in ref: ref.update(dict(variable=variable))
          ref_dat = ds(**ref)
          ref_clim = clim_average(ref_dat, season)
          # -- Check whether the ref is a model or an obs to set the appropriate context
          context = ('bias' if 'product' in ref_dat.kvp else 'model_model')
          # 1. Si le context est 'model_model', on verifie si la variable ne serait pas disponible en moyenne zonale
          #       - si oui, on travaille directement avec celle-ci
          #       - si non, on recupere les masks de bassins
          # 2. Si le context est 'bias', on recupere les masks de bassins qui doivent etre dans le repertoire des obs
          #    A partir des masks, on calcule les moyennes zonales par bassin
          #zovarbas_ref = ref.copy() ; zovarbas.update(dict(variable=tmpzonmvar))
          #tmpref = ds(**zovarbas_ref)  # -> on regarde si ds() trouve un fichier qui correspondn a la variable
          # -- Si on a les variables pre-calculees en moyennes zonales pour le model et les obs, on utilise ces moyennes zonales
          # --> Ok si on utilise WOA13-v2 comme reference
          #if tmpref.baseFiles() and tmp.baseFiles():
          #   ref_clim_zonmean_basin_interp = regridn(mask(clim_average(tmpref, season), miss=0.0), cdogrid='r1x180', option='remapdis')
          #   model_clim_zonmean_basin_interp = regridn(model_clim_zonmean_basin, cdogrid='r1x180', option='remapdis')
          #   ZM_OBS = zonmean_interpolation(ref_clim_zonmean_basin_interp, model_clim_zonmean_basin_interp)
          #   ZM_MODEL = model_clim_zonmean_basin_interp
          #else:
          #   #
          ##   ref_clim = mask(clim_average(ref_dat, season), miss=0.0)
          if fileHasVar(cfile(ref_clim), 'lev'):
             ref_clim_ok = rename_depth(ref_clim)
          else:
             ref_clim_ok = ref_clim
          print "cfile(ref_clim_ok) = ",cfile(ref_clim_ok)
          #
          # -- Si 'ref' est un autre simulation et a des mesh_masks, on les utilisent
          if context=='model_model' and 'mesh_masks' in ref:
             set_fixed_fields('ccdfzonalmean_bas', basin, ref)
             ref_clim_interp = ref_clim_ok
          else:
             # -> Sinon, on regrille 'obs' sur le modele, et on utilise les masks de bassins
             # -> du model pour calculer les moyennes zonales
             #ref_clim_interp = regrid(ref_clim_ok, model_clim_ok, option='remapdis')
             ref_clim_interp = ccdo(ref_clim_ok, operator='remapdis,'+cfile(model_clim_ok))
          test = lonlatvert_interpolation(ref_clim_interp, model_clim_ok, horizontal_regridding=False)
          ref_clim_zonmean_basin = ccdfzonalmean_bas(test, point_type='T', basin=str(basin).lower())
          # calculer la moyenne zonale pour le bassin choisi
          ZM_OBS = zonmean_interpolation(ref_clim_zonmean_basin, model_clim_zonmean_basin, horizontal_regridding=False)
          ZM_bias = minus(ZM_MODEL, ZM_OBS)
        #
        # -- Now compute the difference (bias)
    if method=='regrid_on_1deg':
       print 'Not yet available : ',method

    # Plot
    #
    # -- Get the period for display in the plot: we build a tmp_period string
    # -- Check whether the period is described by clim_period, years or period (default)
    # -- and make a string with it
    tmp_period = build_period_str(wmodel)
    #
    # -- Title of the plot -> If 'customname' is in the dictionary of dat, it will be used
    # -- as the title. If not, it checks whether dat is a reference or a model simulation
    # -- and builds the title
    title = build_plot_title(wmodel, None)# add_product_in_title='') #add_product_in_title)
    #
    # -- Get the default plot parameters with the function 'plot_params'
    # -- We also update with a custom dictionary of params (custom_plot_params) if the user sets one
    p = plot_params(variable+'_zonmean', context, custom_plot_params=custom_plot_params)
    p.update(dict(y=y,
             contours=1,
             tiMainFontHeightF=0.023,tiMainFont="helvetica-bold",
             gsnStringFontHeightF=0.019,
             options="cnMissingValFillColor=gray|trYReverse=True|"+\
                     "vpHeightF=0.4|vpWidthF=0.8|"+\
                     "pmLabelBarWidthF=0.075|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.012|"
             ))
    if ymin: p['options']=p['options']+'|trYMinF='+str(ymin)
    #
    # -- Set the left, center and right strings of the plot
    p.update(dict(gsnRightString = tmp_period,
                  gsnCenterString = variable+' '+method,
	          gsnLeftString  = basin))
    #
    if ref:
        ZM = ZM_bias
    else:
        ZM = ZM_MODEL
    #
    plot_zonmean = plot(ZM, title=title, **p)
    # -- If the user doesn't want to do the cfile within plot_climato, set do_cfile=False
    # -- Otherwise we check if the plot has been done successfully.
    # -- If not, the user can set safe_mode=False and clog('debug') to debug.
    return safe_mode_cfile_plot(plot_zonmean, do_cfile, safe_mode)




