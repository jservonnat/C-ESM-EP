#!/usr/bin/env python
# -*- coding: utf-8 -*-

# S.Sénési - 2025

# Code for creating an atlas showing maps and time series,
# with an 'interactive' html page (i.e. allowing selection of what is
# displayed).

# Variables are grouped in user-defined categories

# Maps come in three flavors : plain climatologies, anomalies, and
# differences vs. first simulation.

# Time series are spatially integrated over a choice of basins
# described by an auxiliary file

# Best doc yet is the example of use by component 'orchidee'. See
# params_orchidee.py

# -- This diag is yet validated only for IGCM_OUT !

from custom_plot_params import dict_plot_params as custom_plot_params
from CM_atlas import mapper
from reference.reference import reference_has_data
    
# Build a dict of map specification by combining 5 sources
def build_map_specs(variables_setup, variables_specific, common_plot_params,
                    plots_setup, special_project_specs):
    variables_per_category = dict()
    for category in variables_setup.keys() :
        variables_per_category[category] = []
        for variable in variables_setup[category]['variables']:
            var_dict = {'variable' : variable}
            pspecs = copy.deepcopy(variables_setup[category].get('specs',{}))
            var_dict.update({'project_specs' : pspecs})
            if variable in special_project_specs :
                var_dict['project_specs'].update(special_project_specs[variable])
            var_dict.update(common_plot_params)
            var_dict.update(variables_specifics.get(variable,{}))
            var_dict.update(plots_setup.get(variable,{}))
            if 'PFT' in variable:
                derive_var_PFT(variable)
            variables_per_category[category].append(var_dict)
    return variables_per_category


# Build the list of time series specifications for one category by combining 5 sources
def build_time_series_specs(category, variables_setup, variables_specifics,
                            special_project_specs, time_series_setup,
                            common_ts_plot_params, regions, regions_file) :

    # From NetCDF 'regions_file', returns the pair, 'reg_number','reg_label' value for
    # region which 'reg_id' is 'region', assuming they share coordinate 'reg'
    def ts_get_region_label(region, regions_file):
        if region == 'G' :
            return(None, "Globe")
        with xr.open_dataset(regions_file) as rf:
            for reg in rf.reg.values :
                if rf.reg_id[reg] == region:
                    return reg , str(rf.reg_label[reg].to_numpy())
            raise ValueError("Cannot find region %s in %s"%(region,regions_file))


    specs = list()
    for variable in variables_setup[category]['variables']:
        spec = dict(variable=variable,
                    project_specs=copy.deepcopy(
                        variables_setup[category].get('specs',{})))
        if variable in special_project_specs:
            spec['project_specs'].update(special_project_specs[variable])
        for common_key in common_ts_plot_params:
            if common_key not in spec:
                spec.update({common_key:common_ts_plot_params[common_key]})
        spec.update(variables_specifics.get(variable,{}))
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
    atlas_head_title = 'Maps and TS'
# When driven by libIGCM, an additional title may be provided by config.card
if AtlasTitle != "NONE":
    atlas_head_title += " - " + AtlasTitle
    

# -- Period Manager
if not use_available_period_set:
    Wmodels = period_for_diag_manager(models, diag = diag_name)
else:
    Wmodels = copy.deepcopy(Wmodels_clim)

if ts_regions is None or ts_regions == []:
    ts_regions=["G"]
    
if interactive_selection:
    # Activate relevant filename scheme 
    map_filename_func = mapper.mapper_map_filename
    ts_filename_func = mapper.mapper_ts_filename
    # Build html page
    mapper_page = mapper.build_mapper_page(models, variables_setup, \
                    case_toggles, seasons, ts_frequencies, ts_regions, \
                    ts_regions_file,  custom_obs_dict, variables_specifics,\
                    atlas_head_title, references)

# -- Add table. To be re-scrutinized
#for model in Wmodels:
#    model.update(dict(table='Lmon'))

# -- This diag is yet validated only for IGCM_OUT !
for model in Wmodels.copy():
    if 'IGCM' not in model['project'] :
        print('removing Model %s, for which project (%s) this diag has not been validated yet'%(model,model['project']))
        Wmodels.remove(model)

# -- Init html index
index = header(atlas_head_title, style_file=style_file)

index += section('Maps', level=1)

# Common args for all climato_* functions calls further below
args_rest = dict(domain=domain,
                 add_product_in_title=add_product_in_title,
                 custom_plot_params=custom_plot_params, shade_missing=True,
                 safe_mode=safe_mode, alternative_dir=alternative_dir,
                 custom_obs_dict=custom_obs_dict, thumbnail_size=thumbnail_size,
                 filename_func=map_filename_func)

# -- Create dicts of variables, listed by category, applying 
# -- all spec sources (setup, common_plot_params, special_projet_specs, ...)

map_specs = build_map_specs(variables_setup, variables_specifics, common_plot_params,
                            plots_setup, special_project_specs)

# -- Create map plots 
# For each variable category, generate a section
# For each variable, generate a subsection

for category in map_specs.keys() :
    index += section(category, level=2)
    #
    for season in seasons:
        if case_toggles.get('maps',False):
            title1 = category + ' - Climatologies'
            index += section_climato_2D_maps(
                copy.deepcopy(Wmodels), None, proj, season,
                copy.deepcopy(map_specs[category]), title1, **args_rest)
        #
        if case_toggles.get('anomalies',False):
            title1 = category + ' - Anomalies (i.e. vs obs and/or other reference)'
            # Create a specs list for all variables but the one with
            # a default reference that is missing
            vars_with_ref = []
            for each_var in map_specs[category]:
                if reference == 'default' or 'default' in reference:
                    if reference_has_data(each_var, custom_obs_dict):
                        vars_with_ref.append(copy.deepcopy(each_var))
                else:
                    vars_with_ref.append(copy.deepcopy(each_var))
            index += section_2D_maps(
                copy.deepcopy(Wmodels), reference, proj, season,
                vars_with_ref, title1, **args_rest)
        #
        if case_toggles.get('diffs',False) and len(Wmodels) > 1:
            title1 = category + ' - Diff vs simulation'
            wms = copy.deepcopy(Wmodels)
            index += section_2D_maps(
                wms[1:len(wms)], wms[0], proj, season,
                copy.deepcopy(map_specs[category]), title1, **args_rest)



if case_toggles.get('time_series',False):
    #
    index += section('Time series', level=1)

    # Find a diagnostic code file for Time Series, 
    # (first locally, next co-located with this code, then
    # in share/cesmep_diagnostics)
    ts_diag_file = None
    here = os.path.split(diagnostics_file)[0]
    for loc in [ "./", here, main_cesmep_path+"/share/cesmep_diagnostics"]:
        fic = loc + "/diagnostics_MainTimeSeries.py"
        if os.path.isfile(fic):
            ts_diag_file = fic
            break
    if ts_diag_file is None:
        print("No ts_diag_file found")
        exit(1)
    print("Using TS diag with code at: %s" % ts_diag_file)
        
    do_main_time_series = True
    
    for category in variables_setup.keys():
        index += section(category, level=2)
        time_series_specs = build_time_series_specs(
            category, variables_setup, variables_specifics,
            special_project_specs, time_series_setup, common_ts_plot_params,
            ts_regions, ts_regions_file)
        #print('time_series_specs=',time_series_specs)
        
        for frequency_for_ts in ts_frequencies:
            index += section("Time Series - %s - %s"%(category,frequency_for_ts),
                             level=4)
            exec(open(ts_diag_file).read())

