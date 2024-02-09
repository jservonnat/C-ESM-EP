#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------ #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division

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
# --  Main Time series                            \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


def convert_list_to_string(dum, separator1=',', separator2='|'):
    string = ''
    if isinstance(dum, list):
        for elt in dum:
            concat_elt = elt
            if isinstance(elt, list):
                substring = ''
                for elt2 in elt:
                    if substring == '':
                        substring = str(elt2)
                    else:
                        substring += separator1+str(elt2)
                concat_elt = substring
                if string == '':
                    string = concat_elt
                else:
                    string += separator2+concat_elt
            else:
                if string == '':
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
    print('---------------------------------')
    print('-- Processing Main Time Series --')
    print('-- do_main_time_series = True  --')
    print('-- time_series_specs =         --')
    print('-> ', time_series_specs)
    print('--                             --')
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("Main Time Series", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    thumbN_size = thumbnail_size
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

    #
    # -- Loop on the time series specified in the params file
    # -----------------------------------------------------------------------------------------
    for time_series in time_series_specs:
        # ==> -- Open the html line with the title
        # -----------------------------------------------------------------------------------------
        index += open_table()
        line_title = ''
        index += start_line(line_title)
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
                    dataset_dict.update(
                        time_series['project_specs'][dataset_dict['project']])

            for dataset_dict in WWmodels_ts:
                if dataset_dict['project'] in time_series['project_specs']:
                    dataset_dict.update(
                        time_series['project_specs'][dataset_dict['project']])
            time_series.pop('project_specs')
        if 'table' in time_series:
            for dataset_dict in WWmodels_clim:
                dataset_dict['table'] = time_series['table']
            for dataset_dict in WWmodels_ts:
                dataset_dict['table'] = time_series['table']
            time_series.pop('table')
        if 'grid' in time_series:
            for dataset_dict in WWmodels_clim:
                dataset_dict['grid'] = time_series['grid']
            for dataset_dict in WWmodels_ts:
                dataset_dict['grid'] = time_series['grid']
            time_series.pop('grid')

        #
        if 'highlight_period' in time_series:
            if time_series['highlight_period'] == 'clim_period':
                for dataset_dict in WWmodels_clim:
                    print('dataset_dict in time_series = ', dataset_dict)
                    # -- Apply period manager if needed
                    dataset_dict.update(dict(variable=time_series['variable']))
                    dataset_dict = get_period_manager(
                        dataset_dict, diag='clim')
                    highlight_period.append(build_period_str(dataset_dict))

        for dataset_dict in WWmodels_ts:
            #
            wdataset_dict = dataset_dict.copy()
            wdataset_dict.update(dict(variable=time_series['variable']))

            # -- Apply period manager if needed
            wdataset_dict = get_period_manager(wdataset_dict, diag='ts')
            #
            # -- Get the dataset
            print('wdataset_dict in time_series = ', wdataset_dict)
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
                dat = llbox(dat, lonmin=lonmin, lonmax=lonmax,
                            latmin=latmin, latmax=latmax)
            #
            #
            # -- Apply the operation
            if 'operation_kwargs' in time_series:
                ts_dat = time_series['operation'](
                    dat, **time_series['operation_kwargs'])
            else:
                ts_dat = time_series['operation'](dat)
            #
            # -- Get the name
            mem_name = build_plot_title(wdataset_dict)
            names_ens.append(mem_name)
            #
            # -- Add to the ensemble for plot
            ens_ts_dict.update({mem_name: ts_dat})
            #
        #
        # -- Finalize the CliMAF ensemble
        # -> Test if we have duplicates in names_ens => will produce problems in the ensemble
        #    where all the member need to have unique names
        if len(set(names_ens)) < len(names_ens):
            raise Climaf_Error("All the members/simulations from datasets_setup.py need to have unique names, "
                               "which is not the case here = %s ; use customname to provide names to your simulations "
                               "(use another key, like customname=${experiment}, customname=${model}_${realization}, "
                               "or provide a name, like customname='My simulation' ; "
                               "see https://github.com/jservonnat/C-ESM-EP/wiki/Building-my-comparison-part-1:"
                               "-datasets_setup.py-and-atlas-subdirectories#4-the-customname-control-the-name-in-"
                               "the-plot)" % repr(names_ens))
        ens_ts = cens(ens_ts_dict, order=names_ens)
        #
        # -- Do the plot
        p = time_series.copy()
        p.pop('variable')
        if 'operation' in p:
            p.pop('operation')
        if 'operation_kwargs' in p:
            p.pop('operation_kwargs')
        if 'domain' in p:
            p.pop('domain')
        if highlight_period:
            p.update(dict(highlight_period=highlight_period))
        else:
            print('==> No highlight period provided => ', highlight_period)
        # -- Colors
        p.update(dict(colors=colors_manager(WWmodels_ts, cesmep_python_colors)))
        print('ens_ts = ', ens_ts)
        print('p = ', p)
        myplot = ts_plot(ens_ts, **p)
        cdrop(myplot)
        #
        # ==> -- Add the plot to the line
        # -----------------------------------------------------------------------------------------
        if 'fig_size' in time_series:
            fig_size = time_series['fig_size']
        else:
            fig_size = '15*5'
        thumbnail_main_ts = str(
            int(str.split(fig_size, '*')[0])*75)+'*'+str(int(str.split(fig_size, '*')[1])*75)
        index += cell("", safe_mode_cfile_plot(myplot, safe_mode=safe_mode),
                      thumbnail=thumbnail_main_ts, hover=hover, **alternative_dir)
        #
    # ==> -- Close the line and the table for this section
    # -----------------------------------------------------------------------------------------
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
