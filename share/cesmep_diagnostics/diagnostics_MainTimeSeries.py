#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------ #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division
import inspect
from climaf.plot.varlongname import varlongname
# Note : the code sequences which are driven by a test like :
#        if ts_frequency in locals():
# are used when this code is executed by diagnostics_orchidee
# They extend the functionnalities of the original code
# (SS - jan 2025)


def ts_adapt_frequency(dat, from_freq, to_freq, data_name):
    #
    rep = None
    if to_freq != from_freq:
        if to_freq == 'yearly':
            if from_freq in ['monthly', 'daily' ]:
                rep = ccdo(dat, operator = 'yearmean')
        elif to_freq == 'monthly':
            if from_freq == 'daily' :
                rep = ccdo(dat, operator = 'monmean')
        elif to_freq == 'annual_cycle':
            if from_freq in [ 'monthly' , 'daily' ]:
                rep = annual_cycle(dat)
        else:
            raise ValueError( "Cannot process target frequency %s"%to_freq)
        #
        if rep is None:
            raise ValueError( "Cannot compute %s output with %s input for data %s"%\
                              to_freq, from_freq, data_name)
    else:
        rep = dat
    return rep

def ts_get_contfrac(spec):
    """ Returns a CliMAF dataset representing the continental fraction
    for the dataset provided as a dictionnary of attributes SPEC"""
        
    # TBD : test if data can be found
    contfrac = copy.deepcopy(spec)
    if contfrac['project'] in ['CMIP6', 'CMIP5' ]:
        contfrac['table'] = 'Lmon'
        contfrac['variable'] = 'sftlf'
    elif contfrac['project'] in ['IGCM_OUT' ]:
        contfrac['variable'] = 'CONTFRAC'
        contfrac['DIR'] = 'SBG'
    else:
        raise ValueError("Cannot find a continental fraction for project %s"%contfrac['project'])
    return(ds(**contfrac))

if do_main_time_series:
    print('-- time_series_specs =         --')
    print('-> ', time_series_specs)
    print('--                             --')
    #
    # - Init html index
    # -----------------------------------------------------------------------------------
    if atlas_head_title is None :
        atlas_head_title = "Main time Series"
    # We possibly are just complementing an index
    if "index" not in locals() or index is None :
        index = header(atlas_head_title, style_file=style_file)
        index += section("Main Time Series", level=4)
    #
    # -- Add the references which are simulations
    if type(reference) is list:
        refs = reference
    else:
        refs = [reference]
    wmodels = [ref for ref in refs if ref != 'default'] + models
    #
    # -- Period Manager
    if not use_available_period_set:
        WWmodels_ts = period_for_diag_manager(wmodels, diag='TS')
        WWmodels_clim = period_for_diag_manager(wmodels, diag='clim')
    else:
        WWmodels_ts = copy.deepcopy(Wmodels_ts)
        WWmodels_clim = copy.deepcopy(Wmodels_clim)
    #
    WTSmodels = copy.deepcopy(WWmodels_ts)
    WCLIMmodels = copy.deepcopy(WWmodels_clim)

    #print('WTSmodels=',WTSmodels)

    #
    # -- Loop on the time series (a.k.a. variable) specified in the params file
    # ------------------------------------------------------------------------------------
    for time_series in time_series_specs:
        
        # ==> -- Open the html line with the title
        # ---------------------------------------------------------------------------------
        index += open_table()
        line_title = time_series['variable']
        index += start_line(line_title)
        #
        okwargs = time_series.get('operation_loop_kwargs', {})
        if type(okwargs) is not list : okwargs = [ okwargs ]

        # Iterate over some parameter (e.g. regions)
        for okwarg in okwargs :
            if "ts_filename_func" in locals() :
                ts_region = okwarg.get('region','g')
                ts_region_name = okwarg.get('region_name','')
            print("processing time_series with :",okwarg, time_series)
            ens_ts_dict = dict()
            names_ens = []
            #
            highlight_period = []
            #
            # -- Initialize WWmodels_clim and WWmodels_ts
            WWmodels_clim = copy.deepcopy(WCLIMmodels)
            WWmodels_ts = copy.deepcopy(WTSmodels)
    
            # -- Project specs: transfer project-specific arguments
            # -- from time_series to WWModels if applicable
            specs = time_series.get('project_specs',None)
            if specs is not None:
                for wmodels in [ WWmodels_clim, WWmodels_ts ]:
                    for dataset_dict in wmodels:
                        if dataset_dict['project'] in specs :
                            dataset_dict.update(specs[dataset_dict['project']])

            # -- Also pass table and grid values
            for attribute in [ 'table', 'grid']:
                if attribute in time_series:
                    for wmodels in [ WWmodels_clim, WWmodels_ts ]:
                        if wmodels is not None:
                            for dataset_dict in wmodels:
                                dataset_dict[attribute] = time_series[attribute]
    
            #
            if time_series.get('highlight_period', None) == 'clim_period':
                for dataset_dict in WWmodels_clim:
                    # -- Apply period manager if needed
                    dataset_dict.update(variable=time_series['variable'])
                    dataset_dict = get_period_manager(dataset_dict, diag='clim')
                    highlight_period.append(build_period_str(dataset_dict))
    
            for dataset_dict in WWmodels_ts:
                #
                wdataset_dict = dataset_dict.copy()
                wdataset_dict.update(variable=time_series['variable'])
    
                # -- Apply period manager if needed
                wdataset_dict = get_period_manager(wdataset_dict, diag='ts')
                #
                # -- Get the dataset
                #print('wdataset_dict in time_series = ', wdataset_dict)
                dat = ds(**wdataset_dict)
                #
                # -- select a domain if the user provided one
                if 'domain' in time_series:
                    lonmin = str(time_series['domain']['lonmin'])
                    lonmax = str(time_series['domain']['lonmax'])
                    latmin = str(time_series['domain']['latmin'])
                    latmax = str(time_series['domain']['latmax'])
                    # -- We regrid the dataset for ocean variables
                    if time_series['variable'] in ocean_variables:
                        dat = regridn(dat, cdogrid='r360x180')
                    #
                    dat = llbox(dat, lonmin=lonmin, lonmax=lonmax,
                                latmin=latmin, latmax=latmax)
                #
                # -- Build a dataset name
                mem_name = build_plot_title(wdataset_dict)
                names_ens.append(mem_name)
                #
                # Change data frequency if needed
                if "frequency_for_ts" in locals():
                    dat = ts_adapt_frequency(dat, wdataset_dict['frequency'],
                                             frequency_for_ts , mem_name)
                #
                # Get continental fraction data if needed, and add it in args
                operation = time_series['operation']
                if 'contfrac' in inspect.getargspec(operation)[0]:
                    contfrac = time_series.get('contfrac',None)
                    if contfrac == 'nc':
                        okwarg['contfrac'] = ts_get_contfrac(wdataset_dict)
                        cfile(okwarg['contfrac'])
                    else:
                        okwarg['contfrac'] = contfrac
                #
                # -- Apply the operation
                ts_dat = operation( dat, **time_series.get('operation_kwargs',{}),
                                    **okwarg)
                #
                # -- Add to the ensemble for plot
                #print("Dat_fic=",cfile(ts_dat))
                ens_ts_dict.update({mem_name: ts_dat})
                #
            #
            # -- Finalize the CliMAF ensemble
            # -> Test if we have duplicates in names_ens => will produce problems in the ensemble
            #    where all the member need to have unique names
            if len(set(names_ens)) < len(names_ens):
                raise Climaf_Error(
                    "All the members/simulations from datasets_setup.py need to have unique names, "
                    "which is not the case here = %s ; use customname to provide names     to your simulations "
                    "(use another key, like customname=${experiment}, customname=${model}_${realization}, "
                    "or provide a name, like customname='My simulation' ; "
                    "see https://github.com/jservonnat/C-ESM-EP/wiki/Building-my-comparison-part-1:"
                    "-datasets_setup.py-and-atlas-subdirectories#4-the-customname-control-the-name-in-"
                    "the-plot)" % repr(names_ens))
            ens_ts = cens(ens_ts_dict, order=names_ens)
            #
            # -- Build arguments dict for the plot function
            p = time_series.copy()
            # Remove every attribute which is not a ts_plot parameter
            #for attribute in ['variable','operation','operation_kwargs',
            #          'operation_loop_kwargs','domain','table',
            #          'grid', 'frequency', 'project_specs',
            #          'contfrac', 'regions']:
            for attribute in list(p.keys()):
                if "${%s}"%attribute not in cscripts["ensemble_ts_plot"].command:
                    p.pop(attribute,None)
            if highlight_period:
                p.update(highlight_period=highlight_period)
            else:
                pass
                #print('==> No highlight period provided => ', highlight_period)
            # -- Colors
            p.update(dict(colors=colors_manager(WWmodels_ts, cesmep_python_colors)))
            # -- Title
            if "ts_region_name" in locals():
                p.update(title = ts_region_name)
            #
            # -- Do the plot
            #print('ens_ts = ', ens_ts)
            #print('p = ', p)
            if "ylabel" not in p:
                p['ylabel'] = time_series['variable'] + ' ' + varlongname(time_series['variable'])
            myplot =  ts_plot(ens_ts, **p)
            cdrop(myplot)
            #
            # ==> -- Add the plot to the plots line 
            # ----------------------------------------------------------------------------
            if "ts_thumbnail_size" in locals():
                ts_thumbN_size = ts_thumbnail_size
            else:
                fig_size = time_series.get('fig_size','15*5')
                fig_sizes = str.split(fig_size, '*')
                ts_thumbN_size = str(int(fig_sizes[0])*75) +\
                    '*' + str(int(fig_sizes[1])*75)
                print("ts_thumbN_size from fig_size",ts_thumbN_size)

            cell_args = alternative_dir.copy()
            if "ts_filename_func" in locals() and 'ts_region_name' in locals():
                cell_args.update(target_filename =
                    ts_filename_func(ts_region, time_series['variable'], frequency_for_ts))
            index += cell("", safe_mode_cfile_plot(myplot, safe_mode=safe_mode),
                          thumbnail=ts_thumbN_size, hover=hover, **cell_args)
            #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
    index += close_line() + close_table()

# -----------------------------------------------------------------------------------
# --   End
# --
# -----------------------------------------------------------------------------------


