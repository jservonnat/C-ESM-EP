# ------------------------------------------------------------------------------------------------------ \
# --                                                                                                    - \
# --                                                                                                     - \
# --      Scientific diagnostics for the                                                                  - \
# --          CliMAF Earth System Model Evaluation Platform                                               - |
# --                                                                                                      - |
# --      diagnostics_${component}.py                                                                     - |
# --        ==> add html code to 'index' (initialized with 'header')                                      - |
# --            using the CliMAF html toolbox (start_line, cell, close_table... )                         - |
# --            to create your own atlas page                                                             - | 
# --                                                                                                      - |
# --      Developed within the ANR Convergence Project                                                    - |
# --      CNRM GAME, IPSL, CERFACS                                                                        - |
# --      Contributions from CNRM, LMD, LSCE, NEMO Group, ORCHIDEE team.                                  - |
# --      Based on CliMAF: WP5 ANR Convergence, S. Senesi (CNRM) and J. Servonnat (LSCE - IPSL)           - |
# --                                                                                                      - |
# --      J. Servonnat, S. Senesi, L. Vignon, MP. Moine, O. Marti, E. Sanchez, F. Hourdin,                - |
# --      I. Musat, M. Chevallier, J. Mignot, M. Van Coppenolle, J. Deshayes, R. Msadek,                  - |
# --      P. Peylin, N. Vuichard, J. Ghattas, F. Maignan, A. Ducharne, P. Cadule,                         - |
# --      P. Brockmann, C. Rousset, J.Y. Perterschmitt                                                    - |
# --                                                                                                      - |
# --      Contact: jerome.servonnat@lsce.ipsl.fr                                                          - |
# --                                                                                                      - |
# --  See the documentation at: https://github.com/jservonnat/C-ESM-EP/wiki                               - |
# --                                                                                                      - |
# --                                                                                                      - /
# --  Note: you can actually use an empty datasets_setup                                                 - /
# --  and an empty params_${component}.py, and set everything from here                                 - /
# --                                                                                                   - /
# --                                                                                                  - /
# ---------------------------------------------------------------------------------------------------- /


# ----------------------------------------------
# --                                             \
# --  Model Tuning: SST 50S/50N average           \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# -- Head title of the atlas
# ---------------------------------------------------------------------------- >
atlas_head_title = "Metrics for model tuning"


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# ---------------------------------------------------------------------------------------- #
# -- Compute the SST biases over 50S/50N for the reference models and the test datasets -- #

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
    # -- Get period manager
    wdataset_dict = get_period_manager(wdataset_dict, diag='clim')
    # -- Build customname and update dictionnary => we need customname anyway, for references too
    if 'customname' in wdataset_dict:
        customname = str.replace(replace_keywords_with_values(wdataset_dict, wdataset_dict['customname']),' ','_')
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
        if not rawvalue=='NA':
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


# -----------------------------------------------------------------------------------
# --   End
# --
# -----------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------ \
# --                                                                                                    - \
# --                                                                                                     - \
# -- main_C-ESM-EP.py will provide you with:                                                              - |
# --   - the list 'models' defined in datasets_setup.py, as well as 'reference'                           - |
# --     if use_available_period_set == True, it means that you also have Wmodels_clim and Wmodels_ts     - |
# --     that correspond to 'models' with periods for climatologies and time series (respectively)        - |
# --     that have already been found (if you used arguments like 'last_10Y', 'first_30Y', 'full' or '*') - |
# --   - alternative_dir: to be used as an argument to cell(..., altdir=alternative_dir)                  - |
# --   - the parameters from params_${component}.py (safe_mode,                                           - |
# --   - the cesmep modules in share/cesmep_modules                                                       - |
# --   - the default values from share/default/default_atlas_settings.py                                  - |
# --                                                                                                      - /
# -- Note: you can actually use an empty datasets_setup                                                  - /
# -- and an empty params_${component}.py, and set everything from here                                  - /
# --                                                                                                   - /
# --                                                                                                  - /
# ---------------------------------------------------------------------------------------------------- /


