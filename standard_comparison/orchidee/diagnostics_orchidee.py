#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Code for

from custom_plot_params import dict_plot_params as custom_plot_params
from orchidee_variables_and_functions import simu_name, mapper_map_filename, mapper_ts_filename
    
# Build a dict of map specification by combining 3 sources
def build_map_specs(variables_setup, common_plot_params, special_project_specs):
    variables_per_category = dict()
    for category in variables_setup.keys() :
        variables_per_category[category] = []
        for variable in variables_setup[category]['variables']:
            var_dict = {'variable' : variable}
            pspecs = copy.deepcopy(variables_setup[category].get('specs',None))
            var_dict.update({'project_specs' : pspecs})
            if variable in special_project_specs :
                var_dict['project_specs'].update(special_project_specs[variable])
            var_dict.update(common_plot_params)
            if 'PFT' in variable:
                derive_var_PFT(variable)
            variables_per_category[category].append(var_dict)
    return variables_per_category


# Build the list of time series specifications for one category by combining 4 sources
def build_time_series_specs(category, variables_setup, special_project_specs,
                            time_series_setup, common_ts_plot_params,
                            regions, regions_file) :

    # From NetCDF 'regions_file', returns the 'reg_label' value for
    # region which 'reg_id' is 'region', assuming both share coordinate 'reg'
    def ts_get_region_label(region, regions_file):
        with xr.open_dataset(regions_file) as rf:
            for reg in rf.reg.values :
                if rf.reg_id[reg] == region:
                    return reg , str(rf.reg_label[reg].to_numpy())
            raise ValueError("Cannot find region %s in %s"%(region,regions_file))


    specs = list()
    for variable in variables_setup[category]['variables']:
        spec = dict(variable=variable,
                    project_specs=copy.deepcopy(
                        variables_setup[category].get('specs',None)))
        if variable in special_project_specs:
            spec['project_specs'].update(special_project_specs[variable])
        for common_key in common_ts_plot_params:
            if common_key not in spec:
                spec.update({common_key:common_ts_plot_params[common_key]})
        spec.update(time_series_setup.get('default',{}))
        spec.update(time_series_setup.get(variable,{}))
        regions = time_series_setup.get("regions",regions)
        if regions_file and regions and (len(regions) > 0) :
            # Create a list of args dict for the space integration function
            spec['operation_loop_kwargs'] = list()
            for region in regions:
                region_number, region_name = ts_get_region_label(region, regions_file)
                spec['operation_loop_kwargs'].append({
                    'region' : region, 'region_name' : region_name,
                    'region_number' : region_number, 'regions_file' : regions_file ,
                    'contfrac' : spec.get('contfrac', None) })
        specs.append(spec)
    return specs

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

if atlas_head_title is None:
    atlas_head_title = 'Mapper - maps part'

# -- Period Manager
if not use_available_period_set:
    Wmodels = period_for_diag_manager(models, diag = diag_name)
else:
    Wmodels = copy.deepcopy(Wmodels_clim)

# -- Add table. To be re-scrutinized
#for model in Wmodels:
#    model.update(dict(table='Lmon'))

# -- This diag is yet validated only for CMIP6 and IGCM_OUT !
for model in Wmodels.copy():
    if 'IGCM' not in model['project'] and model['project'] not in 'CMIP6':
        print('removing Model %s, for which project (%s) this diag has not been validated yet'%(model,model['project']))
        Wmodels.remove(model)

print('Wmodels=',Wmodels)


# -- Init html index
index = header(atlas_head_title, style_file=style_file)

index += section('Maps', level=1)

# Common args for climato_* functions
args_rest = dict(domain=domain,
               add_product_in_title=add_product_in_title,
               custom_plot_params=custom_plot_params, shade_missing=True,
               safe_mode=safe_mode, alternative_dir=alternative_dir,
               custom_obs_dict=custom_obs_dict, thumbnail_size=thumbnail_size,
               filename_func=mapper_map_filename)

# -- Create dicts of variables, listed by category, applying 
# -- all spec sources (setup, common_plot_params, special_projet_specs, ...)

map_specs = build_map_specs(variables_setup, common_plot_params,
                            special_project_specs)

# -- Create map plots 
# For each variable category, generate a section
# For each variable, generate a subsection

for category in map_specs.keys() :
    index += section(category, level=2)
    #
    for season in seasons:
        if case_toggles['maps']:
            title1 = category + ' - Climatologies'
            print("re-specs for ra:",map_specs[category])
            index += section_climato_2D_maps(
                copy.deepcopy(Wmodels), None, proj, season,
                copy.deepcopy(map_specs[category]), title1, **args_rest)
        #
        if case_toggles['anomalies']:
            title1 = category + ' - Anomalies (i.e. vs obs)'
            #
            # Create a specs list for those variables which have a reference
            vars_with_ref = copy.deepcopy(map_specs[category])
            if reference == 'default' or 'default' in reference:
                for one_var in map_specs[category]:
                    try:
                        ref=variable2reference(one_var['variable'],
                                               my_obs=custom_obs_dict)
                        cfile(ds(**ref))
                    except:
                        print('No obs for ', one_var['variable'])
                        vars_with_ref.remove(one_var)
            #
            index += section_2D_maps(
                copy.deepcopy(Wmodels), reference, proj, season,
                vars_with_ref, title1, **args_rest)
        #
        if case_toggles['diff']:
            title1 = category + ' - Diff vs simulation'
            wms = copy.deepcopy(Wmodels)
            index += section_2D_maps(
                wms[1:len(wms)], wms[0], proj, season,
                copy.deepcopy(map_specs[category]), title1, **args_rest)



if case_toggles['time_series']:
    #
    index += section('Time series', level=1)

    # Find a diagnostic code file for Time Series, 
    # (first co-located with this code, then in shared/cesmep_diagnostics)
    here = os.path.split(diagnostics_file)[0]
    ts_diag_file = here + "/diagnostics_MainTimeSeries.py"
    if not os.path.isfile(ts_diag_file):
        ts_diag_file = here + \
            "/../../share/cesmep_diagnostics/diagnostics_MainTimeSeries.py"

    # Set some variables usable by the time series code
    do_main_time_series = True
    ts_filename_func = mapper_ts_filename
    
    for category in variables_setup.keys():
        index += section(category, level=2)
        time_series_specs = build_time_series_specs(
            category, variables_setup, special_project_specs,
            time_series_setup, common_ts_plot_params,
            ts_regions, ts_regions_file)
        print('time_series_specs=',time_series_specs)
        
        for frequency_for_ts in ts_frequencies:
            index += section("Time Series - %s - %s"%(category,frequency_for_ts), level=4)
            print("Now executing TS diag for category %s and frequency %s with code %s"\
                  %(category,frequency_for_ts,ts_diag_file))
            exec(open(ts_diag_file).read())
