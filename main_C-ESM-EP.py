# ----------------------------------------------------------------------------------- #
# -- Header of the atlas.py ; import the useful python modules (CliMAF, NEMO_atlas, -- #
# -- and potentially your own stuff stored in my_plot_functions.py in the current   -- #
# -- working directory.                                                             -- #
# ------------------------------------------------------------------------------------ #
from climaf.api import *
from climaf.html import * 
from climaf import cachedir
from CM_atlas import *
from climaf.site_settings import onCiclad, atTGCC, atCNRM
from getpass import getuser
from climaf import __path__ as cpath
import json
import os, copy, subprocess, shlex


# -----------------------------------------------------------------------------------
# --   PART 1: Get the instructions from:
# --              - the default values
# --              - the parameter file (priority 2)
# --              - the command line (priority 1)
# -----------------------------------------------------------------------------------


# -- Description of the atlas
# -----------------------------------------------------------------------------------
desc="\n\nCliMAF Earth System Model Evaluation Platform: comparing multiple simulations against references (https://github.com/jservonnat/C-ESM-EP/wiki)"


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
                  action="store",default=None)
parser.add_option("--datasets_setup",
                  help="Name of the file containing the list of dictionaries describing the datasets",
                  action="store",default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store",default=None)

(opts, args) = parser.parse_args()


print 'opts.comparison = ', opts.comparison

# -- Get the default parameters from default_atlas_settings.py -> Priority = default
# -----------------------------------------------------------------------------------
default_file = '/share/default/default_atlas_settings.py'
while not os.path.isfile(os.getcwd()+default_file):
    default_file = '/..'+default_file
execfile(os.getcwd()+default_file)


# -- If we specify a datasets_setup from the command line, we use 'models' from this file
# -----------------------------------------------------------------------------------
if opts.datasets_setup:
   datasets_setup_available_period_set_file = str.replace(opts.datasets_setup,'.py','_available_period_set.py')
   if os.path.isfile(datasets_setup_available_period_set_file):
      use_available_period_set = True
      execfile(datasets_setup_available_period_set_file)
      # Create Wmodels_ts and Wmodels_clim from Wmodels
      Wmodels_clim = copy.deepcopy(Wmodels)
      for item in Wmodels_clim:
          clim_period_args = copy.deepcopy(item['clim_period'])
          item.pop('clim_period')
          item.pop('ts_period')
          item.update(clim_period_args)
      # 
      Wmodels_ts = copy.deepcopy(Wmodels)
      for item in Wmodels_ts:
          ts_period_args = copy.deepcopy(item['ts_period'])
          item.pop('ts_period')
          item.pop('clim_period')
          item.update(ts_period_args)
   else:
      execfile(opts.datasets_setup)
      use_available_period_set = False


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
   index_name = str.replace(index_name,'.py','.html')


# -- Add the user to the html file name
# -----------------------------------------------------------------------------------
username=getuser()
user_login = ( str.split(getcwd(),'/')[4] if username=='fabric' else username )
index_name = 'atlas_'+index_name



# -> Clean the cache if specified by the user
# -----------------------------------------------------------------------------------
print 'clean_cache = ',clean_cache
if clean_cache=='True':
   print '!!! Full clean of the cache !!!'
   craz()
   print '!!! Cache cleaned !!!'


# -> Specific Ciclad (fabric): set the url of the web server and the paths where the
# -> images are stored
# -----------------------------------------------------------------------------------
# -- Get component name
component = str.replace( str.replace( str.replace( index_name, '_'+opts.comparison, '' ), '.html',''), 'atlas_', '')


# -- Get the site specifications:
# -----------------------------------------------------------------------------------
#  -> path_to_cesmep_output_rootdir = where (directory) we physically store the results of the C-ESM-EP (root directory of the whole atlas tree)
#  -> path_to_cesmep_output_rootdir_on_web_server = path to the results on the web server
#  -> root_url_to_cesmep_outputs = URL of the root directory of the C-ESM-EP atlas (need to add 'C-ESM-EP', comparison and component to reach the atlas)
from locations import path_to_cesmep_output_rootdir, path_to_cesmep_output_rootdir_on_web_server, root_url_to_cesmep_outputs

# -- Location of the directory where we will store the results of the atlas
atlas_dir = path_to_cesmep_output_rootdir +'/C-ESM-EP/'+ opts.comparison+'_'+username+'/'+component

# -- Url of the atlas (without the html file)
atlas_url = str.replace( atlas_dir, path_to_cesmep_output_rootdir, root_url_to_cesmep_outputs)

# -- at CNRM and TGCC we create the atlas directory if it doesn't exist, or remove the figures
if atCNRM or atTGCC:
   if not os.path.isdir(atlas_dir):
      os.makedirs(atlas_dir)
   else:
      os.system('rm -f '+atlas_dir+'/*.png')
   


# -> Specif TGCC and CNRM: Copy the empty.png image in the cache
# -----------------------------------------------------------------------------------
if atTGCC or atCNRM :
   if not os.path.isdir(cachedir):
      os.makedirs(cachedir)
   if not os.path.isfile(cachedir+'/Empty.png'):
      cmd = 'cp '+cpath+'/plot/Empty.png '+cachedir
      print cmd
      os.system(cmd)


# -- Specify the directory where we will output the atlas html file and the figures
# -----------------------------------------------------------------------------------
alternative_dir = {'dirname' : atlas_dir}


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



# -- Define the path to the main C-ESM-EP directory:
# -----------------------------------------------------------------------------------
rootmainpath = str.split(os.getcwd(),'C-ESM-EP')[0] + 'C-ESM-EP/'
if os.path.isfile(rootmainpath+'main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath
if os.path.isfile(rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/'


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
# --  Model Tuning: SST 50S/50N average           \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


           

# ---------------------------------------------------------------------------------------- #
# -- Compute the SST biases over 50S/50N for the reference models and the test datasets -- #

if do_SST_for_tuning:

      # -- Start an html section to receive the plots
      # ----------------------------------------------------------------------------------------------
      index += section('Spatial averages = metrics for tuning', level=4)
      index+=start_line('SST 50S/50N')

      if not use_available_period_set:
	 Wmodels = period_for_diag_manager(models, diag='clim')
      else:
         Wmodels = copy.deepcopy(Wmodels_clim)
      tuning_colors = colors_manager(Wmodels,cesmep_python_colors)
      print 'tuning_colors = ',tuning_colors
      for model in Wmodels:
          model.update(dict(color=tuning_colors[Wmodels.index(model)]))

      # ------------------------------------------------
      # -- Start computing the spatial averages
      # ------------------------------------------------
      if not reference_models: reference_models = []
      reference_datasets = [
         dict(project='ref_ts', product='HadISST', period='1990-2010', dataset_type='obs_reference', frequency='monthly'),
         dict(project='ref_ts', product='HadISST', period='1875-1899', dataset_type='obs_reference', frequency='monthly'),

      ]
      ref_for_rmsc = dict(project='ref_ts', product='HadISST', period='1990-2010', dataset_type='obs_reference', frequency='monthly', variable='tos')
      all_dataset_dicts= Wmodels + reference_models + reference_datasets
      #
      results = dict()
      variable='tos'
      #outjson = main_cesmep_path+'/'+opts.comparison+'/TuningMetrics/'+variable+'_'+opts.comparison+'_metrics_over_regions_for_tuning.json'
      
      for dataset_dict in all_dataset_dicts:
          #
          # -- We already applied time manager, no need to re-do it (loosing time searching for the available periods)
          wdataset_dict = dataset_dict.copy()
          wdataset_dict.update(dict(variable='tos'))
          #
          # -- Use the project specs:
          if wdataset_dict['project'] in tos_project_specs:
             wdataset_dict.update(tos_project_specs[wdataset_dict['project']])
          #
          #
          if not use_available_period_set:
             frequency_manager_for_diag(wdataset_dict, diag='clim')
             get_period_manager(wdataset_dict)
          
          # -- Build customname and update dictionnary => we need customname anyway, for references too
          if 'customname' in wdataset_dict:
              customname = wdataset_dict['customname']
          else:
              customname = str.replace(build_plot_title(wdataset_dict, None),' ','_')
              wperiod = ''
              if 'clim_period' in wdataset_dict: wperiod=wdataset_dict['clim_period']
              if 'period' in wdataset_dict:
                  if wdataset_dict['period'] not in 'fx': wperiod=wdataset_dict['period']
              if wperiod not in customname: customname = customname+'_'+wperiod
          customname = str.replace(customname,' ','_')
          wdataset_dict.update(dict(customname = customname))
          #
          # -- We tag the datasets to identify if they are: test_dataset, reference_dataset or obs_reference
          # -- This information is used by the plotting R script.
          if dataset_dict in Wmodels:
             wdataset_dict.update(dict(dataset_type='test_dataset'))
          if dataset_dict in reference_models:
             wdataset_dict.update(dict(dataset_type='reference_dataset'))
          dataset_name = customname
          results[dataset_name] = dict(results=dict(), dataset_dict=wdataset_dict)
          #
          # -- Loop on the regions; build the results dictionary and save it in the json file variable_comparison_spatial_averages_over_regions.json
          regions_for_spatial_averages = [ dict(region_name='50S_50N', domain=[-50,50,0,360]) ]
          season='ANM'
          for region in regions_for_spatial_averages:
              dat = llbox(regridn(clim_average(ds(**wdataset_dict), season), cdogrid='r360x180', option='remapdis'),
                          lonmin=region['domain'][2], lonmax=region['domain'][3],
                          latmin=region['domain'][0], latmax=region['domain'][1])
              if safe_mode:
                 try:
                    rawvalue = cMA(space_average(dat))[0][0][0]
                 except:
                    rawvalue = 'NA'
                    print '!! => Computing rawvalue failed for ',wdataset_dict
                    print '--> Return NA'
              else:
                 rawvalue = cMA(space_average(dat))[0][0][0]
              #
              if 'product' in wdataset_dict:
                 if wdataset_dict['product']=='WOA13-v2': rawvalue = rawvalue[0]
              # -- Add offset to convert in Celsius
              #print 'wdataset_dict in tuning_metrics : ',wdataset_dict
              #print 'rawvalue = ',rawvalue
              rawvalue = rawvalue - 273.15
              # -- Compute bias
              results[dataset_name]['results'].update( {region['region_name']: {'rawvalue': str(rawvalue)} } )
              #
              # -- Compute the centered RMSE rmsc
              if wdataset_dict['dataset_type']!='obs_reference':
                 scyc_dat = llbox(regridn(annual_cycle(ds(**wdataset_dict)), cdogrid='r360x180', option='remapdis'),
                                  lonmin=region['domain'][2], lonmax=region['domain'][3],
                                  latmin=region['domain'][0], latmax=region['domain'][1])
                 anom_dat = fsub(scyc_dat, str(cMA(space_average(dat))[0][0][0]) )

                 scyc_ref = llbox(regridn(annual_cycle(ds(**ref_for_rmsc)), cdogrid='r360x180', option='remapdis'),
                                  lonmin=region['domain'][2], lonmax=region['domain'][3],
                                  latmin=region['domain'][0], latmax=region['domain'][1])
                 anom_ref = fsub(scyc_ref, str(cscalar(time_average(space_average(scyc_ref)))) )
                 if safe_mode:
                    try:
                       rmsc = cMA( ccdo( time_average(space_average( ccdo( minus(anom_dat, anom_ref), operator='sqr' ) )), operator='sqrt') )[0][0][0]
                       rms = cMA( ccdo( time_average(space_average( ccdo( minus(scyc_dat, scyc_ref), operator='sqr' ) )), operator='sqrt') )[0][0][0]
                    except:
                       print '!! => Computing RMSC and RMS failed for ',wdataset_dict
                       print '--> Return NA'
                       rmsc = 'NA'
                       rms = 'NA'
                 else:
                    rmsc = cMA( ccdo( time_average(space_average( ccdo( minus(anom_dat, anom_ref), operator='sqr' ) )), operator='sqrt') )[0][0][0]
                    rms = cMA( ccdo( time_average(space_average( ccdo( minus(scyc_dat, scyc_ref), operator='sqr' ) )), operator='sqrt') )[0][0][0]
                 #
                 results[dataset_name]['results'][region['region_name']].update( dict(rmsc = str(rmsc), rms=str(rms) ))
      outjson = main_cesmep_path+'/'+opts.comparison+'/TuningMetrics/'+variable+'_'+opts.comparison+'_metrics_over_regions_for_tuning.json'
      with open(outjson, 'w') as outfile:
           json.dump(results, outfile, sort_keys = True, indent = 4)
      #
      # -- Eventually, do the plots
      for region in regions_for_spatial_averages:
          # -- plot the raw values
          figname = atlas_dir+ '/'+ opts.comparison+'_'+variable+'_'+region['region_name']+'_rawvalues_over_regions_for_tuning.png'
          cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/TuningMetrics/plot_rawvalue.R --metrics_json_file '+outjson+' --region '+region['region_name']+' --figname '+figname
          print(cmd)
          os.system(cmd)
          index+=cell("", os.path.basename(figname), thumbnail="700*600", hover=False)
          #
          # -- plot the rmsc
          figname = atlas_dir+ '/'+ opts.comparison+'_'+variable+'_'+region['region_name']+'_rmsc_over_regions_for_tuning.png'
          cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/TuningMetrics/plot_rmsc.R --metrics_json_file '+outjson+' --region '+region['region_name']+' --figname '+figname
          print(cmd)
          os.system(cmd)
          index+=cell("", os.path.basename(figname), thumbnail="700*600", hover=False)
          #
          # -- plot the rms
          figname = atlas_dir+ '/'+ opts.comparison+'_'+variable+'_'+region['region_name']+'_rms_over_regions_for_tuning.png'
          cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/TuningMetrics/plot_rmsc.R --metrics_json_file '+outjson+' --region '+region['region_name']+' --figname '+figname+' --statistic rms'
          print(cmd)
          os.system(cmd)
          index+=cell("", os.path.basename(figname), thumbnail="700*600", hover=False)

      # -- Close the line and the section
      index += close_line() + close_table()





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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = None

    # -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atlas_explorer_variables,
                  section_title='Atlas Explorer', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  apply_period_manager=apply_period_manager, thumbnail_size=thumbN_size)
    if do_parallel:
       index += parallel_section(section_2D_maps, **kwargs)
    else:
       index += section_2D_maps(**kwargs)

   
    if atlas_explorer_climato_variables:
       # -- Update kwargs accordingly
       kwargs.pop('add_line_of_climato_plots')
       kwargs.update(dict(variables=atlas_explorer_climato_variables, section_title='Atlas Explorer Climatologies'))
       #
       if do_parallel:
          index += parallel_section(section_climato_2D_maps, **kwargs)
       else:
          index += section_climato_2D_maps(**kwargs)



# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
if do_zonal_profiles_explorer:
    print '---------------------------------'
    print '-- Processing Zonal profiles   --'
    print '-- do_zonal_profiles = True    --'
    print '-- zonal_profiles_variables =  --'
    print '-> ',zonal_profiles_variables
    print '--                             --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='clim')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    index += section_zonal_profiles(Wmodels, reference, season, zonal_profiles_variables,
                                    'Zonal Profiles Explorer', domain=domain,
                                    safe_mode=safe_mode, alternative_dir=alternative_dir,
                                    apply_period_manager=apply_period_manager)




# ----------------------------------------------
# --                                             \
# --  Main Time series                            \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------

def convert_list_to_string(dum,separator1=',', separator2='|'):
    string = ''
    if isinstance(dum,list):
        for elt in dum:
            concat_elt = elt
            if isinstance(elt, list):
                substring = ''
                for elt2 in elt:                    
                    if substring=='':
                        substring = str(elt2)
                    else:
                        substring += separator1+str(elt2)
                concat_elt = substring    
                if string=='':
                    string = concat_elt
                else:
                    string += separator2+concat_elt
            else:
                if string=='':
                    string = str(concat_elt)
                else:
                    string += separator1+str(concat_elt)
                
        return string
    else:
        return dum

def ts_plot(ens_ts, **kwargs):
    w_kwargs = kwargs.copy()
    for kwarg in w_kwargs:
        w_kwargs[kwarg] = convert_list_to_string(w_kwargs[kwarg])
    return ensemble_ts_plot(ens_ts, **w_kwargs)


# ---------------------------------------------------------------------------------------- #
# -- Plotting the time series for the IGCMG meetings                                     -- #
if do_main_time_series:
    print '---------------------------------'
    print '-- Processing Main Time Series --'
    print '-- do_main_time_series = True  --'
    print '-- time_series_specs =         --'
    print '-> ',time_series_specs
    print '--                             --'
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("Main Time Series", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    thumbN_size = thumbnail_size
    #
    # -- Period Manager
    if not use_available_period_set:
       WWmodels_ts = period_for_diag_manager(models, diag='TS')
       WWmodels_clim = period_for_diag_manager(models, diag='clim')
       apply_period_manager = True
    else:
       WWmodels_ts = copy.deepcopy(Wmodels_ts)
       WWmodels_clim = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    WTSmodels = copy.deepcopy(WWmodels_ts)
    WCLIMmodels = copy.deepcopy(WWmodels_clim)

    #
    # -- Loop on the time series specified in the params file
    # -----------------------------------------------------------------------------------------
    for time_series in time_series_specs:
        # ==> -- Open the html line with the title
        # -----------------------------------------------------------------------------------------
        index += open_table()
        line_title = ''
        index+=start_line(line_title)
        #
        ens_ts_dict = dict()
        names_ens = []
        #
        highlight_period = []
        #
        # -- Initialize WWmodels_clim and WWmodels_ts
        WWmodels_clim = copy.deepcopy(WCLIMmodels)
        WWmodels_ts = copy.deepcopy(WTSmodels)

        # -- Project specs: pass project-specific arguments
        if 'project_specs' in time_series:
           for dataset_dict in WWmodels_clim:
               if dataset_dict['project'] in time_series['project_specs']:
                  dataset_dict.update(time_series['project_specs'][dataset_dict['project']])
           for dataset_dict in WWmodels_ts:
               if dataset_dict['project'] in time_series['project_specs']:
                  dataset_dict.update(time_series['project_specs'][dataset_dict['project']])
           time_series.pop('project_specs')
        #
        if 'highlight_period' in time_series:
            if time_series['highlight_period']=='clim_period':
                for dataset_dict in WWmodels_clim:
                    print 'dataset_dict in time_series = ', dataset_dict
                    # -- Apply period manager if needed
                    if not use_available_period_set:
                       dataset_dict.update(dict(variable=time_series['variable']))
                       frequency_manager_for_diag(dataset_dict, diag='clim')
                       get_period_manager(dataset_dict)
                    highlight_period.append( build_period_str(dataset_dict) )

        for dataset_dict in WWmodels_ts:
            #
            wdataset_dict = dataset_dict.copy()
            wdataset_dict.update(dict(variable=time_series['variable']))

            # -- Apply period manager if needed
            if not use_available_period_set:
               frequency_manager_for_diag(wdataset_dict, diag='TS')
               get_period_manager(wdataset_dict)
            #
            # -- Get the dataset
            dat = ds(**wdataset_dict)
            #
            # -- select a domain if the user provided one
            if 'domain' in time_series:
                lonmin = str(time_series['domain']['lonmin'])
                lonmax = str(time_series['domain']['lonmax'])
                latmin = str(time_series['domain']['latmin'])
                latmax = str(time_series['domain']['latmax'])
                # -- We regrid the dataset if 
                if time_series['variable'] in ocean_variables:
                   dat = regridn(dat, cdogrid='r360x180')
                #
                dat = llbox(dat,lonmin=lonmin,lonmax=lonmax,latmin=latmin,latmax=latmax) 
            #
            #
            # -- Apply the operation
            if 'operation_kwargs' in time_series:
                ts_dat = time_series['operation'](dat, **time_series['operation_kwargs'])
            else:
                ts_dat = time_series['operation'](dat)
            #
            # -- Get the name
            mem_name = build_plot_title(wdataset_dict)
            names_ens.append(mem_name)
            #
            # -- Add to the ensemble for plot
            ens_ts_dict.update({mem_name:ts_dat})
            #
        #
        # -- Finalize the CliMAF ensemble
        ens_ts = cens(ens_ts_dict, order=names_ens)
        #
        # -- Do the plot
        p = time_series.copy()
        p.pop('variable')
        if 'operation' in p: p.pop('operation')
        if 'operation_kwargs' in p: p.pop('operation_kwargs')
        if 'domain' in p: p.pop('domain')
        if highlight_period:
           p.update(dict(highlight_period = highlight_period))
        else:
           print '==> No highlight period provided => ', highlight_period
        # -- Colors
        p.update(dict(colors=colors_manager(WWmodels_ts,cesmep_python_colors)))
        print 'ens_ts = ', ens_ts
        print 'p = ', p
        myplot = ts_plot(ens_ts, **p)
        #
        # ==> -- Add the plot to the line
        # -----------------------------------------------------------------------------------------
        if 'fig_size' in time_series:
           fig_size = time_series['fig_size']
        else:
           fig_size = '15*5'
        thumbnail_main_ts = str(int(str.split(fig_size,'*')[0])*75)+'*'+str(int(str.split(fig_size,'*')[1])*75)
        index += cell("",safe_mode_cfile_plot(myplot, safe_mode=safe_mode),
                       thumbnail=thumbnail_main_ts, hover=hover, **alternative_dir)
            #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
    index+=close_line() + close_table()









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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='atm_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    for model in Wmodels: model.update(dict(table='Amon'))
    # -- Store all the arguments taken by section_2D_maps in a kwargs dictionary
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=atmos_variables,
                  section_title='Atmosphere', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  apply_period_manager=apply_period_manager)
    if do_parallel:
       index += parallel_section(section_2D_maps, **kwargs)
    else:
       index += section_2D_maps(**kwargs)





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
   hadisst_ts=dict(project="ref_ts",product='HadISST', period='1870-2010')
   aviso_ts=dict(project="ref_ts",product='AVISO-L4', period='1993-2010')
   oras4_ts=dict(project="ref_ts",product='ORAS4', period='1958-2014')


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Ocean 2D maps                                                         -- #
if do_ocean_2D_maps:
    print '----------------------------------'
    print '-- Processing Oceanic variables --'
    print '-- do_ocean_2D_maps = True      --'
    print '-- ocean_variables =            --'
    print '-> ',ocean_2D_variables
    print '--                              --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    for model in Wmodels: model.update(dict(table='Omon'))
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=ocean_2D_variables,
                  section_title='Ocean 2D maps', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  thumbnail_size=thumbN_size,
                  ocean_variables=ocean_variables,
                  apply_period_manager=apply_period_manager)
    if do_parallel:
       index += parallel_section(section_2D_maps, **kwargs)
    else:
       index += section_2D_maps(**kwargs)




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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='MLD_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    # -- Loop on the MLD diags
    for MLD_diag in MLD_diags:
        season = MLD_diag[0]
        proj = MLD_diag[1]
        #
        # -- Control the size of the thumbnail -> thumbN_size
        thumbN_size = (thumbnail_polar_size if 'SH' in proj or 'NH' in proj else thumbnail_size_global)
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
                                         safe_mode=safe_mode, regrid_option='remapdis', apply_period_manager=apply_period_manager)
        #
        # -- Add the climatology to the line
        index += cell("", ref_MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            wmodel.update(dict(table='Omon', grid='gn'))
            if 'frequency_for_annual_cycle' in wmodel: wmodel.update( dict(frequency = wmodel['frequency_for_annual_cycle']) )
            print 'wmodel = '
            MLD_climato = plot_climato(variable, wmodel, season, proj, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis', apply_period_manager=apply_period_manager)
            index += cell("",MLD_climato, thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # -- Close the line and the table of the climatos
        close_line()
        #
        # -- Close the table
        index += close_table()



# ---------------------------------------------------------------------------------------- #
# -- Wind stress curl maps: global, Pacific and North Atlantic                          -- #
# -- Winter and annual max                                                              -- #
if do_curl_maps:
    # -- Open the section and an html table
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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
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
        if not use_available_period_set:
           Wmodels = period_for_diag_manager(models, diag='2D_maps')
        for model in Wmodels:
            # -- This is a trick if the model outputs for the atmosphere and the ocean are yearly
            # -- then we need to set another frequency for the diagnostics needing monthly or seasonal outputs
            wmodel = model.copy()
            #
            # -- Compute the curl with tauu and tauv
            curl_climato = plot_curl(tauu_variable, tauv_variable, curl_variable, wmodel, season, proj, domain=domain, custom_plot_params=custom_plot_params,
                                       safe_mode=safe_mode, regrid_option='remapdis', apply_period_manager=apply_period_manager)
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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TS')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_ts)
       apply_period_manager = False
    #
    # Loop on variables,one per line
    for variable in ts_variables:
        # -- Loop on the regions
        for region in ts_basins:
            # -- Open the line with the title
            index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+')')
	        #
            # -- Loop on the models
            if not use_available_period_set:
               Wmodels = period_for_diag_manager(models, diag='ocean_basin_timeseries')
            for model in Wmodels:
                if variable=="tos" and region=="GLO":
                   print("=> comparison with HadISST")
                   basin_index=index_timeserie(model, variable, region=region, obs=hadisst_ts, prang=None, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
                if variable=="zos" and region=="GLO":
                   print("=> comparisin with AVISO-L4")
                   basin_index=index_timeserie(model, variable, region=region, obs=aviso_ts, prang=None, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
                else:
                   basin_index=index_timeserie(model, variable, region=region, obs=None, prang=None, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
                index+=cell("", basin_index, thumbnail=thumbsize_TS, hover=hover, **alternative_dir)
            index += close_line() + close_table()



# ---------------------------------------------------------------------------------------- #
# -- Plotting the MOC Diagnostics                                                       -- #
if do_ATLAS_MOC_DIAGS:

    index+=section("MOC Diagnoses",level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TS')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_ts)
       apply_period_manager = False
    #
    # List of regions (i.e. basins)
    for region in MOC_basins:
        #
	    # -- Loop on models
        # --> Vertical levels
        index+=start_line(title_region(region)+" MOC (Depth)")
        #
        if not use_available_period_set:
           Wmodels = period_for_diag_manager(models, diag='MOC_slice')
        #
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='lin', apply_period_manager=apply_period_manager)
            index+=cell("", basin_moc_slice, thumbnail=thumbsize_MOC_slice, hover=hover, **alternative_dir)
        index += close_line() + close_table()
        # -- Model levels
        index+=start_line(title_region(region)+" MOC (model levels)")
        for model in Wmodels:
            basin_moc_slice=moc_slice(model, region=region, y='index', apply_period_manager=apply_period_manager)
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
    	   # -- Loop on models
           if not use_available_period_set:
              Wmodels = period_for_diag_manager(models, diag='MOC_timeseries')
    	   for model in Wmodels:
               wmodel = model.copy()
               if 'frequency' in wmodel:
                  if wmodel['frequency'] in ['seasonal','annual_cycle']:
                     wmodel.update(dict(frequency = 'monthly', period = model['clim_period']))
               maxmoc_tserie = maxmoc_time_serie(wmodel, region='ATL', latitude=latitude, safe_mode=safe_mode,
                                                 apply_period_manager=apply_period_manager)
               index+=cell("", maxmoc_tserie, thumbnail=thumbsize_MOC_TS, hover=hover, **alternative_dir)
           index+=close_line()+close_table()



# ---------------------------------------------------------------------------------------- #
# -- Plotting the Vertical Profiles of T and S                                          -- #
if do_ATLAS_VERTICAL_PROFILES:

    index+=section("Vertical Profiles",level=4)
    # Loop on variables, one per line
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_vertical_profiles')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    for variable  in VertProf_variables:
        for obs in VertProf_obs:
            for region in VertProf_basins:
	            # -- Line title
                index+=start_line(title_region(region)+' '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
                for model in Wmodels:
                    if region=="GLO":
                       basin_profile = vertical_profile(model, variable, obs=obs, region=region,
                                                        box=None, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
                    else:
                       #mpm_to_improve: pour l'instant, pas de comparaison aux obs dans les sous-basins
                       basin_profile = vertical_profile(model, variable, obs=None, region=region,
                                                        box=None, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
                    index+=cell("", basin_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
                index+=close_line()+close_table()
	# -- Line title
        index+=start_line('Gibraltar '+varlongname(variable)+' ('+variable+') vs '+obs.get("product"))
        for model in Wmodels:
            gibr_profile = vertical_profile(model, variable, obs=obs, region='GLO',
                                            box=boxes.get("gibraltar"), safe_mode=safe_mode, apply_period_manager=apply_period_manager)
            index+=cell("", gibr_profile, thumbnail=thumbsize_VertProf, hover=hover, **alternative_dir)
        index+=close_line()+close_table()


# ---------------------------------------------------------------------------------------- #
# -- Plotting the Zonal Mean Slices                                                     -- #
if do_ATLAS_ZONALMEAN_SLICES:

    # Loop over variables
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_zonalmean_sections')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Omon', grid='gn'))
    kwargs = dict(models=Wmodels,reference=reference,zonmean_slices_variables=zonmean_slices_variables,
                  zonmean_slices_basins=zonmean_slices_basins,zonmean_slices_seas=zonmean_slices_seas,
                  custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager, custom_obs_dict=custom_obs_dict,
                  safe_mode=safe_mode, y=y, thumbsize_zonalmean=thumbsize_zonalmean, do_parallel=do_parallel,
                  hover=hover, alternative_dir=alternative_dir)
    if do_parallel:
       index += parallel_section(section_zonalmean_slices, **kwargs)
    else:
       index += section_zonalmean_slices(**kwargs)
    




# ---------------------------------------------------------------------------------------- #
# -- Plotting the Drift Profiles (Hovmoller)                                            -- #
if do_ATLAS_DRIFT_PROFILES:

    index+=section("Drift Profiles (Hovmoller)",level=4)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ocean_drift_profiles')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    Wmodels = period_for_diag_manager(models, diag='ocean_drift_profiles')
    # Loop over variables
    for variable in drift_profiles_variables:
        for region in drift_profiles_basins:
            index+=start_line('Drift vs T0: '+title_region(region)+' '+varlongname(variable)+' ('+variable+')')
            for model in Wmodels:
                basin_drift = hovmoller_drift_profile(model, variable, region=region, y=y, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
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
   # -- Period Manager
   if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='sea_ice_volume_annual_cycle')
       apply_period_manager = True
   else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
   # -- Add table
   for model in Wmodels: model.update(dict(table='SImon', grid='gn'))
   #
   # -- Do the plots and the availability check
   siv_NH = plot_SIV(Wmodels, 'NH', safe_mode=safe_mode, apply_period_manager=apply_period_manager)
   siv_SH = plot_SIV(Wmodels, 'SH', safe_mode=safe_mode, apply_period_manager=apply_period_manager)
   #
   # -- Gather the figures in an html line
   index+=open_line('Sea Ice Volume (km3))')+\
                     cell("", siv_NH, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)+\
                     cell("", siv_SH, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='sea_ice_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='SImon', grid='gn'))
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
        if not use_available_period_set:
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
                                                   custom_plot_params=custom_plot_params, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
            # -- And add to the html line
            index += cell("", SI_climato, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            #
        index+=close_line()
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
                                       safe_mode=safe_mode, apply_period_manager=apply_period_manager)
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
                                       safe_mode=safe_mode, apply_period_manager=apply_period_manager)
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
    #
    if do_ENSO_CLIVAR_sstanino3_timeseries:
       # -- Time series of SST anomalies (departures from annual cycle ---------------
       line_title = 'Time Series of Nino3 SST anomalies (departures from annual cycle)'
       index+=start_line(line_title)
       # -- Plot the reference
       ref_ENSO_tos = dict(project='ref_ts', period='1870-2010', product='HadISST', frequency='monthly')
       plot_ref_ENSO_ts_ssta =  ENSO_ts_ssta(ref_ENSO_tos, safe_mode=safe_mode)
       index+=cell("", plot_ref_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
       # And loop over the models
       # -- Period Manager
       Wmodels = period_for_diag_manager(models, diag='ENSO')
       for dataset_dict in Wmodels:
           # -- Add table
           dataset_dict.update(dict(variable='tos', table='Omon', grid='gn'))
           frequency_manager_for_diag(dataset_dict, diag='TS')
           get_period_manager(dataset_dict)
           dataset_dict.pop('variable')
       apply_period_manager = False
       #
       for model in Wmodels:
           plot_model_ENSO_ts_ssta = ENSO_ts_ssta(model, apply_period_manager=apply_period_manager, safe_mode=safe_mode)
           index+=cell("", plot_model_ENSO_ts_ssta, thumbnail=thumbnail_ENSO_ts_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_SSTA_std_maps:
       # -- Standard deviation of SST anomalies (departures from annual cycle ---------------
       # -- Upper band at the top of the section
       line_title = 'Standard Deviation of SST anomalies (deviations from annual cycle)'
       index+=start_line(line_title)
       # -- Plot the reference
       plot_ref_ENSO_std_ssta =  ENSO_std_ssta(ref_ENSO_tos, apply_period_manager=apply_period_manager, safe_mode=safe_mode)
       index+=cell("", plot_ref_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       # And loop over the models
       for model in Wmodels:
           plot_model_ENSO_std_ssta =  ENSO_std_ssta(model, apply_period_manager=apply_period_manager, safe_mode=safe_mode)
           index+=cell("", plot_model_ENSO_std_ssta, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_pr_climatology_maps:
       # -- Precipitation climatology over 'ENSO' domain ------------------------------------
       line_title = 'Annual Mean Climatology of Precipitation'
       index+=start_line(line_title)
       # -- Plot the reference
       ref_ENSO_pr = variable2reference('pr')# ; ref_ENSO_pr.update(dict(frequency='seasonal'))
       plot_ref_ENSO_pr_clim = ENSO_pr_clim(ref_ENSO_pr, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       index+=cell("", plot_ref_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       # And loop over the models
       for model in Wmodels:
           model.update(dict(table='Amon', grid='gr'))
           plot_model_ENSO_pr_clim = ENSO_pr_clim(model, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", plot_model_ENSO_pr_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_tauu_climatology_maps:
       # -- Zonal Wind stress climatology over 'ENSO' domain -------------------------------
       line_title = 'Annual Mean Climatology of Zonal Wind Stress'
       index+=start_line(line_title)
       # -- Plot the reference
       ref_ENSO_tauu = variable2reference('tauu')# ; ref_ENSO_tauu.update(dict(frequency='seasonal'))
       plot_ref_ENSO_tauu_clim = ENSO_tauu_clim(ref_ENSO_tauu, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       index+=cell("", plot_ref_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       # And loop over the models
       for model in Wmodels:
           plot_model_ENSO_tauu_clim =  ENSO_tauu_clim(model, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", plot_model_ENSO_tauu_clim, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_linearRegression_dtauu_dsstanino3_maps:
       # -- Map of linear regression coefficients = d(Zonal Wind Stress) / d(SSTA Nino3) ----
       line_title = 'Linear Regression = d(Zonal Wind Stress) / d(SSTA Nino3)'
       index+=start_line(line_title)
       # -- Plot the reference
       ref_ENSO_tauu = dict(project='ref_ts', product='ERAInterim', period='2001-2010', variable='tauu', frequency='monthly')
       ref_ENSO_tos  = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010', frequency='monthly')
       plot_ref_ENSO_tauuA_on_SSTANino3 =  ENSO_linreg_tauuA_on_SSTANino3(ref_ENSO_tauu, ref_ENSO_tos, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       index+=cell("", plot_ref_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       # And loop over the models
       for model in Wmodels:
           tos_model = model.copy() ; tos_model.update(variable='tos', table='Omon', grid='gn')
           tauu_model = model.copy() ; tauu_model.update(variable='tauu', table='Amon', grid='gr')
           plot_model_ENSO_tauuA_on_SSTANino3 =  ENSO_linreg_tauuA_on_SSTANino3(tauu_model,tos_model, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", plot_model_ENSO_tauuA_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_linearRegression_drsds_dsstanino3_maps:
       # -- Map of linear regression coefficients = d(ShortWave) / d(SSTA Nino3) ----------
       line_title = 'Linear Regression = d(ShortWave) / d(SSTA Nino3)'
       index+=start_line(line_title)
       # -- Plot the reference
       ref_ENSO_rsds = dict(project='ref_ts', product='CERES-EBAF-Ed2-7', period='2001-2010', variable='rsds', frequency='monthly')
       ref_ENSO_tos  = dict(project='ref_ts', variable='tos', product='HadISST', period='2001-2010', frequency='monthly')
       plot_ref_ENSO_rsds_on_SSTANino3 =  ENSO_linreg_rsds_on_SSTANino3(ref_ENSO_rsds, ref_ENSO_tos, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       index+=cell("", plot_ref_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       # And loop over the models
       for model in Wmodels:
           tos_model = model.copy() ; tos_model.update(variable='tos', table='Omon', grid='gn')
           rsds_model = model.copy() ; rsds_model.update(variable='rsds', table='Amon', grid='gr')
           plot_model_ENSO_rsds_on_SSTANino3 =  ENSO_linreg_rsds_on_SSTANino3(rsds_model,tos_model, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", plot_model_ENSO_rsds_on_SSTANino3, thumbnail=thumbnail_ENSO_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_SSTA_annualcycles:
       # -- Annual Cycles -----------------------------------------------------------------
       line_title = 'Annual cycles Nino3 (SST, SSTA, Std.dev)'
       index+=start_line(line_title)
       for model in Wmodels: model.update(dict(table='Omon', grid='gn'))
       plot_annual_cycles = plot_ENSO_annual_cycles(Wmodels, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       thumbN_size="600*350"
       index+=cell("", plot_annual_cycles, thumbnail=thumbN_size, hover=hover, **alternative_dir)
       close_line()
       index+=start_line('')
       for model in Wmodels:
           one_model_plot_annual_cycles = plot_ENSO_annual_cycles([model], safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", one_model_plot_annual_cycles, thumbnail=thumbN_size, hover=hover, **alternative_dir)
       close_line()
       index+=close_table()
       #
    if do_ENSO_CLIVAR_longitudinal_profile_tauu:
       # -- Longitudinal profile of Zonal Wind Stress --------------------------------------
       line_title = 'Annual Mean Climatology of Zonal Wind Stress (-5/5N profile)'
       index+=start_line(line_title)
       for model in Wmodels: model.update(dict(table='Amon', grid='gr'))
       plot_tauu_profile = plot_ZonalWindStress_long_profile(Wmodels, safe_mode=safe_mode, apply_period_manager=apply_period_manager)
       thumbN_size="450*400"
       index+=cell("", plot_tauu_profile, thumbnail=thumbN_size, hover=hover, **alternative_dir)
       close_line()
       index+=start_line('')
       for model in Wmodels:
           one_model_plot_tauu_profile = plot_ZonalWindStress_long_profile([model], safe_mode=safe_mode, apply_period_manager=apply_period_manager)
           index+=cell("", one_model_plot_tauu_profile, thumbnail=thumbN_size, hover=hover, **alternative_dir)
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
        dict(name='WAM - AMMA (-10/10E;12/20N)', domain=dict(lonmin=-10,lonmax=10,latmin=12,latmax=20)),
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

    # -- Get the reference
    pr_ref = ds(**variable2reference('pr'))
    # -- The GPCP mask is obtained by remapping the land-sea mask of the 280*280 LMDz mask on GPCP (nearest neighbour)
    #ref_mask = regrid( fds('/data/igcmg/database/grids/LMDZ4.0_280280_grid.nc', variable='mask', period='fx'), pr_ref, option='remapnn')
    if onCiclad:
       ref_mask = regrid( fds('/data/igcmg/database/grids/LMDZ4.0_280280_grid.nc', variable='mask', period='fx'), pr_ref, option='remapnn')
    if atCNRM:
       ref_mask = regrid( fds('/cnrm/est/COMMON/C-ESM-EP/grids/LMDZ4.0_280280_grid.nc', variable='mask', period='fx'), pr_ref, option='remapnn')
    if atTGCC:
       ref_mask = regrid( fds('/ccc/work/cont003/igcmg/igcmg/Database/grids/LMDZ4.0_280280_grid.nc', variable='mask', period='fx'), pr_ref, option='remapnn')
    # -- Land mask for reference
    land_ref_mask = mask(ref_mask,miss=0)
    land_pr_ref_masked = fmul(pr_ref, land_ref_mask)

    # -- Annual cycle of precipitation over land ---------------------------------------- 
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='clim')
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
    #
    # -- Loop on regions
    for region in monsoon_precip_regions:

        # -- Start line
        line_title = region['name']
        index+=start_line(line_title)
        #
        # -- Reference
        anncyc_pr_ref_masked = fmul(space_average(llbox(land_pr_ref_masked, **region['domain'])), 86400)
        
        ens_for_plot = dict(GPCP=anncyc_pr_ref_masked)
        
        # -- One plot per region -- All models on the same plot ----------------------------------------------------------------
        # -> Loop on the models
        models_order = []
        for model in Wmodels:
            
            wmodel = model.copy()
            wmodel.update(dict(variable='pr', table='Amon', grid='gr'))
            if not use_available_period_set:
               frequency_manager_for_diag(wmodel, diag='clim')
               get_period_manager(wmodel)
  
            pr_sim = ds(**wmodel)

            # Method 1 = regrid the model on the obs, and use the obs mask to compute the spatial average
            land_pr_sim_masked = fmul(regrid(pr_sim,pr_ref, option='remapcon2'), land_ref_mask)

            anncyc_pr_sim_masked = fmul(space_average(llbox(land_pr_sim_masked, **region['domain'])), 86400)
            if model['project']=='CMIP5':
               monsoon_name_in_plot = wmodel['model']
            else:
               monsoon_name_in_plot = str.replace(build_plot_title(wmodel, None), ' ','_')
            #
            if safe_mode:
               try:
                  cfile(anncyc_pr_sim_masked)
                  ens_for_plot.update({monsoon_name_in_plot:anncyc_pr_sim_masked})
                  models_order.append(monsoon_name_in_plot)
               except:
                  print 'No data for Monsoon pr diagnostic for ',model
            else:
               ens_for_plot.update({monsoon_name_in_plot:anncyc_pr_sim_masked})
               models_order.append(monsoon_name_in_plot)

        print 'ens_for_plot = ',ens_for_plot
        cens_for_plot = cens(ens_for_plot, order=['GPCP'] + models_order)
    
        plot_pr_anncyc_region = safe_mode_cfile_plot( curves(cens_for_plot, title=region['name'], X_axis='aligned',  **cpp), True, safe_mode)

        index+=cell("", plot_pr_anncyc_region, thumbnail=thumbnail_monsoon_pr_anncyc_size, hover=hover, **alternative_dir)
        close_line()

        # -- One plot per region -- One model with the ref on the plot ----------------------------------------------------------------
        # -> Loop on the models
        index += start_line('')
        for model in Wmodels:
            # -- Reinitialize the climaf ensemble for the plot
            ens_for_plot = dict(GPCP=anncyc_pr_ref_masked)

            wmodel = model.copy()
            wmodel.update(dict(variable='pr'))
            if not use_available_period_set:
               frequency_manager_for_diag(wmodel, diag='clim')
               get_period_manager(wmodel)

            pr_sim = ds(**wmodel)

            # Method 1 = regrid the model on the obs, and use the obs mask to compute the spatial average
            land_pr_sim_masked = fmul(regrid(pr_sim,pr_ref, option='remapcon2'), land_ref_mask)

            anncyc_pr_sim_masked = fmul(space_average(llbox(land_pr_sim_masked, **region['domain'])), 86400)
            if model['project']=='CMIP5':
               monsoon_name_in_plot = model['model']
            else:
               monsoon_name_in_plot = str.replace(build_plot_title(wmodel, None), ' ','_')
            #
            if safe_mode:
               try:
                  cfile(anncyc_pr_sim_masked)
                  ens_for_plot.update({monsoon_name_in_plot:anncyc_pr_sim_masked})
                  cens_for_plot = cens(ens_for_plot, order=['GPCP'] + [monsoon_name_in_plot])
               except:
                  print 'No data for Monsoon pr diagnostic for ',model
            else:
               ens_for_plot.update({monsoon_name_in_plot:anncyc_pr_sim_masked})
               cens_for_plot = cens(ens_for_plot, order=['GPCP'] + [monsoon_name_in_plot])

            plot_pr_anncyc_region_one_model = safe_mode_cfile_plot( curves(cens_for_plot, title=region['name'], X_axis='aligned',  **cpp), True, safe_mode)

            index+=cell("", plot_pr_anncyc_region_one_model, thumbnail=thumbnail_monsoon_pr_anncyc_size, hover=hover, **alternative_dir)

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
# -- Hotelling Test: evaluation metric for the spatio-temporal variability              -- #
# -- of the annual cycle                                                                -- #
if do_Hotelling_Test:
  # -- Period Manager
  if not use_available_period_set:
     Wmodels = period_for_diag_manager(models, diag='clim')
     apply_period_manager = True
  else:
     Wmodels = copy.deepcopy(Wmodels_clim)
     apply_period_manager = False
  #
  # -- For the Hotelling Test, the scripts are not declared properly as CliMAF operators
  # -- because CliMAF doesn't handle json output files at the moment (and also because of
  # -- how the scripts were written, the CEOFs plots are done along the computation of the
  # -- test; not the metrics plot that is done separately.
  # -- This is why we need to prepare the path to the output results 'hard coded'
  # -- atlas_outdir is the directory containing the atlas and all the figures (or links)
  # -- hotelling_outputdir is the independant directory where the user will store all
  # -- the results from the Hotelling test (json files, plots...) so that we will
  # -- be able to easily check the available results.
  if onCiclad:
     #hotelling_outputdir = '/prodigfs/ipslfs/dods/'+getuser()+'/C-ESM-EP/Hotelling_test_results/'
     hotelling_outputdir = path_to_cesmep_output_rootdir+'/Hotelling_test_results/'
     if not os.path.isdir(hotelling_outputdir+'json_files/'): os.makedirs(hotelling_outputdir+'json_files/')
     if not os.path.isdir(hotelling_outputdir+'CEOFs_plots/'): os.makedirs(hotelling_outputdir+'CEOFs_plots/')
     #atlas_outdir = subdir+'/Hotelling_Test/'
     atlas_outdir = atlas_dir
     if not os.path.isdir(atlas_outdir):
        os.makedirs(atlas_outdir)
     else:
        os.system('rm -f '+atlas_outdir+'*')
  #
  # -- Assign a color (if the user didn't) to the tested datasets
  # -- If the user didn't assign one, we take one from R_colorpalette defined in params_HotellingTest.py
  # -- If the user assigned one that was already attributed automatically with the mechanism above,
  # -- we replace it with another one.
  hotelling_colors = colors_manager(Wmodels, cesmep_python_colors)
  for model in Wmodels:
      model.update(dict(color=hotelling_colors[Wmodels.index(model)]))

  # -- Loop on the variables
  for variable in hotelling_variables:

      # --------------------------------------------------------------------------------------------- #
      # -->   First, prepare the annual cycle files for the reference observational datasets
      # -->   if they are not available
      # -->   At the end of this section, we have json file containing a python dictionnary
      # -->   describing the informations and access to the reference datasets.
      # --------------------------------------------------------------------------------------------- #
      # -- Create the json file RefFiles.json
      RefFileName = main_cesmep_path+'/share/scientific_packages/Hotelling_Test/reference_json_files/reference_files_GB2015_'+variable+'.json'
      # -- list_of_ref_products is the predefined list of reference products of the GB2015 ensemble
      list_of_ref_products = ['OAFlux','NCEP','NCEP2','CORE2','FSU3','NOCS-v2','J-OFURO2','GSSTFM3','IFREMER',
                              'DFS4.3','TropFlux','DASILVA','HOAPS3','ERAInterim']

      if not os.path.isfile(RefFileName) or force_compute_reference:
         # -- Get the reference files
         RefFiles = dict()
         # Scan the available files for variable
         listfiles = ds(project='ref_climatos', variable=variable)
         files = set(str.split(listfiles.baseFiles(),' '))
         for f in files:
             if get_product(f) in list_of_ref_products:
                 # -- Get the dataset and regrid to the common grid
                 refdat = regridn( ds(variable=variable, project='ref_climatos', product=get_product(f)),
                                   cdogrid=common_grid, option='remapdis')
                 RefFiles.update({get_product(f):dict(variable=variable, file=cfile(refdat))})
         #
         # -- Create the json file RefFiles.json
         # -- It contains the paths to the netcdf files of the reference observational datasets
         # -- associated with the names used in the plots
         with open(RefFileName, 'w') as fp:
            json.dump(RefFiles, fp)
         fp.close()

      # --------------------------------------------------------------------------------------------- #
      # -->   Then, we deal with the model datasets
      # --------------------------------------------------------------------------------------------- #

      # -- Add the reference_models python list => list of models used as reference results (CMIP5, AMIP...)
      Wmodels = Wmodels + reference_models
      #
      # -- Get the tested datasets
      TestFiles = dict()
      names_to_keep_order_in_atlas = []
      for model in Wmodels:
          # 
          # -- Copy the dictionary to modify it without modifying the original dictionaries
          model.update(dict(variable=variable))
          #
          # -- Use the project specs
          if model['project'] in hotelling_project_specs:
             model.update(hotelling_project_specs[model['project']])
          #
          # -- Apply the frequency and time manager
          if not use_available_period_set:
             frequency_manager_for_diag(model, diag='clim')
             get_period_manager(model)
          wmodel = model.copy()
          #
          # -- FIX TROHL
          if 'simulation' in wmodel and wmodel['project']=='IGCM_OUT':
             if wmodel['simulation'] in ['PI6AV-Sr12','TR6AV-Sr03']:
                calias('IGCM_OUT','hfls','lat_oce', scale=-1, filenameVar='histmth')
             else:
                calias('IGCM_OUT','hfls','flat', scale=-1, filenameVar='histmth')
          # -- Get the dataset, compute the annual cycle and regrid to the common grid
          dat = regridn( annual_cycle( ds(**wmodel) ), cdogrid=common_grid, option='remapdis')
          #
          # -- Get the name that will be used in the plot => customname
          # -- It will also serve to identify the dataset in the json file TestFiles
          if 'customname' in wmodel:
             customname = wmodel['customname']
          else:
             customname = str.replace(build_plot_title(wmodel, None),' ','_')
             if 'clim_period' in wmodel: wperiod=wmodel['clim_period']
             if 'period' in wmodel:
                if wmodel['period'] not in 'fx': wperiod=wmodel['period']
             if wperiod not in customname: customname = customname+'_'+wperiod
          #
          # -- Build a string that identifies the dataset in the output files names
          # -- More complete version of customname
          dataset_name_in_filename = ''
          for key in ['project','model','login','experiment','simulation','realization']:
              ds_for_keys = ds(**wmodel)
              if key in ds_for_keys.kvp:
                 if ds_for_keys.kvp[key] not in '*':
                    if dataset_name_in_filename=='':
                       dataset_name_in_filename = ds_for_keys.kvp[key]
                    else:
                       dataset_name_in_filename += '_'+ds_for_keys.kvp[key]
          # Add the customname if the user provided one (this for plotting issues)
          if 'customname' in wmodel:
             dataset_name_in_filename += '_'+str.replace(customname,' ','_')
          else:
             # Add the period
             dataset_name_in_filename += '_'+wperiod
          # -- From this, we build the names of the output files = hard coded
          # -- Names of the json file and the plots of the CEOFs
          output_res_hotelling_json_file = hotelling_outputdir+'json_files/Res-Hotelling_'+dataset_name_in_filename+'-'+variable+'.json'
          output_ceof1_figname = hotelling_outputdir+'CEOFs_plots/'+dataset_name_in_filename+'-'+variable+'-CEOFs1.pdf'
          output_ceof2_figname = hotelling_outputdir+'CEOFs_plots/'+dataset_name_in_filename+'-'+variable+'-CEOFs2.pdf'
          #
          # -- Make the output directory of the hotelling results json file if it doesn't exist
          if not os.path.isdir(os.path.dirname(output_res_hotelling_json_file)): os.makedirs(output_res_hotelling_json_file)
          #
          # -- If the result json file is not in the main output directory (hotelling_outputdir+'json_files/'),
          # -- we check whether it's available in the scientific_packages/Hotelling_Test/results/json_files
          # -- If so, we link the file in hotelling_outputdir+'json_files/'
          ref_res_hotelling_json_file = str.replace(output_res_hotelling_json_file,
                                                    hotelling_outputdir,
                                                    main_cesmep_path+'share/scientific_packages/Hotelling_Test/results/json_files/')
          #
          dataset_description_dict = dict(variable = variable,
                                          dataset_name_in_filename = dataset_name_in_filename,
                                          output_res_hotelling_json_file = output_res_hotelling_json_file,
                                          output_ceof1_figname = output_ceof1_figname,
                                          output_ceof2_figname = output_ceof2_figname,
                                          )
          # -------------------------------------------------------
          # -- Let's now compute the Hotelling Test
          # -------------------------------------------------------
          # --> We treat separately the tested models and the reference models to keep control on whether we want
          # --> to force recompute results for each batch of datasets
          # -->
          # --> The main_Hotelling.R script will use the instruction compute_hotelling='FALSE'/'TRUE'
          # --> to compute or not the Hotelling Test.
          # --> We use this mechanism rather than removing the dataset of the TestFiles list
          # --> because we need the complete list of datasets to do the plots eventually.
          # -->
          # --> First, we treat the tested models
          # ---------------------------------------
          if model not in reference_models:
            if force_compute_test==True:
               try:
                   wmodel.update(dict(file=cfile(dat), compute_hotelling='TRUE', **dataset_description_dict))
                   TestFiles.update({customname:wmodel})
                   names_to_keep_order_in_atlas.append(customname)
               except:
                   print 'Force compute = True but No dataset available for wmodel = ',wmodel
            else:
               # -- Normal case = we use the existing results (force_compute_test=False)
               if os.path.isfile(output_res_hotelling_json_file) or os.path.isfile(ref_res_hotelling_json_file):
                   # -- If the result json file is not in the main output directory (hotelling_outputdir+'json_files/'),
                   # -- we check whether it's available in the share/scientific_packages/Hotelling_Test/results/json_files
                   # -- If so, we link the file in hotelling_outputdir+'json_files/'
                   if not os.path.isfile(output_res_hotelling_json_file): os.system('ln -s '+ref_res_hotelling_json_file+' '+output_res_hotelling_json_file)
                   wmodel.update(dict(file="", compute_hotelling='FALSE', **dataset_description_dict))
                   TestFiles.update({customname:wmodel})
                   names_to_keep_order_in_atlas.append(customname)
               else:
                   # -- If we have no file already
                   try:
                      wmodel.update(dict(file=cfile(dat), compute_hotelling='TRUE', **dataset_description_dict))
                      TestFiles.update({customname:wmodel})
                      names_to_keep_order_in_atlas.append(customname)
                   except:
                      print 'Force compute = False and No dataset available for wmodel = ',wmodel
          else:
            # --> Then, we treat the reference models
            # ---------------------------------------
            if force_compute_reference_results==True:
               # -- If we force recomputing, just (try to) do it and add it to the list of test files if successfull:
               try:
                   wmodel.update(dict(file=cfile(dat), compute_hotelling='TRUE', **dataset_description_dict))
                   TestFiles.update({customname:wmodel})
               except:
                   print 'Force compute = True but No dataset available for wmodel = ',wmodel
            else:
               if os.path.isfile(output_res_hotelling_json_file) or os.path.isfile(ref_res_hotelling_json_file):
                   # -- If the json file already exists...
                   if not os.path.isfile(output_res_hotelling_json_file): os.system('ln -s '+ref_res_hotelling_json_file+' '+output_res_hotelling_json_file)
                   wmodel.update(dict(file="", compute_hotelling='FALSE', **dataset_description_dict))
                   TestFiles.update({customname:wmodel})
               else:
                   # -- If it's not there yet...
                   try:
                      wmodel.update(dict(file=cfile(dat), compute_hotelling='TRUE', **dataset_description_dict))
                      TestFiles.update({customname:wmodel})
                   except:
                      print 'Force compute = False and No dataset available for wmodel = ',wmodel
      #
      # -- Create the json file TestFiles.json
      # ------------------------------------------------
      TestFileName = main_cesmep_path+'/'+opts.comparison+'/HotellingTest/test_files_'+opts.comparison+'_'+variable+'.json'
      with open(TestFileName, 'w') as fp:
         json.dump(TestFiles, fp)
      fp.close()
      #
      # --> Now run the main_Hotelling.R script to compute the Hotelling Test on the datasets defined in TestFiles
      # --------------------------------------------------------------------------------------------------------------
      cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/Hotelling_Test/main_Hotelling.R --test_json_file '+TestFileName+' --reference_json_file '+RefFileName+' --hotelling_outputdir '+hotelling_outputdir+' --main_dir '+main_cesmep_path+'share/scientific_packages/Hotelling_Test'
      print cmd
      p=subprocess.Popen(shlex.split(cmd))
      p.communicate()
      #
      # -- We now have the Hotelling results = both metrics (but not the plot, TBD below) and CEOFs plots  
      #
      # -- Start an html section to receive the plots
      # ----------------------------------------------------------------------------------------------
      index += section('Hotelling Test Metrics (T2) in the intertropical band -20/20N (left plot) ; Annual Mean raw spatial average (right plot)', level=4)
      index+=start_line(varlongname(variable)+' ('+variable+')')

      # --> We start with the Hotelling metrics plot
      # --> by running share/scientific_packages/Hotelling_Test/Plot-Hotelling-test-results-one-variable.R
      # ----------------------------------------------------------------------------------------------
      # --> Make the plot now with the list of datasets in input
      for stat in ['T2']:
          #figname = subdir +'/'+ opts.comparison+'_'+variable+'_'+stat+'_hotelling_statistic.pdf'
          figname = atlas_dir +'/'+ opts.comparison+'_'+variable+'_'+stat+'_hotelling_statistic.pdf'
          cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/Hotelling_Test/Plot-Hotelling-test-results-one-variable.R --test_json_files '+TestFileName+' --figname '+figname+' --main_dir '+main_cesmep_path+'share/scientific_packages/Hotelling_Test --statistic '+stat
          print cmd
          p=subprocess.Popen(shlex.split(cmd))
          p.communicate()
          # -- Add the figure (hard coded) to the html line in a cell (climaf.html function)
          pngfigname = str.replace(figname,'pdf','png')
          os.system('convert -density 150 '+figname+' -quality 90 '+pngfigname)
          index+=cell("", os.path.basename(pngfigname), thumbnail="650*600", hover=False)
      #
      # --> The Hotelling statistic is about the spatio-temporal variability of the annual cycle
      # --> Here we add a plot with the raw spatial averages over the domain and other potential domains
      # --> to give a more comprehensive view of the evaluation of the turbulent fluxes 
      #
      # --> Include the plot of the averages over defined regions
      regions_for_spatial_averages = [ dict(region_name='Intertropical_Band', domain=[-20,20,0,360] ) ]
      # -- Prepare the references
      references = []
      for ref in list_of_ref_products:
          ref_dict = dict(product=ref, variable=variable, project='ref_climatos')
          try:
             cfile(ds(**ref_dict))
             ref_dict.update(dict(customname=ref))
             references.append( ref_dict )
          except:
             print 'No dataset for ', variable, ref
      #
      # -- We need to apply the same mask to all the datasets to compute the same spatial average
      # -- For this, we build the mask from the ensemble mean of the annual means of the regridded references on the common grid
      ens_dict = dict()
      commongrid='r180x90'
      for ref in references:
          ens_dict.update({ref['product']:llbox(regridn(clim_average(ds(**ref),season), cdogrid=commongrid, option='remapdis'),
                                                lonmin=0,lonmax=360,latmin=-20,latmax=20)})
      ens = cens(ens_dict)
      ens_mean = ccdo_ens(ens, operator='ensavg')
      # -- We obtain the mask (Fill_values and 1) by dividing the ensemble mean of the references by itself
      #mask = divide(ens_mean,ens_mean)
      mask = ccdo(divide(ens_mean,ens_mean), operator='selname,'+variable)
      #
      # ------------------------------------------------
      # -- Start computing the spatial averages
      # ------------------------------------------------
      all_dataset_dicts = Wmodels + references # -> reference_models already is in Wmodels from above
      #
      results = dict()
      for dataset_dict in all_dataset_dicts:
          #
          # -- We already applied time manager, no need to re-do it (loosing time searching for the available periods)
          wdataset_dict = dataset_dict.copy()
          #
          # -- Build customname and update dictionnary => we need customname anyway, for references too
          if 'customname' in wdataset_dict:
              customname = wdataset_dict['customname']
          else:
              customname = str.replace(build_plot_title(wdataset_dict, None),' ','_')
   	      wperiod = ''
	      if 'clim_period' in wdataset_dict: wperiod=wdataset_dict['clim_period']
	      if 'period' in wdataset_dict:
                  if wdataset_dict['period'] not in 'fx': wperiod=wdataset_dict['period']
              if wperiod not in customname: customname = customname+'_'+wperiod
          customname = str.replace(customname,' ','_')
          wdataset_dict.update(dict(customname = customname))
          #
          # -- We tag the datasets to identify if they are: test_dataset, reference_dataset or obs_reference
          # -- This information is used by the plotting R script.
          if dataset_dict in Wmodels: 
             wdataset_dict.update(dict(dataset_type='test_dataset'))
          if dataset_dict in reference_models:
             wdataset_dict.update(dict(dataset_type='reference_dataset'))
          if dataset_dict in references:
             wdataset_dict.update(dict(dataset_type='obs_reference'))
          dataset_name = customname
          results[dataset_name] = dict(results=dict(), dataset_dict=wdataset_dict)
          #
          # -- Loop on the regions; build the results dictionary and save it in the json file variable_comparison_spatial_averages_over_regions.json
          for region in regions_for_spatial_averages:
              dat = llbox(regridn(clim_average(ds(**wdataset_dict), season), cdogrid=commongrid, option='remapdis'),
                          lonmin=region['domain'][2], lonmax=region['domain'][3],
                          latmin=region['domain'][0], latmax=region['domain'][1])
              # Garde fou
              dat = ccdo(dat, operator='selname,'+variable)
              if safe_mode:
                 try:
                    #metric = cMA(space_average(multiply(dat,mask)))[0][0][0]
                    metric = cscalar(space_average(multiply(dat,mask)))
                 except:
                    print 'cMA(space_average(multiply(dat,mask)))[0][0][0] has failed for wdataset_dict = ',wdataset_dict
                    metric = 'NA'
              else:
                 #metric = cMA(space_average(multiply(dat,mask)))[0][0][0]
                 print 'cfile(dat) = ', cfile(dat)
                 print 'cfile(mask) = ', cfile(mask)
                 metric = cscalar(space_average(multiply(dat,mask)))
              #
              results[dataset_name]['results'].update( {region['region_name']: str(metric) })

      outjson = main_cesmep_path+'/'+opts.comparison+'/HotellingTest/'+variable+'_'+opts.comparison+'_spatial_averages_over_regions.json'
      results.update(dict(json_structure=['dataset_name','results','region_name'],
                          variable=dict(variable=variable, varlongname=varlongname(variable))))
      #
      # -- Eventually, do the plots
      for region in regions_for_spatial_averages:
          with open(outjson, 'w') as outfile:
               json.dump(results, outfile, sort_keys = True, indent = 4)
          #figname = subdir+ '/'+ opts.comparison+'_'+variable+'_'+region['region_name']+'_space_averages_over_.png'
          figname = atlas_dir+ '/'+ opts.comparison+'_'+variable+'_'+region['region_name']+'_space_averages_over_.png'
          cmd = 'Rscript --vanilla '+main_cesmep_path+'share/scientific_packages/Hotelling_Test/plot_space_averages_over_regions.R --metrics_json_file '+outjson+' --region '+region['region_name']+' --figname '+figname
          print(cmd)
          os.system(cmd)
          index+=cell("", os.path.basename(figname), thumbnail="650*600", hover=False)

      # -- Close the line and the section
      index += close_line() + close_table()


      # --> Then we add a section for the variable to store the plots of the CEOFs 
      # --> that are produced automatically by main_Hotelling.R -> Hotelling_routine.R -> Fig-common-EOFS-First-reduction.R 
      # ----------------------------------------------------------------------------------------------------------------------
      index += section('First (CEOF1) and second (CEOF2) Common EOFs with the projections', level=4)
      index+=start_line(varlongname(variable)+' ('+variable+')')
      for dataset_name in names_to_keep_order_in_atlas:
          # -- Add the CEOF1 plot figure (hard coded) to the html line in a cell (climaf.html function)
          pdffigname_ceof1 = TestFiles[dataset_name]['output_ceof1_figname']
          #pngfigname_ceof1 = str.replace(str.replace(pdffigname_ceof1,'pdf','png'), hotelling_outputdir+'CEOFs_plots', subdir)
          pngfigname_ceof1 = str.replace(str.replace(pdffigname_ceof1,'pdf','png'), hotelling_outputdir+'CEOFs_plots', atlas_dir)
          os.system('convert -density 150 '+pdffigname_ceof1+' -quality 90 '+pngfigname_ceof1)
          if variable=='hfls':
             ceof_thumbnail = "650*450"
          else:
             ceof_thumbnail = "650*300"
          index+=cell("", os.path.basename(pngfigname_ceof1), thumbnail=ceof_thumbnail, hover=False)
          # -- Add the CEOF2 plot figure (hard coded) to the html line in a cell (climaf.html function)
          # --> To do if needed
      # -- Close the line and the section
      index += close_line() + close_table()


# ---------------------------------------------------------------------------------------- #
# -- Global plot Turbulent fluxes                                                       -- #
if do_GLB_SFlux_maps:
    # -- Open the section and an html table
    index += section("Turbulent Fluxes Annual Mean", level=4)
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    # -- Loop on the turbulent fluxes variables
    for variable in TurbFluxes_variables:
        #
        # -- we copy the dictionary to midfy it inside the loop
        wmodel = Wmodels[0].copy()
        #
        # -- Here, we add table='Amon' for the CMIP5 outputs
        wmodel.update(dict(variable=variable,table='Amon'))
        # -- Use the project specs
        if wmodel['project'] in TurbFluxes_project_specs:
           wmodel.update(TurbFluxes_project_specs[wmodel['project']])
        #
        # -- Plot using plot_climato_TurbFlux_GB2015
        # --> Global Annual Mean
        # --> For the simulation
        GLB_plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
        # --> And for the reference
        GLB_plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Global',
                                                                custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
        #
        # -- Open the html line with the title
        line_title = 'GLOBAL Annual Mean '+varlongname(variable)+' ('+variable+')'
        index += start_line(line_title)
	#
        # -- Add the plots at the beginning line
        # --> First, the climatology of the reference
        index += cell("", GLB_plot_climato_ref_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
        # --> Then, the climatology of the first model
        index += cell("", GLB_plot_climato_sim_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
        #
        # -- Loop on the models (add the results to the html line)
        for model in Wmodels:
            wmodel = model.copy()
            wmodel.update(dict(variable=variable,table='Amon'))
            GLB_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, climatology='ANM', region='Global', custom_plot_params=custom_plot_params, apply_period_manager=apply_period_manager)
            index=index+cell("", GLB_bias_ANM, thumbnail=thumbnail_size_global, hover=hover, **alternative_dir)
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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='TurbulentAirSeaFluxes')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    #
    for variable in TurbFluxes_variables:
        # -- Second Line: Climatos seasons REF + models
        # -- Third line: bias maps
        # -- First line: Climato ANM -----------------------------------------------------
        line_title = varlongname(variable)+' ('+variable+') => Annual Mean Climatology - GB2015, Model and bias map'
        index+=start_line(line_title)
        # -- Plot the reference
        plot_climato_ref_ANM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        #
        # -- We apply the frequency and time manager once per variable
        # -- For this we create a Wmodels_var per variable
        from copy import deepcopy
        Wmodels_var = deepcopy(Wmodels)
        for model in Wmodels_var:
            model.update(dict(variable=variable))
            # -- Use the project specs
            if model['project'] in TurbFluxes_project_specs:
               model.update(TurbFluxes_project_specs[model['project']])
            if not use_available_period_set:
               frequency_manager_for_diag(model, diag='clim')
               get_period_manager(model)

        # And loop over the models
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_ANM = plot_climato_TurbFlux_GB2015(variable, wmodel, climatology='ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_ANM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'ANM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
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
        plot_climato_ref_DJF = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_MAM = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_JJA = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
        plot_climato_ref_SON = plot_climato_TurbFlux_GB2015(variable,'GB2015',climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
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
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_climato_sim_DJF = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_MAM = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_JJA = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_climato_sim_SON = plot_climato_TurbFlux_GB2015(variable,wmodel,climatology='SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
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
        for model in Wmodels_var:
            wmodel = model.copy()
            sim = ds(**wmodel)
            plot_bias_DJF = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'DJF', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_MAM = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'MAM', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_JJA = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'JJA', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            plot_bias_SON = plot_bias_TurbFlux_vs_GB2015(variable, wmodel, 'SON', region='Tropics', custom_plot_params=custom_plot_params, do_cfile=False, apply_period_manager=apply_period_manager)
            seas_bias_plot= cpage(fig_lines=[[plot_bias_DJF],[plot_bias_MAM],[plot_bias_JJA],[plot_bias_SON]],fig_trim=True,page_trim=True,
                                  title=sim.model+' '+sim.simulation+' (vs GB2015)',
                                  gravity='NorthWest',
                                  ybox=80, pt=30,
                                  x=30, y=40,
                                  font='Waree-Bold'
                                 )
            if safe_mode==True:
               try:
                  index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
               except:
                  index+=cell("", blank_cell, thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
            else:
               index+=cell("", cfile(seas_bias_plot), thumbnail=thumbnail_polar_size, hover=hover, **alternative_dir)
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
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='PISCES_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Omon'))
    #if do_parallel:
    #   index += parallel_section_2D_maps(Wmodels, reference, proj, season, ocebio_2D_variables,
    #                         'Ocean Biogeochemistry 2D', domain=domain, custom_plot_params=custom_plot_params,
    #                         add_product_in_title=add_product_in_title, safe_mode=safe_mode,
    #                         add_line_of_climato_plots=add_line_of_climato_plots,
    #                         alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
    #                         apply_period_manager=apply_period_manager)#, thumbnail_size=thumbN_size)
    #else:
    #   index += section_2D_maps(Wmodels, reference, proj, season, ocebio_2D_variables,
    #                         'Ocean Biogeochemistry 2D', domain=domain, custom_plot_params=custom_plot_params,
    #                         add_product_in_title=add_product_in_title, safe_mode=safe_mode,
    #                         add_line_of_climato_plots=add_line_of_climato_plots,
    #                         alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
    #                         #thumbnail_size=thumbN_size,
    #                         ocean_variables=ocean_variables,
    #                         apply_period_manager=apply_period_manager)
    #
    kwargs = dict(models=Wmodels, reference=reference, proj=proj, season=season, variables=ocebio_2D_variables,
                  section_title='Ocean Biogeochemistry 2D', domain=domain, custom_plot_params=custom_plot_params,
                  add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                  add_line_of_climato_plots=add_line_of_climato_plots,
                  alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                  ocean_variables=ocean_variables,
                  apply_period_manager=apply_period_manager)
    if do_parallel:
       index += parallel_section(section_2D_maps, **kwargs)
    else:
       index += section_2D_maps(**kwargs)







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
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_energy_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_energy_budget_bias,
                                                         'ORCHIDEE Energy Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							 custom_plot_params=custom_plot_params, shade_missing=True, safe_mode=safe_mode,
							 alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                                                         apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Energy_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_bias=[]
    for tmpvar in variables_energy_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_energy_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_energy_budget_bias,
                             'ORCHIDEE Energy Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode, 
                             add_line_of_climato_plots=add_line_of_climato_plots,
	                     alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    wvariables_energy_budget_modelmodel=[]
    for tmpvar in variables_energy_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_energy_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_energy_budget_modelmodel,
                             'ORCHIDEE Energy Budget, difference with first simulation', domain=domain, 
                              add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                              add_line_of_climato_plots=add_line_of_climato_plots,
			      custom_plot_params=custom_plot_params, alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                              apply_period_manager=apply_period_manager)



if do_ORCHIDEE_Energy_Budget_diff_with_ref_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Energy Budget Variables                        --'
    print '-- do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_energy_budget =                                          --'
    print '-> ',variables_energy_budget
    print '--                                                                    --'
    for tmpvar in variables_energy_budget:
        if 'PFT' in tmpvar: derive_var_PFT(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, refsimulation, proj, season, variables_energy_budget,
                             'ORCHIDEE Energy Budget, difference with a reference (climatological month, season)', domain=domain,
                              add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                              add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
	 		      custom_plot_params=custom_plot_params, alternative_dir=alternative_dir,
                              apply_period_manager=apply_period_manager)



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
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_water_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                                                         'ORCHIDEE Water Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							 shade_missing=True, safe_mode=safe_mode, custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict,
							 alternative_dir=alternative_dir,
                                                         apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Water_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climobs_bias_maps = True  --'
    print '-- variables_water_budget =                                          --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_bias=[]
    for tmpvar in variables_water_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_water_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_water_budget_bias,
                             'ORCHIDEE Water Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			     alternative_dir=alternative_dir, apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Water Budget Variables                         --'
    print '-- do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps = True   --'
    print '-- variables_water_budget =                                           --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    wvariables_water_budget_modelmodel=[]
    for tmpvar in variables_water_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_water_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_water_budget_modelmodel,
                             'ORCHIDEE Water Budget, difference with first simulation', domain=domain,
                              add_product_in_title=add_product_in_title, custom_plot_params=custom_plot_params,
                              add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			      shade_missing=True, safe_mode=safe_mode, alternative_dir=alternative_dir,
                              apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Water_Budget_climatology_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Water_Budget_climatology_maps = True                  --'
    print '-- variables_water_budget =                                          --'
    print '-> ',variables_water_budget
    print '--                                                                    --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
           model.update(dict(DIR='SBG'))
    index += section_climato_2D_maps(Wmodels, None, proj, season, variables_water_budget,
                             'ORCHIDEE Water Budget, climatologies', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager, thumbnail_size=thumbnail_size)




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
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_carbon_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
           model.update(dict(DIR='SBG'))
    index += section_2D_maps_climobs_bias_modelmodeldiff(Wmodels, reference, proj, season, wvariables_carbon_budget_bias,
                                                         'ORCHIDEE Carbon Budget, Climato OBS, Bias and model-model differences',
                                                         domain=domain, add_product_in_title=add_product_in_title,
							 shade_missing=True, safe_mode=safe_mode, custom_plot_params=custom_plot_params,
                                                         custom_obs_dict=custom_obs_dict, alternative_dir=alternative_dir,
                                                         apply_period_manager=apply_period_manager)


if do_ORCHIDEE_Carbon_Budget_climobs_bias_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_bias=[]
    for tmpvar in variables_carbon_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
           wvariables_carbon_budget_bias.append(tmpvar)
        except:
           print 'No obs for ',tmpvar
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
           model.update(dict(DIR='SBG'))
    index += section_2D_maps(Wmodels, reference, proj, season, wvariables_carbon_budget_bias,
                             'ORCHIDEE Carbon Budget, Climato OBS and Bias maps', custom_plot_params=custom_plot_params,
                             domain=domain, add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
                             alternative_dir=alternative_dir,
                             apply_period_manager=apply_period_manager)



if do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps = True  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    wvariables_carbon_budget_modelmodel=[]
    for tmpvar in variables_carbon_budget:
        if isinstance(tmpvar,dict):
           ttmpvar = tmpvar['variable']
        else:
           ttmpvar = tmpvar
        if 'PFT' in ttmpvar: derive_var_PFT(ttmpvar)
        try:
           cfile(ds(**variable2reference(ttmpvar, my_obs=custom_obs_dict)))
        except:
           wvariables_carbon_budget_modelmodel.append(tmpvar)
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
           model.update(dict(DIR='SBG'))
    index += section_2D_maps(Wmodels[1:len(Wmodels)], Wmodels[0], proj, season, wvariables_carbon_budget_modelmodel,
                             'ORCHIDEE Carbon Budget, difference with first simulation', domain=domain,
                             add_product_in_title=add_product_in_title, shade_missing=True, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots, custom_obs_dict=custom_obs_dict,
			     custom_plot_params=custom_plot_params, alternative_dir=alternative_dir,
                             apply_period_manager=apply_period_manager)

if do_ORCHIDEE_Carbon_Budget_climatology_maps:
    print '------------------------------------------------------------------------'
    print '-- Processing ORCHIDEE Carbon Budget Variables                        --'
    print '-- do_ORCHIDEE_Carbon_Budget_climatology_maps = True                  --'
    print '-- variables_carbon_budget =                                          --'
    print '-> ',variables_carbon_budget
    print '--                                                                    --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='ORCHIDEE_2D_maps')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    # -- Add table
    for model in Wmodels: model.update(dict(table='Lmon'))
    # -- Garde fou to avoid missing the first simulation
    WWmodels = copy.deepcopy(Wmodels)
    for model in WWmodels:
        if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
           Wmodels.remove(model)
    # -- Work on SBG file (for IGCM_OUT)
    for model in Wmodels:
        if model['project'] in ['IGCM_OUT']:
           model.update(dict(DIR='SBG'))
    index += section_climato_2D_maps(Wmodels, None, proj, season, variables_carbon_budget,
                             'ORCHIDEE Carbon Budget, climatologies', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager, thumbnail_size=thumbnail_size)




# ----------------------------------------------
# --                                             \
# --  Tests O. Torres                             \
# --  MSE export                                  /
# --  Also used as an example of how to plug     /
# --  an external script with cscript           /
# --                                           /
# --                                          /
# -------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- MSE export maps                                                                    -- #
if do_mse_otorres_maps:
    #
    # -- Declare UEVE script (O.Torres)
    # -- After this operation, you will be able to use the script as:
    # --    MSE_plot = ueve_otorres(ue_dat, ve_dat, aire_dat, pourc_ter_dat, title=title, **default_ueve)
    # -- **default_ueve is a mechanism to pass the keyword/values defined in the default_ueve dictionary
    # -- to the function (python mechanism).
    # -- See the documentation of cscript for more details: http://climaf.readthedocs.io/en/latest/functions_processing.html 
    ueve_script = main_cesmep_path+'share/scientific_packages/UEVE_otorres/UE_VE_plot_CLIMAF_plug.py'
    cscript('ueve_otorres',
            'python '+ueve_script+' ${in} ${in_2} ${in_3} ${in_4} "${title}" "${arrow_width}" '+
                 '"${colorbar}" "${narrow_x}" "${narrow_y}" "${arrow_scale}" "${min}" "${max}" "${land_mask_value}" ${out}',
            format='graph')
    #
    # -- Open the section and an html table
    index += section("MSE Export", level=4)
    #
    # -- use season from params
    # -- Control the size of the thumbnail -> thumbN_size
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    #
    # -- Open the html line with the title
    index += open_table()
    line_title = 'MSE Export'
    index+=start_line(line_title)
    #
    # -- Loop on the models (add the results to the html line)
    Wmodels = period_for_diag_manager(models, diag='clim')
    for model in Wmodels:
        # -- Apply frequency and period manager
        wmodel_var = model.copy() # - copy the dictionary to avoid modifying the original dictionary
        wmodel_var.update(dict(variable='ue')) # - add a variable to this dictionary; it will be used by frequency_manager_for_diag
        #                                          and get_period_manager to scan the existing files and find the requested period
        frequency_manager_for_diag(wmodel_var, 'clim') # - Apply frequency_manager_for_diag
        get_period_manager(wmodel_var) # - Apply get_period_manager
        wmodel = wmodel_var.copy() # - copy wmodel_var to do a new dictionary wmodel without the variable name (used below to get the datasets)
        wmodel.pop('variable')
        #
        # -- Get ue and ve and compute the climatology
        ue_dat = clim_average( ds(variable='ue', **wmodel), season )
        ve_dat = clim_average( ds(variable='ve', **wmodel), season )
        #
        # -- Get aire and pourc_ter
        aire_dat = ds(variable='aire', **wmodel)
        pourc_ter_dat = ds(variable='pourc_ter', **wmodel)
        #
        # -- Build the title
        title = build_plot_title(wmodel_var,None)#+'_'+build_period_str(wmodel_var)
        # -- Compute the MSE export and do the plot with ueve_otorres
        MSE_plot = ueve_otorres(ue_dat, ve_dat, aire_dat, pourc_ter_dat, title=title, **default_ueve)
        #
        # -- Add the plot to the line
        index += cell("",safe_mode_cfile_plot(MSE_plot, safe_mode=safe_mode), thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #cfile(MSE_plot, target='/home/otorres/myfigure.png')
        #
    # -- Close the line and the table of the climatos
    index+=close_line() + close_table()
    #
if do_mse_otorres_diff_maps:
    # -- Second part of the analysis = compute differences
    # -- Declare UEVE script for differences (O.Torres)
    ueve_script_diff = main_cesmep_path+'share/scientific_packages/UEVE_otorres/UE_VE_plot_CLIMAF_diff_plug.py'
    cscript('ueve_otorres_diff',
            'python '+ueve_script_diff+' ${in} ${in_2} ${in_3} ${in_4} ${in_5} ${in_6} "${title}" "${arrow_width}" '+
                 '"${colorbar}" "${narrow_x}" "${narrow_y}" "${arrow_scale}" "${min}" "${max}" "${land_mask_value}" ${out}',
            format='graph')
    #
    # -- Open the html line with the title
    index += open_table()
    line_title = 'MSE Export Diff'
    index+=start_line(line_title)
    #
    # -- Preparing the reference simulation
    # -- Apply frequency and period manager
    if reference=='default':
       ref_mse_diff = models[0].copy()
    else:
       ref_mse_diff = reference.copy()
    wref_var = ref_mse_diff.copy() # - copy the dictionary to avoid modifying the original dictionary
    wref_var.update(dict(variable='ue')) # - add a variable to this dictionary; it will be used by frequency_manager_for_diag
    #                                          and get_period_manager to scan the existing files and find the requested period
    frequency_manager_for_diag(wref_var, 'clim') # - Apply frequency_manager_for_diag
    get_period_manager(wref_var) # - Apply get_period_manager
    wref = wref_var.copy() # - copy wmodel_var to do a new dictionary wmodel without the variable name (used below to get the datasets)
    wref.pop('variable')
    #
    # -- Get ue and ve and compute the climatology
    ue_ref = clim_average( ds(variable='ue', **wref), season )
    ve_ref = clim_average( ds(variable='ve', **wref), season )
    #
    # -- Copy of models to avoid modifying it
    models_for_diff = copy.deepcopy(models)
    # -- and remove the reference of the list
    models_for_diff.remove(ref_mse_diff)

    # -- Loop on the models (add the results to the html line)
    Wmodels = period_for_diag_manager(models_for_diff, diag='clim')
    for model in Wmodels:
        # -- Apply frequency and period manager
        wmodel_var = model.copy() # - copy the dictionary to avoid modifying the original dictionary
        wmodel_var.update(dict(variable='ue')) # - add a variable to this dictionary; it will be used by frequency_manager_for_diag
        #                                          and get_period_manager to scan the existing files and find the requested period
        frequency_manager_for_diag(wmodel_var, 'clim') # - Apply frequency_manager_for_diag
        get_period_manager(wmodel_var) # - Apply get_period_manager
        wmodel = wmodel_var.copy() # - copy wmodel_var to do a new dictionary wmodel without the variable name (used below to get the datasets)
        wmodel.pop('variable')
        #
        # -- Get ue and ve and compute the climatology
        ue_dat = clim_average( ds(variable='ue', **wmodel), season )
        ve_dat = clim_average( ds(variable='ve', **wmodel), season )
        #
        # -- Get aire and pourc_ter
        aire_dat = ds(variable='aire', **wmodel)
        pourc_ter_dat = ds(variable='pourc_ter', **wmodel)
        #
        # -- Build the title
        title = build_plot_title(wmodel_var, wref_var)#+'_'+build_period_str(wmodel_var)
        # -- Compute the MSE export and do the plot with ueve_otorres
        MSE_diff_plot = ueve_otorres_diff(ue_ref, ve_ref, ue_dat, ve_dat, aire_dat, pourc_ter_dat, title=title, **default_ueve_diff)
        #
        # -- Add the plot to the line
        index += cell("",safe_mode_cfile_plot(MSE_diff_plot, safe_mode=safe_mode), thumbnail=thumbN_size, hover=hover, **alternative_dir)
        #
    # -- Close the line and the table of the climatos
    index+=close_line() + close_table()



# ----------------------------------------------
# --                                             \
# --  Add your own CliMAF diagnostic              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- Your own diagnostic script                                                         -- #
# -- This section is a copy of the previous section; it is a good example               -- #
# -- of how to add your own script/diagnostic                                           -- # 
# -- The section starting with comments with ==> at the beginning are mandatory to      -- #
# -- build a section in the C-ESM-EP. The comments starting with /// identify code that -- #
# -- is specific to the diagnostic presented here.                                      -- #
if do_my_own_climaf_diag:
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("My own CliMAF diagnostic", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    #
    # ==> -- Open the html line with the title
    # -----------------------------------------------------------------------------------------
    index += open_table()
    line_title = 'Diag #1 = amplitude of the annual cycle'
    index+=start_line(line_title)
    #
    # ==> -- Apply the period_for_diag_manager (not actually needed here)
    # -----------------------------------------------------------------------------------------
    Wmodels = copy.deepcopy(models)
    #
    # -- Define plot parameters per variable -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_plot_params = dict(
       tas = dict(contours=1, min=0, max=60, delta=5, color='precip3_16lev'),
       pr  = dict(contours=1, min=0, max=30, delta=2, color='precip_11lev', scale=86400.),

    )
    #
    # -- Loop on the variables defined in my_own_climaf_diag_variables -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_variables = ['tas', 'pr']
    for variable in my_own_climaf_diag_variables:
        #
        # -- Loop on the models
        # -----------------------------------------------------------------------------------------
        for model in Wmodels:
            #
            # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
            # -- in the list models, and add the variable
            # -----------------------------------------------------------------------------------------
            wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
            wmodel.update(dict(variable=variable)) # - add a variable to the dictionary with update
            #
            # ==> -- Apply frequency and period manager
            # -----------------------------------------------------------------------------------------
            # ==> -- They aim at finding the last SE or last XX years available when the user provides
            # ==> -- clim_period='last_SE' or clim_period='last_XXY'...
            # ==> -- and get_period_manager scans the existing files and find the requested period
            # ==> -- !!! Both functions modify the wmodel so that it will point to the requested period
            frequency_manager_for_diag(wmodel, 'clim')
            get_period_manager(wmodel)
            #
            # /// -- Get the dataset and compute the annual cycle
            # -----------------------------------------------------------------------------------------
            dat = annual_cycle( ds(**wmodel) )
            #
            # -- Compute the amplitude of the annual cycle (max - min)
            # -----------------------------------------------------------------------------------------
            amp = minus( ccdo(dat, operator='timmax'), ccdo(dat, operator='timmin') )
            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            title = build_plot_title(wmodel,None) # > returns the model name if project=='CMIP5'
            #                                         otherwise it returns the simulation name
            #                                         It returns the name of the reference if you provide
            #                                         a second argument ('dat1 - dat2')
            LeftString = variable
            RightString = build_str_period(wmodel)  # -> finds the right key for the period (period of clim_period)
            CenterString = 'Seas cyc. amplitude'
            #
            # -- Plot the amplitude of the annual cycle
            # -----------------------------------------------------------------------------------------
            plot_amp = plot(amp, title=title, gsnLeftString = LeftString, gsnRightString = RightString, gsnCenterString = CenterString,
                            **my_own_climaf_diag_plot_params[variable] )
            #
            # ==> -- Add the plot to the line
            # -----------------------------------------------------------------------------------------
            index += cell("",safe_mode_cfile_plot(plot_amp, safe_mode=safe_mode),
                          thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # ==> -- Close the line and the table for this section
        # -----------------------------------------------------------------------------------------
        index+=close_line() + close_table()



# ----------------------------------------------
# --                                             \
# --  Raw plot of climatologies on variables      \
# --  with undefined plot parameters              /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- Your own diagnostic script                                                         -- #
# -- This section is a copy of the previous section; it is a good example               -- #
# -- of how to add your own script/diagnostic                                           -- #
# -- The section starting with comments with ==> at the beginning are mandatory to      -- #
# -- build a section in the C-ESM-EP. The comments starting with /// identify code that -- #
# -- is specific to the diagnostic presented here.                                      -- #
if do_plot_raw_climatologies:
    #
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    if atlas_explorer_climato_variables:
       #
       for variable in ping_2D_variables:
         if isinstance(variable,dict):
           #
           # -- Preliminary step: check the range of values across the models
           # -----------------------------------------------------------------------------------------
           min_values = []
           max_values = []
           for model in Wmodels:
               #
               # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
               # -- in the list models, and add the variable
               # -----------------------------------------------------------------------------------------
               wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
               wmodel.update(variable) # - add a variable to the dictionary with update
               #wmodel.update(dict(variable=variable['variable'])) # - add a variable to the dictionary with update
               if apply_period_manager:
                  frequency_manager_for_diag(wmodel, 'clim')
                  get_period_manager(wmodel)
               #
               # /// -- Get the dataset and compute the annual cycle
               # -----------------------------------------------------------------------------------------
               try:
                  print 'wmodel =======> ',wmodel
                  dat = time_average( ds(**wmodel) )
                  #
                  min_values.append( cscalar(ccdo(dat,operator='fldmin')) )
                  max_values.append( cscalar(ccdo(dat,operator='fldmax')) )
               except:
                  print 'No data found for wmodel = ',wmodel
               #
           min_val = float('%s' % float('%.2g' % min(min_values)))
           max_val = float('%s' % float('%.2g' % max(max_values)))
           import numpy as np
           my_colors_list = np.linspace(min_val,max_val,num=11)
           my_colors_str=''
           for cl in my_colors_list:
               if my_colors_str=='':
                  my_colors_str+=str(cl)
               else:
                  my_colors_str+=' '+str(cl)
           variable.update(dict(colors=my_colors_str))   
       index += section_climato_2D_maps(Wmodels, reference, proj, season, ping_2D_variables,
                             'Atlas Explorer Climatologies', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager, thumbnail_size=thumbN_size)
    #
    #
    ## ==> -- Open the section and an html table
    ## -----------------------------------------------------------------------------------------
    #index += section("Raw climatologies", level=4)
    ##
    ## ==> -- Control the size of the thumbnail -> thumbN_size
    ## -----------------------------------------------------------------------------------------
    #if thumbnail_size:
    #   thumbN_size = thumbnail_size
    #else:
    #  # thumbN_size = thumbnail_size_global
    ##
    #for var in ping_2D_variables:
    #    # -- decompose the var dictionary
    #    # -----------------------------------------------------------------------------------------
    #    if isinstance(var,dict):
    #       variable = var['variable']
    #       #p = var.copy()
    #       #p.pop('variable')
    #       if 'line_title' in var:
    #          line_title = var['line_title']
    #          var.pop('line_title')
    #       else:
    #          line_title = variable
    #       #if 'display_field_stats' in var:
    #       #   display_field_stats=var['display_field_stats']
    #       #   p.pop('display_field_stats')
    #       #else:
    #       #   display_field_stats=False
    #    else:
    #       variable = var
    #       line_title = variable
    #       p = dict()
    #    #
    #    # ==> -- Open the html line with the title
    #    # -----------------------------------------------------------------------------------------
    #    index += open_table()
    #    #line_title = variable+' = '+var_description[variable]
    #    index+=start_line(line_title)
    #    #
    #    Wmodels = copy.deepcopy(models)
    #    #
    #    # -- Preliminary step: check the range of values across the models
    #    # -----------------------------------------------------------------------------------------
    #    min_values = []
    #    max_values = []
    #    for model in Wmodels:
    #        #
    #        # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
    #        # -- in the list models, and add the variable
    #        # -----------------------------------------------------------------------------------------
    #        wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
    #        wmodel.update(dict(variable=variable)) # - add a variable to the dictionary with update
    #        #
    #        # /// -- Get the dataset and compute the annual cycle
    #        # -----------------------------------------------------------------------------------------
    #        dat = time_average( ds(**wmodel) )
    #        #
    #        min_values.append( cscalar(ccdo(dat,operator='fldmin')) )
    #        max_values.append( cscalar(ccdo(dat,operator='fldmax')) )
    #        #
    #    min_val = '%s' % float('%.3g' % min(min_values))
    #    max_val = '%s' % float('%.3g' % max(max_values))
    #    var.update(dict(min=min_val, max=max_val))
    #    #
    #    for model in Wmodels:
    #        #
    #        # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
    #        # -- in the list models, and add the variable
    #        # -----------------------------------------------------------------------------------------
    #        wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
    #        wmodel.update(dict(variable=variable)) # - add a variable to the dictionary with update
    #        #
    #        # /// -- Get the dataset and compute the annual cycle
    #        # -----------------------------------------------------------------------------------------
    #        dat = time_average( ds(**wmodel) )
    #        #        
    #        # /// -- Build the titles
    #        # -----------------------------------------------------------------------------------------
    #        title = build_plot_title(wmodel,None) # > returns the model name if project=='CMIP5'
    #        #                                         otherwise it returns the simulation name
    #        #                                         It returns the name of the reference if you provide
    #        #                                         a second argument ('dat1 - dat2')
    #        LeftString = variable
    #        RightString = build_period_str(wmodel)  # -> finds the right key for the period (period of clim_period)
    #        CenterString = ''
    #        #
    #        # -- Plot the raw variable
    #        # -----------------------------------------------------------------------------------------
    #        #plot_raw = plot(dat, title=title, gsnLeftString = LeftString, gsnRightString = RightString, gsnCenterString = CenterString,
    #        #                color='BlueWhiteOrangeRed', min=min_val, max=max_val, **p)
    #        plot_raw = plot_climato(var, dat, 'ANM',
    #                        color='BlueWhiteOrangeRed', )
    #        #
    #        # ==> -- Add the plot to the line
    #        # -----------------------------------------------------------------------------------------
    #        index += cell("",safe_mode_cfile_plot(plot_raw, safe_mode=safe_mode),
    #                      thumbnail=thumbN_size, hover=hover, **alternative_dir)
    #        #
    #    # ==> -- Close the line and the table for this section
    #    # -----------------------------------------------------------------------------------------
    #    index+=close_line() + close_table()
#





# ----------------------------------------------
# --                                             \
# --  Precipitation annual cycle                  \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- Refined annual cycle of precipitation to ease comparison of simulations and        -- #
# -- better understand evaluation metrics.                                              -- #
if do_annual_cycle_precip:
    #
    variable = 'pr'
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("Precipitation annual cycle", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    #
    # ==> -- Open the html line with the title
    # -----------------------------------------------------------------------------------------
    index += open_table()
    line_title = 'Seasonal'
    index+=start_line(line_title)
    #
    # ==> -- Apply the period_for_diag_manager (not actually needed here)
    # -----------------------------------------------------------------------------------------
    Wmodels = copy.deepcopy(models)
    #
    # -- Define plot parameters per variable -> better if in the params file
    # -----------------------------------------------------------------------------------------
    pp_annual_cycle_precip = plot_params('pr','bias')
    pp_annual_cycle_precip.update(dict(colors='-12 -10 -8 -6 -4 -2 -1 -0.5 0.5 1 2 4 6 8 10 12 ', contours=1)) 
    #
    # /// -- Get the reference and compute the annual cycle
    # -----------------------------------------------------------------------------------------
    ref_dict = variable2reference(variable)
    ref = annual_cycle( ds(**ref_dict) )
    #
    # -- Loop on the models
    # -----------------------------------------------------------------------------------------
    for model in Wmodels:
        #
        # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
        # -- in the list models, and add the variable
        # -----------------------------------------------------------------------------------------
        wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
        wmodel.update(dict(variable=variable)) # - add a variable to the dictionary with update
        #
        # ==> -- Apply frequency and period manager
        # -----------------------------------------------------------------------------------------
        frequency_manager_for_diag(wmodel, 'clim')
        get_period_manager(wmodel)
        #
        # /// -- Get the dataset and compute the annual cycle
        # -----------------------------------------------------------------------------------------
        dat = annual_cycle( ds(**wmodel) )
        #
        fig_lines = []
        options='pmLabelBarWidthF=0.065|pmLabelBarOrthogonalPosF=0.01|lbLabelFontHeightF=0.01|tmXBLabelFontHeightF=0.01|tmYLLabelFontHeightF=0.01'
        for m in months:
            clim_ref = llbox( clim_average(ref,m), **domain)
            clim_dat = llbox( regrid( clim_average(dat,m), clim_ref ), **domain)
            anom_ref = fsub(clim_ref, str(cMA(space_average(clim_ref))[0][0][0]))
            anom_dat = fsub(clim_dat, str(cMA(space_average(clim_dat))[0][0][0]))
            bias_map_m = minus(clim_dat, clim_ref)
            # -- metrics
            bias_m = cMA(space_average(bias_map_m))[0][0][0] * 86400.
            rms_m = cMA(ccdo( time_average(space_average( ccdo( minus(clim_dat, clim_ref), operator='sqr' ) )),
                              operator='sqrt'))[0][0][0] * 86400.
            num_cor_m = ccdo(multiply(anom_dat,anom_ref), operator='fldavg')
            denom_cor_m = fmul(ccdo(anom_dat,operator='fldstd'),ccdo(anom_ref,operator='fldstd'))
            cor_m = cMA( fdiv(num_cor_m, denom_cor_m))[0][0][0]
            s_bias_m = '%s' % float('%.3g' % bias_m)
            s_rms_m = '%s' % float('%.3g' % rms_m)
            s_cor_m = '%s' % float('%.3g' % cor_m)
            metrics = 'bias = '+s_bias_m+' ; rms = '+s_rms_m+' ; cor = '+s_cor_m
            plot_m = plot( bias_map_m, gsnCenterString = m, gsnRightString = metrics, gsnLeftString = build_period_str(wmodel),
                           options =  options, mpCenterLonF=200, **pp_annual_cycle_precip )
            fig_lines.append([plot_m])
    
        mp = cpage(fig_lines = fig_lines,
                   title=build_plot_title(wmodel,ref_dict),
                   gravity='NorthWest',
                   ybox=80, pt=30,
                   x=30, y=40,
                   font='Waree-Bold'
                   )
            
        # -----------------------------------------------------------------------------------------
        index += cell("",safe_mode_cfile_plot(mp, safe_mode=safe_mode),
                           thumbnail="300*600", hover=hover, **alternative_dir)
    #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
    index+=close_line() + close_table()




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

# -- End the index
index += trailer()

# -- Write the atlas html file
outfile=atlas_dir+"/"+index_name
print 'outfile = ',outfile
with open(outfile,"w") as filout : filout.write(index)
#
if atTGCC:
   # -- Ecriture du fichier html dans le repertoire sur scratch
   path_to_comparison_outdir_workdir_tgcc = atlas_dir.replace('scratch', 'work')
   if not os.path.isdir(path_to_comparison_outdir_workdir_tgcc):
      os.makedirs(path_to_comparison_outdir_workdir_tgcc)
   else:
      print 'rm -rf '+path_to_comparison_outdir_workdir_tgcc+'/*'
      os.system('rm -rf '+path_to_comparison_outdir_workdir_tgcc+'/*')
   cmd1 = 'cp -r '+atlas_dir+'* '+path_to_comparison_outdir_workdir_tgcc
   print cmd1
   os.system(cmd1)
   #
   # -- dods_cp du repertoire copie sur le work
   cmd12 = 'rm -rf '+path_to_comparison_on_web_server+'/'+component
   print cmd12
   os.system(cmd12)
   cmd2 = 'dods_cp '+path_to_comparison_outdir_workdir_tgcc+' '+path_to_comparison_on_web_server+'/'
   print cmd2
   os.system(cmd2)

print(' -- ')
print(' -- ')
print(' -- ')
print('Index available at : '+outfile.replace(path_to_cesmep_output_rootdir,root_url_to_cesmep_outputs))
if atTGCC:
   print("The atlas is ready as ", str.replace(index_name, atlas_dir, path_to_comparison_outdir_workdir_tgcc))
else:
   print("The atlas is ready as ", index_name)

# -----------------------------------------------------------------------------------
# --   End PART 3
# --
# -----------------------------------------------------------------------------------


# -- Systematically clean the cache
if routine_cache_cleaning:
   if not isinstance(routine_cache_cleaning,list): routine_cache_cleaning = [routine_cache_cleaning]
   for clean_args in routine_cache_cleaning:
       print 'clean_args = ',clean_args
       crm(**clean_args)

# -----------------------------------------------------------------------------------
# -- End of the atlas                                                                
# -----------------------------------------------------------------------------------

