# ------------------------------------------------------------------------------------ #
# -- Header of the atlas.py ; import the useful python modules (CliMAF, NEMO_atlas, -- #
# -- and potentially your own stuff stored in my_plot_functions.py in the current   -- #
# -- working directory.                                                             -- #
# ------------------------------------------------------------------------------------ #
from climaf.api import *
from climaf.html import * 
from climaf import cachedir
from CM_atlas import *
from climaf.site_settings import onCiclad, atTGCC
from getpass import getuser
from climaf import __path__ as cpath

# -----------------------------------------------------------------------------------
# --   PART 1: Get the instructions from:
# --              - the default values
# --              - the parameter file (priority 2)
# --              - the command line (priority 1)
# -----------------------------------------------------------------------------------


# -- Description of the atlas
# -----------------------------------------------------------------------------------
desc="\n\nAtlas Comparaisons de simulations (par rapport a une simulation de ref)"


# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser(desc) ; parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("-p", "--params",
                  help="Parameter file for the Coupled Model atlas (.py)",
                  action="store",default="params_couple.py")
parser.add_option("-s", "--season",
                  help="Season for the atlas",
                  action="store",default=None)
parser.add_option("--proj",
                  help="Projection: choose among GLOB, NH30, SH30",
                  action="store",default=None)
parser.add_option("--index_name",
                  help="Name of the html file (atlas)",
                  action="store",default=None)
parser.add_option("--clean_cache",
                  help="Set to 'True' or 'False' to clean the CliMAF cache (default: 'False')",
                  action="store",default='False')
parser.add_option("--datasets_setup",
                  help="Name of the file containing the list of dictionaries describing the datasets",
                  action="store",default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store",default=None)

(opts, args) = parser.parse_args()


# -- Get the default parameters from default_atlas_settings.py -> Priority = default
# -----------------------------------------------------------------------------------
default_file = '/share/default/default_atlas_settings.py'
while not os.path.isfile(os.getcwd()+default_file):
    default_file = '/..'+default_file
execfile(os.getcwd()+default_file)


# -- If we specify a datasets_setup from the command line, we use 'models' from this file
# -----------------------------------------------------------------------------------
if opts.datasets_setup:
   execfile(opts.datasets_setup)


# -- Get the parameters from the param file -> Priority = 2
# -----------------------------------------------------------------------------------
execfile(opts.params)


# -- Get the command line arguments -> Priority = 1
# -----------------------------------------------------------------------------------
if opts.season:
   season = opts.season
if opts.proj:
   proj = opts.proj
if opts.index_name:
   index_name = opts.index_name
if opts.clean_cache:
   clean_cache = opts.clean_cache



# -- Add the season to the html file name
# -----------------------------------------------------------------------------------
if not index_name:
   tmp_param_filename = str.split(opts.params,'/')
   index_name = str.replace(tmp_param_filename[len(tmp_param_filename)-1],'params_','')
   if opts.comparison:
      index_name = str.replace(index_name,'.py', '_'+opts.comparison+'.html')
   # Add the season
   index_name = str.replace(index_name,'.py','.html')
   index_name = str.replace(index_name,'.html', '_'+season+'.html')


# -- Add the user to the html file name
# -----------------------------------------------------------------------------------
user_login = ( str.split(getcwd(),'/')[4] if getuser()=='fabric' else getuser() )
#index_name = user_login+'_'+index_name
index_name = 'atlas_'+index_name


# -> Clean the cache if specified by the user
# -----------------------------------------------------------------------------------
if clean_cache=='True':
   craz()

# -> Specific Ciclad (fabric): set the url of the web server and the paths where the
# -> images are stored
# -----------------------------------------------------------------------------------




if onCiclad:
   # Create a directory: /prodigfs/ipslfs/dods/user/CESMEP/comparison
   # The atlas will be available in a self-consistent directory, containing the html and the figures.
   # This way it is possible to clean the cache without removing the figures.
   # It is also possible to copy the directory somewhere else (makes it transportable)
   # subdir = '/prodigfs/ipslfs/dods/user/CESMEP/comparison'
   from climaf import cachedir
   component = str.replace( str.replace( str.replace(index_name,'.html',''), 'atlas_', ''), '_'+opts.comparison, '' )
   subdir = '/prodigfs/ipslfs/dods/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component
   #subdir = '/prodigfs/ipslfs/dods/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+str.replace(index_name,'.html','')
   if not os.path.isdir(subdir):
      os.makedirs(subdir)
   else:
      os.system('rm -f '+subdir+'/*')
   alt_dir_name = "/thredds/fileServer/IPSLFS"+str.split(subdir,'dods')[1]
   root_url = "https://vesg.ipsl.upmc.fr"
   #alt_dir_name = "/thredds/fileServer/IPSLFS"+str.split(cachedir,'dods')[1]

# -> Specif TGCC: Creation du repertoire de l'atlas, ou nettoyage de celui-ci si il existe deja
# -----------------------------------------------------------------------------------
if atTGCC:
   component_season = str.replace( str.replace( str.replace(index_name,'.html',''), 'atlas_', ''), '_'+opts.comparison, '' )
   CWD = os.getcwd()
   if '/dsm/' in CWD: wspace='dsm'
   if '/gencmip6/' in CWD: wspace='gencmip6'
   scratch_alt_dir_name = '/ccc/scratch/cont003/'+wspace+'/'+user_login+'/C-ESM-EP/out/'+opts.comparison+'_'+user_login+'/'+component_season+'/'
   work_alt_dir_name = scratch_alt_dir_name.replace('scratch', 'work')
   root_url = str.split(os.getcwd(),'C-ESM-EP')[0] + 'C-ESM-EP/'
   #work_alt_dir_name = root_url + 'out/'+opts.comparison+'_'+user_login+'/'+component_season+'/'
   #alt_dir_name = work_alt_dir_name #.replace('work', 'scratch')
   #alt_dir_name = work_alt_dir_name.replace('work', 'scratch')
   alt_dir_name = scratch_alt_dir_name
   if not os.path.isdir(scratch_alt_dir_name):
      os.makedirs(scratch_alt_dir_name)
   else:
      os.system('rm -f '+scratch_alt_dir_name+'/*')

# -> Specif TGCC: Copy the empty.png image in the cache
# -----------------------------------------------------------------------------------
if atTGCC:
   if not os.path.isdir(cachedir):
      os.makedirs(cachedir)
   if not os.path.isfile(cachedir+'/Empty.png'):
      cmd = 'cp '+cpath[0]+'/plot/Empty.png '+cachedir
      print cmd
      os.system(cmd)


# -> Differentiate between Ciclad and TGCC -> the first one allows working
# -> directly on the dods server ; the second one needs to go through a dods_cp 
# -> That's why we set a 'dirname' on TGCC (copied with dods_cp afterwards)
# -> and an 'altdir' on Ciclad
# -----------------------------------------------------------------------------------
if atTGCC:   alternative_dir = {'dirname': scratch_alt_dir_name}
if onCiclad: alternative_dir = {'dirname' : subdir}



# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug',
# -- intermediate -> 'warning')
# -----------------------------------------------------------------------------------
clog(verbose)



# -- Control the 'force' option (by default set to None)
# -----------------------------------------------------------------------------------
for model in models:
    if 'force' not in model:
        model.update({'force': None})


# -- Print the models
# -----------------------------------------------------------------------------------
print '==> ----------------------------------- #'
print '==> Working on models:'
print '==> ----------------------------------- #'
print '  '
for model in models:
    for key in model:
        print '  '+key+' = ',model[key]
    print '  --'
    print '  --'



# -----------------------------------------------------------------------------------
# --   End PART 1 
# -- 
# -----------------------------------------------------------------------------------






# -----------------------------------------------------------------------------------
# --   PART 2: Build the html
# --              - the header
# --              - and the sections of diagnostics:
# --                 * Atlas Explorer
# --                 * Atmosphere
# --                 * Blue Ocean - physics
# --                 * White Ocean - Sea Ice 
# --                 * Green Ocean - Biogeochemistry
# --                 * Land Surfaces
# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)



# ----------------------------------------------
# --                                             \
# --  PMP - Metrics Garden                        \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------



# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
do_PMP_MG=False
if do_PMP_MG:
    print '---------------------------------'
    print '-- Processing PMP_MG           --'
    print '-- do_PMP_MG = True            --'
    print '-- PMP_MG_variables         =  --'
    #print '-> ',PMP_MG_variables
    #print '--                             --'
    #Wmodels = period_for_diag_manager(models, diag='PMP_MG')
    #
    #index += section_2D_maps(Wmodels, reference, proj, season, atlas_explorer_variables,
    #                         'Atlas Explorer', domain=domain, custom_plot_params=custom_plot_params,
    #                         add_product_in_title=add_product_in_title, safe_mode=safe_mode,
    #                         add_line_of_climato_plots=add_line_of_climato_plots,
    #                                     alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)




# ----------------------------------------------
# --                                             \
# --  Atlas Explorer                              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------



# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
if do_atlas_explorer:
    print '---------------------------------'
    print '-- Processing Atlas Explorer   --'
    print '-- do_atlas_explorer = True    --'
    print '-- atlas_explorer_variables =  --'
    print '-> ',atlas_explorer_variables
    print '--                             --'
    Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
    index += section_2D_maps(Wmodels, reference, proj, season, atlas_explorer_variables,
                             'Atlas Explorer', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)
    if atlas_explorer_climato_variables:
       index += section_climato_2D_maps(Wmodels, reference, proj, season, atlas_explorer_climato_variables,
                             'Atlas Explorer Climatologies', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)






# ----------------------------------------------
# --                                             \
# --  Atmosphere                                  \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------

# ---------------------------------------------------------------------------------------- #
# -- Plotting the Atmosphere maps                                                       -- #
if do_atmos_maps:
    print '--------------------------------------'
    print '-- Processing Atmospheric variables --'
    print '-- do_atmos_maps = True             --'
    print '-- atmos_variables =                --'
    print '-> ',atmos_variables
    print '--                                  --'
    print '-- thumbnail_size = ',thumbnail_size
    Wmodels = period_for_diag_manager(models, diag='atm_2D_maps')
    for model in Wmodels:
        if model['project'] in ['CMIP5']: model.update(dict(table='Amon'))
    index += section_2D_maps(Wmodels, reference, proj, season, atmos_variables,
                             'Atmosphere', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
			     alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)







# ----------------------------------------------
# --                                             \
# --  Blue Ocean                                  \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# Useful observations for the NEMO atlas
if reference=='default':
   # (1) Annual Cycles (12 years, 2D fields)
   levitus_ac=dict(project="ref_climatos",product='NODC-Levitus')
   woa13_ac=dict(project="ref_climatos",product='WOA13-v2')
   rapid_ac=dict(project="ref_climatos",variable='moc', product='RAPID')
   # (2) Time Series (N months, 2D fields)
   hadisst_ts=dict(project="ref_ts",product='HadISST', period='1870-2010')#,period=opts.period)
   aviso_ts=dict(project="ref_ts",product='AVISO-L4', period='1993-2010')#,period=opts.period)
   oras4_ts=dict(project="ref_ts",product='ORAS4', period='1958-2014')#,period=opts.period)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Ocean 2D maps                                                         -- #
if do_ocean_2D_maps:
    print '----------------------------------'
    print '-- Processing Oceanic variables --'
    print '-- do_ocean_2D_maps = True      --'
    print '-- ocean_variables =            --'
    print '-> ',ocean_2D_variables
    print '--                              --'
    Wmodels = period_for_diag_manager(models, diag='ocean_2D_maps')
    for model in Wmodels:
        if model['project'] in ['CMIP5']: model.update(dict(table='Omon'))
    index += section_2D_maps(Wmodels, reference, proj, season, ocean_2D_variables, 
                             'Ocean 2D maps', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
      	                     alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)




# ---------------------------------------------------------------------------------------- #
# -- MLD maps: global, polar stereographic and North Atlantic                           -- #
# -- Winter and annual max                                                              -- #
if do_MLD_maps:
    # -- Open the section and an html table
    index += section("Mixed Layer Depth", level=4)
    #
    # -- MLD
    variable = 'mlotst'
    #
    # -- Check which reference will be used:
    #       -> 'default' = the observations that we get from variable2reference()
    #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
    if reference=='default':
       ref = variable2reference(variable, my_obs=custom_obs_dict)
    else:
       ref = reference
    #
    # -- MLD Diags -> Season and proj
    if not MLD_diags: MLD_diags=[('ANM','GLOB'),('JFM','GLOB'),('JAS','GLOB'),('JFM','NH40'),('Annual Max','NH40'),('JAS','SH30'),('Annual Max','SH30')]
    #
    # -- Loop on the MLD diags
    for MLD_diag in MLD_diags:
        season = MLD_diag[0]
        proj = MLD_diag[1]
        #
        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = (thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size)
        #
        # -- Open the html line with the title
        index += open_table()
        line_title = season+' '+proj+' climato '+varlongname(variable)+' ('+variable+')'
        index+=open_line(line_title) + close_line()+ close_table()
        #
	    # -- Open the html line for the plots
        index += open_table() + open_line('')
        #
        # --> Plot the climatology vs the reference
        # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
        # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
        wref = ref.copy()
        if 'frequency_for_annual_cycle' in wref: wref.update( dict(frequency = wref['frequency_for_annual_cycle']) )
        ref_MLD_climato   = plot_climato(variable, wref, season, proj, custom_plot_params=custom_plot_params,
                                         safe_mode=safe_mode, regrid_option='remapdis')
        #
        # -- Add the climatology to the line
        index += cell("", ref_MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #
        # -- Loop on the models (add the results to the html line)
        Wmodels = period_for_diag_manager(models, diag='MLD_maps')
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            MLD_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
            index += cell("",MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
	## -- Open the table and line for the plots
        #index += open_line('')
	##
        ## -- Add a blank space (no bias map below the climatology map that is right above)
        #index += cell("", blank_cell, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        ##
        ## -- Loop on the models (add the results to the html line)
        #Wmodels = period_for_diag_manager(models, diag='MLD_maps')
        #for model in Wmodels:
        #    #
        #    # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
        #    # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
        #    wmodel = model.copy()
        #    if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
        #    #
        #    # -- Plot the bias
        #    MLD_bias = plot_diff(variable, wmodel, ref, season, proj, custom_plot_params=custom_plot_params,
        #                         safe_mode=safe_mode, regrid_option='remapdis')
        #    index += cell("", MLD_bias, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #    #
        ## -- Close the line
        #close_line()
        #
        # -- Close the table
        index += close_table()



# ---------------------------------------------------------------------------------------- #
# -- Wind stress curl maps: global, Pacific and North Atlantic                          -- #
# -- Winter and annual max                                                              -- #
if do_curl_maps:
    # -- Open the section and an html table
    #cscript('ccdfcurl',
    #        'ln -s ${mesh_hgr} mesh_hgr.nc ; /opt/cdfTools-3.0/cdfcurl -u ${in_1} tauuo -v ${in_2} tauvo -l 1 -surf -o ${out} ; '+
    #        'ncatted -O -a coordinates,socurl,o,c,"nav_lon nav_lat time" ${out}', _var='socurl')
    index += section("Wind stress Curl", level=4)
    #
    # -- Zonal and meridional components of the wind stress
    tauu_variable = 'tauuo'
    tauv_variable = 'tauvo'
    curl_variable = 'socurl'
    #
    # -- Wind stress curl Diags -> Season and proj
    if not curl_diags:
       curl_diags= [ dict(name='Global, annual mean', season='ANM',proj='GLOB', thumbNsize='400*300'),
                  dict(name='NH, annual mean', season='ANM',proj='NH40', thumbNsize='400*400'),
                  dict(name='North Atlantic, annual mean', season='ANM', domain=dict(lonmin=-80,lonmax=0,latmin=30,latmax=90), thumbNsize='400*300'),
                  dict(name='Tropical Atlantic, annual mean', season='ANM', domain=dict(lonmin=-90,lonmax=0,latmin=-10,latmax=45), thumbNsize='400*300'),
                  dict(name='North Pacific, annual mean', season='ANM', domain=dict(lonmin=120,lonmax=240,latmin=30,latmax=75), thumbNsize='500*250'),
                  dict(name='North Atlantic, JFM', season='JFM', domain=dict(lonmin=-80,lonmax=0,latmin=30,latmax=90), thumbNsize='400*300'),
                 ]
    domains = dict( ATL=dict(lonmin=-80,lonmax=0,latmin=20,latmax=90),
                    PAC=dict(lonmin=-80,lonmax=0,latmin=20,latmax=90),
                  )
    #
    # -- Loop on the wind stress curl diags
    for curl_diag in curl_diags:
        season = curl_diag['season']
        proj = 'GLOB'
        if 'proj' in curl_diag:
           proj = curl_diag['proj']
        domain = {}
        if 'domain' in curl_diag:
           domain = curl_diag['domain']
        #
        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = curl_diag['thumbNsize']
        #
        # -- Open the html line with the title
        index += open_table()
        line_title = 'Wind stress Curl climato '+curl_diag['name']
        index+=start_line(line_title)
        #
        # -- Loop on the models (add the results to the html line)
        Wmodels = period_for_diag_manager(models, diag='2D_maps')
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            #
            # -- Compute the curl with tauu and tauv
            #if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            curl_climato = plot_curl(tauu_variable, tauv_variable, curl_variable, wmodel, season, proj, domain=domain, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis')
            index += cell("",curl_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()







# ---------------------------------------------------------------------------------------- #
# -- Plotting the time series of spatial indexes                                        -- #
if do_ATLAS_TIMESERIES_SPATIAL_INDEXES:

    index+=section("Time-serie of Spatial Indexes",level=4)
    #
    # Loop on variables,one per line
    for variable in ts_variables:
        # -- Loop on the regions
        for region in ts_basins:
            # -- Open the line with the title
	        #index+=open_table()
            #index+=open_line(title_region(region)+' '+varlongname(variable)+' ('+variable+')') + close_line()+ close_table()
	        # -- Open the line for the plots
	        #index += open_table() + open_line('')
            index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+')')
	        #
            # -- Loop on the models
            Wmodels = period_for_diag_manager(models, diag='ocean_basin_timeseries')
            for model in Wmodels:
                if variable=="tos" and region=="GLO":
                   print("=> comparison with HadISST")
                   basin_index=index_timeserie(model, variable, region=region, obs=hadisst_ts, prang=None, safe_mode=safe_mode)
                if variable=="zos" and region=="GLO":
                   print("=> comparisin with AVISO-L4")
                   basin_index=index_timeserie(model, variable, region=region, obs=aviso_ts, prang=None, safe_mode=safe_mode)
                else:
                    basin_index=index_timeserie(model, variable, region=region, obs=None, prang=None, safe_mode=safe_mode)
                index+=cell("", basin_index, thumbnail=thumbsize_TS, hover=hover, **alternative_dir)
            index += close_line() + close_table()



# ---------------------------------------------------------------------------------------- #
# -- Plotting the MOC Diagnostics                                                       -- #
if do_ATLAS_MOC_DIAGS:

    index+=section("MOC Diagnoses",level=4)
    #
    # List of regions (i.e. basins)
    for region in MOC_basins:
        #
	    # -- Loop on models
        # --> Vertical levels
        index+=start_line(title_region(region)+" MOC (Depth)")
	    #index+=open_table() + open_line(title_region(region)+" MOC (Depth)") + close_line()+ close_table()
	    # -- Open the line for the plots
	    #index += open_table() + open_line('')
        #
        Wmodels = period_for_diag_manager(models, diag='MOC_slice')
        #
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='lin')
            index+=cell("", basin_moc_slice, thumbnail=thumbsize_MOC_slice, hover=hover, **alternative_dir)
        index += close_line() + close_table()
        # -- Model levels
        index+=start_line(title_region(region)+" MOC (model levels)")
        #index+=open_table() + open_line(title_region(region)+" MOC (model levels)") + close_line()+ close_table()
	    # -- Open the line for the plots
	    #index += open_table() + open_line('')
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='index')
            index+=cell("", basin_moc_slice, thumbnail=thumbsize_MOC_slice, hover=hover, **alternative_dir)
        index += close_line() + close_table()
    #
    # -- MOC Profile at 26N vs Rapid
    #index+=open_table()
    ## -- Title of the line
    #index+=open_table() + open_line("MOC Profile at 26N vs RAPID") + close_line()+ close_table()
    ## -- Loop on models
    #index += open_table() + open_line('')
    #Wmodels = period_for_diag_manager(models, diag='MOC_profile')
    #for model in Wmodels:
    #    moc_profile_26N_vs_rapid = moc_profile_vs_obs(model, obs=rapid_ac, region='ATL', latitude=26.5,
    # 	                                              y=y, safe_mode=safe_mode)
    #    index+=cell("", moc_profile_26N_vs_rapid, thumbnail=thumbsize_MAXMOC_profile, hover=hover, **alternative_dir)
    #index += close_line() + close_table()
    ## -- Close the section
    #
    if do_TS_MOC:
       # List of latitudes
       if not llats: llats=[26.5,40.,-30.]
       for latitude in llats:
           # -- Line title
           index+=start_line("maxMoc at latitude "+str(latitude))
       	   #index+=open_table() + open_line("maxMoc at latitude "+str(latitude)) + close_line()+ close_table()
    	   # -- Loop on models
           Wmodels = period_for_diag_manager(models, diag='MOC_timeseries')
    	   for model in Wmodels:
               wmodel = model.copy()
               if 'frequency' in wmodel:
                  if wmodel['frequency'] in ['seasonal','annual_cycle']:
                     wmodel.update(dict(frequency = 'monthly', period = model['clim_period']))
               maxmoc_tserie = maxmoc_time_serie(wmodel, region='ATL', latitude=latitude, safe_mode=safe_mode)
               index+=cell("", maxmoc_tserie, thumbnail=thumbsize_MOC_TS, hover=hover, **alternative_dir)
           index+=close_line()+close_table()



# ---------------------------------------------------------------------------------------- #
# -- Plotting the Vertical Profiles of T and S                                          -- #
if do_ATLAS_VERTICAL_PROFILES:

    index+=section("Vertical Profiles",level=4)
    # Loop on variables, one per line
    Wmodels = period_for_diag_manager(models, diag='ocean_vertical_profiles')
    for variable  in VertProf_variables:
        for obs in VertProf_obs:
            for region in VertProf_basins:
	            # -- Line title
                index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
	            #index+=open_table()+open_line(title_region(region)+' '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))+close_line()+close_table()
		        #index+=open_table()+open_line('')
                for model in Wmodels:
                    if region=="GLO":
                       basin_profile = vertical_profile(model, variable, obs=obs, region=region,
                                                        box=None, safe_mode=safe_mode)
                    else:
                       #mpm_to_improve: pour l'instant, pas de comparaison aux obs dans les sous-basins
                       basin_profile = vertical_profile(model, variable, obs=None, region=region,
                                                        box=None, safe_mode=safe_mode)
                    index+=cell("", basin_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
                index+=close_line()+close_table()
	    # -- Line title
        #index+=open_table()+open_line('Gibraltar '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))+close_line()+close_table()
        index+=start_line('Gibraltar '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
        for model in Wmodels:
            gibr_profile = vertical_profile(model, variable, obs=obs, region='GLO',
                                            box=boxes.get("gibraltar"), safe_mode=safe_mode)
            index+=cell("", gibr_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
        index+=close_line()+close_table()


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Zonal Mean Slices                                                     -- #
if do_ATLAS_ZONALMEAN_SLICES:

    #crm(pattern='mask')
    index+=section("Zonal Means Sections per ocean basin --> Model regridded on reference (before computing the zonal mean)",level=4)
    # Loop over variables
    Wmodels = period_for_diag_manager(models, diag='ocean_zonalmean_sections')
    for variable in zonmean_slices_variables:
        # Loop over seasons
        for season in zonmean_slices_seas:
            index+=open_table()+open_line(variable+"-"+season)+close_line()+close_table()
            for basin in zonmean_slices_basins:
                ## -- Model Grid
                index+=start_line(title_region(basin)+' '+varlongname(variable)+' ('+variable+')')
                ref = variable2reference(variable, my_obs=custom_obs_dict)
                basin_zonmean_modelgrid = zonal_mean_slice2(ref, variable, basin=basin, season=season,
                                                ref=None, safe_mode=safe_mode, y=y, add_product_in_title=None,
                                                custom_plot_params=custom_plot_params, method='regrid_model_on_ref')
                index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
                for model in Wmodels:
                    basin_zonmean_modelgrid = zonal_mean_slice2(model, variable, basin=basin, season=season,
                                                ref=variable2reference(variable, my_obs=custom_obs_dict), safe_mode=safe_mode, y=y, add_product_in_title=None,
                                                custom_plot_params=custom_plot_params, method='regrid_model_on_ref')
                    index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
                index+=close_line()+close_table()

    index+=section("Zonal Means Sections with CDFtools per basin",level=4)
    # Loop over variables
    #Wmodels = period_for_diag_manager(models, diag='ocean_zonalmean_sections')
    #for variable in zonmean_slices_variables:
    #    # Loop over seasons
    #    for season in zonmean_slices_seas:
    #        #index+=open_table()+open_line(variable+"-"+season)+close_line()+close_table()
    #        for region in zonmean_slices_basins:
    #            ## -- Model Grid
    #            #index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+') Model Grid')
    #            #ref = variable2reference(variable, my_obs=custom_obs_dict)
    #            #basin_zonmean_modelgrid = zonal_mean_slice2(ref, variable, basin=basin, season=season,
    #            #                                ref=None, safe_mode=safe_mode, y=y, add_product_in_title=None,
    #            #                                custom_plot_params=custom_plot_params, method='regrid_ref_on_model')
    #            #index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
    #            #for model in Wmodels:
    #            #    basin_zonmean_modelgrid = zonal_mean_slice2(model, variable, basin=basin, season=season,
    #            #                                ref=variable2reference(variable, my_obs=custom_obs_dict), safe_mode=safe_mode, y=y, add_product_in_title=None,
    #            #                                custom_plot_params=custom_plot_params, method='regrid_ref_on_model')
    #            #    index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
    #		#index+=close_line()+close_table()




# ---------------------------------------------------------------------------------------- #
# -- Plotting the Drift Profiles (Hovmoller)                                            -- #
if do_ATLAS_DRIFT_PROFILES:

    index+=section("Drift Profiles (Hovmoller)",level=4)
    # Loop over variables
    Wmodels = period_for_diag_manager(models, diag='ocean_drift_profiles')
    for variable in drift_profiles_variables:
        for region in drift_profiles_basins:
            #index+=open_table()+open_line('Drift vs T0: '+title_region(region)+' '+varlongname(variable)+' ('+variable+')')+close_line()+close_table()
	        #index+=open_table()+open_line()
            index+=start_line('Drift vs T0: '+title_region(region)+' '+varlongname(variable)+' ('+variable+')')
            for model in Wmodels:
                basin_drift = hovmoller_drift_profile(model, variable, region=region, y=y, safe_mode=safe_mode)
                index+=cell("", basin_drift, thumbnail=thumbsize_TS, hover=hover, **alternative_dir)
            index+=close_line()+close_table()










# ----------------------------------------------
# --                                             \
# --  White Ocean                                 \
# --  Sea Ice                                     /
# --                                             /
# --                                            /
# ---------------------------------------------




# ---------------------------------------------------------------------------------------- #
# -- Plotting the Sea Ice volume annual cycle of both hemispheres                       -- #
if do_seaice_annual_cycle:
   print '--------------------------------------------------'
   print '-- Computing Sea Ice Volume of both hemispheres --'
   print '-- do_seaice_annual_cycle = True                --'
   print '--------------------------------------------------'
   # -- Open the section and an html table
   index += section("Sea Ice volume - annual cycle", level=4)
   index += open_table()
   #
   Wmodels = period_for_diag_manager(models, diag='sea_ice_volume_annual_cycle')
   # -- Do the plots and the availability check
   print '---'
   print '---'
   print '--- safe_mode = ',safe_mode
   print '---'
   print '---'
   siv_NH = plot_SIV(Wmodels, 'NH', safe_mode=safe_mode)
   siv_SH = plot_SIV(Wmodels, 'SH', safe_mode=safe_mode)
   #
   # -- Gather the figures in an html line
   index+=open_line('Sea Ice Volume (km3))')+\
                     cell("", siv_NH, thumbnail=thumbnail_size, hover=hover, **alternative_dir)+\
                     cell("", siv_SH, thumbnail=thumbnail_size, hover=hover, **alternative_dir)
   close_line()
   #
   # -- Close this table
   index += close_table()



# ---------------------------------------------------------------------------------------- #
# -- Sea Ice polar stereographic maps (sic and sit)                                     -- #
if do_seaice_maps:
    print '----------------------------------------------'
    print '-- Sea Ice Concentration and Thickness Maps --'
    print '-- do_seaice_maps = True                    --'
    print '----------------------------------------------'
    # -- Open the section and an html table    
    index += section("Sea Ice Concentration and Thickness (NH and SH)", level=4)
    #
    # -- Sea Ice Diags -> Season and Pole
    if not sea_ice_diags: sea_ice_diags=[('March','NH'),('September','NH'),('March','SH'),('September','SH')]
    #
    # -- Loop on the sea ice diags: region and season
    for sea_ice_diag in sea_ice_diags:
        season = sea_ice_diag[0]
        proj = sea_ice_diag[1]
	    #
        # -- Sea Ice Concentration ---------------------------------------------------
        variable='sic'
        # -- Check which reference will be used:
        #       -> 'default' = the observations that we get from variable2reference()
        #       -> or a dictionary pointing to a CliMAF dataset (without the variable)
        if reference=='default':
           ref = variable2reference(variable, my_obs=custom_obs_dict)
        else:
           ref = reference
        #
        # -> Sea Ice climatos
	    # -- Line Title
        line_title = proj+' '+season+' climatos '+varlongname(variable)+' ('+variable+')'
    	# -- Open the line for the plots
        index+= start_line(line_title)
        #
        # -- Loop on the models (in order to add the results to the html line)
        Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Do the plot
            SI_climato = plot_sic_climato_with_ref(variable, wmodel, ref, season, proj,
                                                   custom_plot_params=custom_plot_params, safe_mode=safe_mode)
            # -- And add to the html line
            index += cell("", SI_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()
        #
        ## --> Sea Ice Concentration bias
	## -- Open the line for the plots
        #index += open_line('') #+ cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        ##
        ## -- Loop on the models (in order to add the results to the html line)
        #for model in Wmodels:
        #    # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
        #    # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
        #    wmodel = model.copy()
        #    if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
        #    #
        #    # -- Do the plot
        #    SI_bias = plot_diff(variable, wmodel, ref, season, proj, custom_plot_params=custom_plot_params,
        #                        safe_mode=safe_mode)
        #    #
        #    # -- And add to the html line
        #    index += cell("", SI_bias, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        #    #
        #index+=close_line()+close_table()
        #
        # --> Sea Ice thickness climato ----------------------------------------------
        variable='sit'
        # -- Title of the line
        line_title = proj+' '+season+' climato '+varlongname(variable)+' ('+variable+')'
	    # -- Open the line for the plots
        index+=start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index=index+cell("", SIT_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()+close_table()

        # --> Sea Ice thickness climato ----------------------------------------------
        variable='sivolu'
        # -- Title of the line
        line_title = proj+' '+season+' climato '+varlongname(variable)+' ('+variable+')'
            # -- Open the line for the plots
        index+=start_line(line_title)
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            #
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            #
            # -- Do the plot
            SIT_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode)
            #
            # -- And add to the html line
            index=index+cell("", SIT_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()+close_table()





# ----------------------------------------------
# --                                             \
# --  ENSO - CLIVAR                               \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------

# ---------------------------------------------------------------------------------------- #
# -- ENSO - CLIVAR diagnostics                                                          -- #
if do_ENSO_CLIVAR:
    print '----------------------------------------------'
    print '-- ENSO - CLIVAR diagnostics                --'
    print '-- do_ENSO_CLIVAR = True                    --'
    print '----------------------------------------------'
    # -- Open the section ---------------------------------------------------------------
    index += section("ENSO - CLIVAR diagnostics", level=4)

    # -- Time series of SST anomalies (departures from annual cycle ---------------
    line_title = 'Time Series of Nino3 SST anomalies (departures from annual cycle)'
    index+=start_line(line_title)
    # -- Plot the reference
    ref_ENSO_tos = dict(project='ref_ts', period='1870-2010', product='HadISST')
    plot_ref_ENSO_ts_ssta =  ENSO_ts_ssta(ref_ENSO_tos)
    index+=cell("", plot_ref_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        plot_model_ENSO_ts_ssta = ENSO_ts_ssta(model)
        index+=cell("", plot_model_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Standard deviation of SST anomalies (departures from annual cycle ---------------
    # -- Upper band at the top of the section
    line_title = 'Standard Deviation of SST anomalies (deviations from annual cycle)'
    index+=start_line(line_title)
    # -- Plot the reference
    #ref_ENSO_tos = dict(project='ref_ts', period='1980-2005', product='HadISST')
    plot_ref_ENSO_std_ssta =  ENSO_std_ssta(ref_ENSO_tos)
    index+=cell("", plot_ref_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        plot_model_ENSO_std_ssta =  ENSO_std_ssta(model)
        index+=cell("", plot_model_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Precipitation climatology over 'ENSO' domain ------------------------------------
    line_title = 'Annual Mean Climatology of Precipitation'
    index+=start_line(line_title)
    # -- Plot the reference
    ref_ENSO_pr = variable2reference('pr')# ; ref_ENSO_pr.update(dict(frequency='seasonal'))
    plot_ref_ENSO_pr_clim = ENSO_pr_clim(ref_ENSO_pr, safe_mode=safe_mode)
    index+=cell("", plot_ref_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        plot_model_ENSO_pr_clim = ENSO_pr_clim(model, safe_mode=safe_mode)
        index+=cell("", plot_model_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Zonal Wind stress climatology over 'ENSO' domain -------------------------------
    line_title = 'Annual Mean Climatology of Zonal Wind Stress'
    index+=start_line(line_title)
    # -- Plot the reference
    ref_ENSO_tauu = variable2reference('tauu')# ; ref_ENSO_tauu.update(dict(frequency='seasonal'))
    plot_ref_ENSO_tauu_clim = ENSO_tauu_clim(ref_ENSO_tauu, safe_mode=safe_mode)
    index+=cell("", plot_ref_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        plot_model_ENSO_tauu_clim =  ENSO_tauu_clim(model, safe_mode=safe_mode)
        index+=cell("", plot_model_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Map of linear regression coefficients = d(Zonal Wind Stress) / d(SSTA Nino3) ----
    line_title = 'Linear Regression = d(Zonal Wind Stress) / d(SSTA Nino3)'
    index+=start_line(line_title)
    # -- Plot the reference
    ref_ENSO_tauu = dict(project='ref_ts', product='ERAInterim', period='2001-2010', variable='tauu')
    ref_ENSO_tos  = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010')
    plot_ref_ENSO_tauuA_on_SSTANino3 =  ENSO_linreg_tauuA_on_SSTANino3(ref_ENSO_tauu, ref_ENSO_tos, safe_mode=safe_mode)
    index+=cell("", plot_ref_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        tos_model = model.copy() ; tos_model.update(variable='tos')
        tauu_model = model.copy() ; tauu_model.update(variable='tauu')
        plot_model_ENSO_tauuA_on_SSTANino3 =  ENSO_linreg_tauuA_on_SSTANino3(tauu_model,tos_model, safe_mode=safe_mode)
        index+=cell("", plot_model_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Map of linear regression coefficients = d(ShortWave) / d(SSTA Nino3) ----------
    line_title = 'Linear Regression = d(ShortWave) / d(SSTA Nino3)'
    index+=start_line(line_title)
    # -- Plot the reference
    ref_ENSO_rsds = dict(project='ref_ts', product='CERES-EBAF-Ed2-7', period='2001-2010', variable='rsds')
    ref_ENSO_tos  = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010')
    plot_ref_ENSO_rsds_on_SSTANino3 =  ENSO_linreg_rsds_on_SSTANino3(ref_ENSO_rsds, ref_ENSO_tos, safe_mode=safe_mode)
    index+=cell("", plot_ref_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    # And loop over the models
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    for model in Wmodels:
        tos_model = model.copy() ; tos_model.update(variable='tos')
        rsds_model = model.copy() ; rsds_model.update(variable='rsds')
        plot_model_ENSO_rsds_on_SSTANino3 =  ENSO_linreg_rsds_on_SSTANino3(rsds_model,tos_model, safe_mode=safe_mode)
        index+=cell("", plot_model_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()
    #
    # -- Annual Cycles -----------------------------------------------------------------
    line_title = 'Annual cycles Nino3 (SST, SSTA, Std.dev)'
    index+=start_line(line_title)
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    plot_annual_cycles = plot_ENSO_annual_cycles(Wmodels, safe_mode=safe_mode)
    index+=cell("", plot_annual_cycles, thumbnail="350*200", hover=hover, **alternative_dir)
    close_line()
    index+=close_table()


    # -- Longitudinal profile of Zonal Wind Stress --------------------------------------
    line_title = 'Annual Mean Climatology of Zonal Wind Stress (-5/5N profile)'
    index+=start_line(line_title)
    Wmodels = period_for_diag_manager(models, diag='ENSO')
    plot_tauu_profile = plot_ZonalWindStress_long_profile(Wmodels, safe_mode=safe_mode)
    index+=cell("", plot_tauu_profile, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
    close_line()
    index+=close_table()





# ----------------------------------------------
# --                                             \
# --  Precipitation annual cycles                 \
# --  r.w. monsoons                               /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- Monsoons - precip annual cycles                                                    -- #

if do_Monsoons_pr_anncyc:
    print '----------------------------------------------'
    print '-- Monsoons precipitation ann. cycles       --'
    print '-- do_Monsoons_pr_anncyc = True             --'
    print '----------------------------------------------'
    # -- Open the section ---------------------------------------------------------------
    index += section("Monsoons - precipitation annual cycles diagnostics", level=4)
    
    # -- Regions
    if not monsoon_precip_regions:
       monsoon_precip_regions = [
	dict(name='All-India Rainfall (65/95E;5/30N)', domain=dict(lonmin=65,lonmax=95,latmin=5,latmax=30)),
        dict(name='West African Monsoon (-20/30E;0/20N)', domain=dict(lonmin=-20,lonmax=30,latmin=0,latmax=20)),
        ]
    
    # -- Common plot parameters for monsoons precip annual cycles
    cpp = dict(min=0,max=10, lgcols=2,
           options = 'vpXF=0|'+\
              'vpWidthF=0.33|'+\
              'vpHeightF=0.4|'+\
              'tmXBLabelFontHeightF=0.012|'+\
              'tmYLLabelFontHeightF=0.014|'+\
              'lgLabelFontHeightF=0.012|'+\
              'tmXMajorGrid=True|'+\
              'tmYMajorGrid=True|'+\
              'tmXMajorGridLineDashPattern=2|'+\
              'tmYMajorGridLineDashPattern=2|'+\
              'xyLineThicknessF=9|'+\
              'gsnYRefLineThicknessF=3|'+\
              'pmLegendHeightF=0.3|'+\
              'pmLegendSide=Bottom|'+\
              'gsnYRefLine=0.0|'+\
              'tiYAxisString=Precipitation (mm/day)|'+\
              'gsnStringFontHeightF=0.017'#+\
          )
          #    'xyMonoLineThickness=False|'+\
          #    'xyLineThicknesses=(/ 6.0, 14.0/)|'+\
          #'xyLineThicknesses=(/6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 14.0/)|'+\

    # -- Get the reference
    pr_ref = ds(**variable2reference('pr'))
    # -- The GPCP mask is obtained by remapping the land-sea mask of the 280*280 LMDz mask on GPCP (nearest neighbour)
    ref_mask = regrid( fds('/data/igcmg/database/grids/LMDZ4.0_280280_grid.nc', variable='mask', period='fx'), pr_ref, option='remapnn')

    # -- Land mask for reference
    land_ref_mask = mask(ref_mask,miss=0)
    land_pr_ref_masked = fmul(pr_ref, land_ref_mask)

    # -- Annual cycle of precipitation over land ---------------------------------------- 
    line_title = 'Annual cycle of precipitation over land'
    index+=start_line(line_title)
    #
    Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
    # -- Loop on regions
    #MP = []
    for region in monsoon_precip_regions:

        anncyc_pr_ref_masked = fmul(space_average(llbox(land_pr_ref_masked, **region['domain'])), 86400)
        
        ens_for_plot = dict(GPCP=anncyc_pr_ref_masked)
        
        # -- One plot per region
        # -> Loop on the models
        models_order = []
        for model in Wmodels:
            
            wmodel = model.copy()
            wmodel.update(dict(variable='pr'))
            frequency_manager_for_diag(wmodel, diag='SE')
            get_period_manager(wmodel)
  
            pr_sim = ds(**wmodel)

            # Method 1 = regrid the model on the obs, and use the obs mask to compute the spatial average
            land_pr_sim_masked = fmul(regrid(pr_sim,pr_ref, option='remapcon2'), land_ref_mask)

            anncyc_pr_sim_masked = fmul(space_average(llbox(land_pr_sim_masked, **region['domain'])), 86400)
            if safe_mode:
               try:
                  cfile(anncyc_pr_sim_masked)
                  if model['project']=='CMIP5':
                     monsoon_name_in_plot = model['model']
                  else:
                     monsoon_name_in_plot = (model['customname'] if 'customname' in model else model['simulation'])
                  ens_for_plot.update({monsoon_name_in_plot:anncyc_pr_sim_masked})
                  models_order.append(monsoon_name_in_plot)
               except:
                  print 'No data for Monsoon pr diagnostic for ',model

        cens_for_plot = cens(ens_for_plot, order=['GPCP'] + models_order)
    
        plot_pr_anncyc_region = safe_mode_cfile_plot( curves(cens_for_plot, title=region['name'], X_axis='aligned',  **cpp), True, safe_mode)

        index+=cell("", plot_pr_anncyc_region, thumbnail=thumbnail_monsoon_pr_anncyc_size, hover=hover, **alternative_dir)
    #
    close_line()
    index+=close_table()







# ----------------------------------------------
# --                                             \
# --  Turbulent Air-Sea Fluxes                    \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------




# ---------------------------------------------------------------------------------------- #
# -- Global plot Turbulent fluxes                                                       -- #
if do_GLB_SFlux_maps:
    # -- Open the section and an html table
    index += section("Turbulent Fluxes Annual Mean", level=4)
    #
    Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
    #
    # -- Loop on the turbulent fluxes variables
    for variable in TurbFluxes_variables:
        #
        # -- we copy the dictionary to midfy it inside the loop
        wmodel = Wmodels[0].copy()
        #
        # -- Here, we add table='Amon' for the CMIP5 outputs
        wmodel.update(dict(variable=variable,table='Amon'))
        #
        # -- Plot using plot_climato_TurbFlux_GB2015
        # --> Global Annual Mean
        # --> For the simulation
        GLB_plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params)
        # --> And for the reference
        GLB_plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params)
        #
        # -- Open the html line with the title
        line_title = 'GLOBAL Annual Mean '+varlongname(variable)+' ('+variable+')'
        index += start_line(line_title)
	#
        # -- Add the plots at the beginning line
        print 'Do climato plots for '+variable
        # --> First, the climatology of the reference
        index += cell("", GLB_plot_climato_ref_ANM, thumbnail=thumbnail_size, hover=hover, **alternative_dir)
        # --> Then, the climatology of the first model
        index += cell("", GLB_plot_climato_sim_ANM, thumbnail=thumbnail_size, hover=hover, **alternative_dir)
        #
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            wmodel = model.copy()
            wmodel.update(dict(variable=variable,table='Amon'))
            print 'Do bias plots for '+variable , model
            GLB_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, climatology='ANM', region='Global', custom_plot_params=custom_plot_params)
            index=index+cell("", GLB_bias_ANM, thumbnail=thumbnail_size, hover=hover, **alternative_dir)
            #
        # -- Close the line
        index+=close_line()+close_table()
        #




# ---------------------------------------------------------------------------------------- #
# -- Tropical (GB2015) Heat Fluxes and Wind stress
if do_Tropics_SFlux_maps:
    # -- Open the section and an html table
    index += section("Turbulent Air-Sea Fluxes Tropics = Gainusa-Bogdan et al. 2015", level=4)
    #
    Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
    #
    for variable in TurbFluxes_variables:
        # -- Second Line: Climatos seasons REF + models
        # -- Third line: bias maps
        # -- First line: Climato ANM -----------------------------------------------------
        line_title = varlongname(variable)+' ('+variable+') => Annual Mean Climatology - GB2015, Model and bias map'
        index+=start_line(line_title)
        # -- Plot the reference
        plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
        # And loop over the models
        for model in Wmodels:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable, wmodel, climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_ANM = cpage(fig_lines=[[plot_climato_sim_ANM],[plot_climato_ref_ANM],[plot_bias_ANM]], fig_trim=True, page_trim=True,
                             title=sim.model+' '+sim.simulation+' (vs GB2015)',
                             gravity='NorthWest',
                             ybox=80, pt=30,
                             x=30, y=40,
                             font='Waree-Bold'
                             )
            index+=cell("", safe_mode_cfile_plot(plot_ANM, safe_mode=safe_mode, do_cfile=True), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()
        index+=close_table()
        # 
        # -- First line: Climato ANM -----------------------------------------------------
        line_title = varlongname(variable)+' ('+variable+') => Seasonal climatologies (top line) and bias maps (bottom line)'
        index+=start_line(line_title)
        # -- Plot the reference
        plot_climato_ref_DJF = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
        plot_climato_ref_MAM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
        plot_climato_ref_JJA = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
        plot_climato_ref_SON = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
        seas_ref_clim_plot = cpage(fig_lines=[[plot_climato_ref_DJF],[plot_climato_ref_MAM],[plot_climato_ref_JJA],[plot_climato_ref_SON]],
                                   fig_trim=True,page_trim=True,
                                   title='Climatology GB2015',
                                   gravity='NorthWest',
                                   ybox=80, pt=30,
                                   x=30, y=40,
                                   font='Waree-Bold'
                                  )
        index+=cell("", safe_mode_cfile_plot(seas_ref_clim_plot, safe_mode=safe_mode, do_cfile=True), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        # And loop over the models
        for model in Wmodels:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_DJF = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_climato_sim_MAM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_climato_sim_JJA = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_climato_sim_SON = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            seas_sim_clim_plot = cpage(fig_lines=[[plot_climato_sim_DJF],[plot_climato_sim_MAM],[plot_climato_sim_JJA],[plot_climato_sim_SON]],
                                       fig_trim=True,page_trim=True,
                                       title='Climatology '+sim.model+' '+sim.simulation,
                                       gravity='NorthWest',
                                       ybox=80, pt=30,
                                       x=30, y=40,
                                       font='Waree-Bold'
                                      )
            index+=cell("", safe_mode_cfile_plot(seas_sim_clim_plot, safe_mode=safe_mode), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()

        # -- Third line: Bias maps -----------------------------------------------------
        index+=open_line('')
        # Add a blank space
        index+=cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        # And loop over the models
        for model in Wmodels:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_bias_DJF = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_bias_MAM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_bias_JJA = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            plot_bias_SON = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False)
            seas_bias_plot= cpage(fig_lines=[[plot_bias_DJF],[plot_bias_MAM],[plot_bias_JJA],[plot_bias_SON]],fig_trim=True,page_trim=True,
                                  title=sim.model+' '+sim.simulation+' (vs GB2015)',
                                  gravity='NorthWest',
                                  ybox=80, pt=30,
                                  x=30, y=40,
                                  font='Waree-Bold'
                                 )
            #if safe_mode==True:
            #   try:
            #      index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #   except:
            #      index+=cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #else:
            #   index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            index+=cell("", safe_mode_cfile(seas_bias_plot, safe_mode=safe_mode), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
        close_line()
        index+=close_table()
        #









# ----------------------------------------------
# --                                             \
# --  Green Ocean                                 \
# --  Ocean Biogeochemistry                       /
# --                                             /
# --                                            /
# ---------------------------------------------



# ---------------------------------------------------------------------------------------- #
# -- Plotting the biogeochemistry maps                                                  -- #
if do_biogeochemistry_2D_maps:
    print '---------------------------------------'
    print '-- Processing Oceanic variables      --'
    print '-- do_biogeochemistry_2D_maps = True --'
    print '-- ocebio_2D_variables =             --'
    print '-> ',ocebio_2D_variables
    print '--                              --'
    Wmodels = period_for_diag_manager(models, diag='PISCES_2D_maps')
    index += section_2D_maps(Wmodels, reference, proj, season, ocebio_2D_variables,
                             'Ocean Biogeochemistry 2D', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
   			                 alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)









# ----------------------------------------------
# --                                             \
# --  Land Surfaces                               \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------




# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Energy Budget                                                             -- #
if do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_bias=[]
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_energy_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_energy_budget_bias,
                                                         'ORCHIDEE Energy Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							 custom_plot_params=custom_plot_params, shade_missing=True, safe_mode=safe_mode,
							 alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)


if do_ORCHIDEE_Energy_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_bias=[]
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_energy_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_energy_budget_bias,
                             'ORCHIDEE Energy Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode, 
                             add_line_of_climato_plots=add_line_of_climato_plots,
	                     alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)


if do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_modelmodel=[]
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_energy_budget_modelmodel.append(tmpvar)
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_energy_budget_modelmodel,
                             'ORCHIDEE Energy Budget, difference with first simulation', domain=domain, 
                              add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                              add_line_of_climato_plots=add_line_of_climato_plots,
			      custom_plot_params=custom_plot_params, alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict)



if do_ORCHIDEE_Energy_Budget_diff_with_ref_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, refsimulation, proj, season, variables_energy_budget,
                             'ORCHIDEE Energy Budget, difference with a reference (climatological month, season)', domain=domain,
                              add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                              add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
	 		      custom_plot_params=custom_plot_params, alternative_dir=alternative_dir)



# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Water Budget                                                             -- #
if do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_water_budget =                                          --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_bias=[]
    for tmpvar in variables_water_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_water_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                                                         'ORCHIDEE Water Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							 shade_missing=True, safe_mode=safe_mode, custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict,
							 alternative_dir=alternative_dir)


if do_ORCHIDEE_Water_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climobs_bias_maps = True  --'
    print '-- variables_water_budget =                                          --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_bias=[]
    for tmpvar in variables_water_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_water_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                             'ORCHIDEE Water Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			                 alternative_dir=alternative_dir)


if do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                         --'
    print '-- do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps = True   --'
    print '-- variables_water_budget =                                           --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_modelmodel=[]
    for tmpvar in variables_water_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_water_budget_modelmodel.append(tmpvar)
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_water_budget_modelmodel,
                             'ORCHIDEE Water Budget, difference with first simulation', domain=domain,
                              add_product_in_title=add_product_in_title, custom_plot_params=custom_plot_params,
                              add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			                  shade_missing=True, safe_mode=safe_mode, alternative_dir=alternative_dir)



# ---------------------------------------------------------------------------------------- #
# -- ORCHIDEE Carbon Budget                                                             -- #
if do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_bias=[]
    for tmpvar in variables_carbon_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_carbon_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_carbon_budget_bias,
                                                         'ORCHIDEE Carbon Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							                             shade_missing=True, safe_mode=safe_mode, custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict,
							                             alternative_dir=alternative_dir)


if do_ORCHIDEE_Carbon_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_bias=[]
    for tmpvar in variables_carbon_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
           wvariables_carbon_budget_bias.append(tmpvar)
        except:
           print 'No obs for '+tmpvar
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_carbon_budget_bias,
                             'ORCHIDEE Carbon Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
                             alternative_dir=alternative_dir)



if do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_modelmodel=[]
    for tmpvar in variables_carbon_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
        try:
           cfile(ds(**variable2reference(tmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_carbon_budget_modelmodel.append(tmpvar)
    Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
    # -- Garde fou to avoid missing the first simulation
    for model in Wmodels:
        if model['project'] not in ['IGCM_OUT']:
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_carbon_budget_modelmodel,
                             'ORCHIDEE Carbon Budget, difference with first simulation', domain=domain,
                              add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                              add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			                  custom_plot_params=custom_plot_params, alternative_dir=alternative_dir)



# -----------------------------------------------------------------------------------
# --   End PART 2
# --
# -----------------------------------------------------------------------------------








# -----------------------------------------------------------------------------------
# --   PART 3: Finalize the index by replacing the paths to the cache for the paths       
# --   to the alternate directory                                                         
# -----------------------------------------------------------------------------------
# --   ONLY FOR DEVELOPERS - users shouldn't need to modify this section             
# --   Contact jerome.servonnat@lsce.ipsl.fr                                         
# -----------------------------------------------------------------------------------
# -- Here we can work either on Ciclad or at TGCC
# -- On Ciclad we feed directly the cache located on the dods server
# -- and point at this web address.
# -- At TGCC we need to:
# --   - feed the cache on $SCRATCHDIR (set in your environment) and make a hard link in
# --     a target directory (alt_dir_name, based on the current working directory and
# --     subdir)
# --   - at the end of the atlas, we copy the target directory (alt_dir_name) on the
# --     $WORKDIR (work_alt_dir_name) before copying it on the dods with dods_cp
# --   - Eventually, we dods_cp the directory work_alt_dir_name
# --     on the /ccc/work/cont003/dods/public space

# -- Adding the compareCompanion JavaScript functionality to make a selection of images
if add_compareCompanion:
   index += compareCompanion()

index += trailer()
import os 
if alt_dir_name :
    #
    if onCiclad:
       #OLD#outfile=cachedir+"/"+index_name
       #OLD#print 'outfile = ',outfile
       #OLD#with open(outfile,"w") as filout : filout.write(index)
       #OLD#print(' -- ')
       #OLD#print(' -- ')
       #OLD#print(' -- ')
       #OLD#print("index actually written as : "+outfile)
       #OLD#print("may be seen at "+root_url+outfile.replace(cachedir,alt_dir_name))
       outfile=subdir+"/"+index_name
       print 'outfile = ',outfile
       with open(outfile,"w") as filout : filout.write(index)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       print("index actually written as : "+outfile)
       print("may be seen at "+root_url+outfile.replace(subdir,alt_dir_name))
    #
    if atTGCC:
       # -- Ecriture du fichier html dans le repertoire sur scratch
       outfile=scratch_alt_dir_name+index_name
       with open(outfile,"w") as filout : filout.write(index)
       print("index actually written as : "+outfile)
       # -- Copie du repertoire de resultat du scratch vers le work (avant copie sur le dods)
       #subdir = opts.comparison+'_'+user_login+'/'+component
       #work_alt_dir_name = os.getcwd()+'/'+subdir

       if not os.path.isdir(work_alt_dir_name):
          os.makedirs(work_alt_dir_name)
       else:
          print 'rm -rf '+work_alt_dir_name+'/*'
          os.system('rm -rf '+work_alt_dir_name+'/*')
       #cmd1 = 'cp -r '+scratch_alt_dir_name+' '+work_alt_dir_name.replace('/'+subdir,'')
       cmd1 = 'cp -r '+scratch_alt_dir_name+'* '+work_alt_dir_name
       print cmd1
       os.system(cmd1)
       #
       # Rajouter thredds si sur gencmip6
       # -- dods_cp du repertoire copie sur le work
       if 'gencmip6' in getcwd():
          public_space = '/ccc/work/cont003/thredds/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login
       if 'dsm' in getcwd():
          public_space = '/ccc/work/cont003/dods/public/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login
       cmd12 = 'rm -rf '+public_space+'/'+component_season
       print cmd12
       os.system(cmd12)
       #'dods_cp root_url+C-ESM-EP/out/comparison_user/component public_space'
       cmd2 = 'dods_cp '+work_alt_dir_name+' '+public_space+'/'
       print cmd2
       os.system(cmd2)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       #print('Index available at : https://esgf.extra.cea.fr/thredds/fileServer/work/'+getuser()+'/'+subdir+'/'+index_name)
       print('Index available at : https://esgf.extra.cea.fr/thredds/fileServer/work/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component_season+'/'+index_name)
    #
else :
    with open(index_name,"w") as filout : filout.write(index)
    print("The atlas is ready as %s"%index_name)


# -----------------------------------------------------------------------------------
# --   End PART 3
# --
# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
# -- End of the atlas                                                                
# -----------------------------------------------------------------------------------

