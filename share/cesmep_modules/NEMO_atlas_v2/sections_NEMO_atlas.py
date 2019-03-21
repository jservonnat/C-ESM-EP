from plot_NEMO_CERFACS import *
from plot_NEMO_atlas import *
from CM_atlas import *


def section_zonalmean_slices(models=[],reference='default',zonmean_slices_variables=[],zonmean_slices_basins=[],zonmean_slices_seas=[],
                             custom_plot_params=dict(), apply_period_manager=False, custom_obs_dict=dict(),
                             safe_mode=True, y='lin', do_cfile=True,
                             thumbsize_zonalmean='400*300', hover=False, alternative_dir=dict(), do_parallel=False):
    #
    # -- For parallel execution of the plots -> collect the CRS of all the plots in a list plots_crs
    if do_parallel:
       do_cfile=False
       plots_crs = []
    else:
       index=section("Zonal Means Sections per ocean basin --> Model regridded on reference (before computing the zonal mean)",level=4)
       do_cfile=True
    #
    # Loop over variables
    for variable in zonmean_slices_variables:
        # Loop over seasons
        for season in zonmean_slices_seas:
            if do_cfile:
                index+=open_table()+open_line(variable+"-"+season)+close_line()+close_table()
            for basin in zonmean_slices_basins:
                ## -- Model Grid
                if do_cfile:
                   index+=start_line(title_region(basin)+' '+varlongname(variable)+' ('+variable+')')
                if reference=='default':
                   ref = variable2reference(variable, my_obs=custom_obs_dict)
                else:
                   ref = reference.copy()
                basin_zonmean_modelgrid = zonal_mean_slice(ref, variable, basin=basin, season=season,
                                                ref=None, safe_mode=safe_mode, do_cfile=do_cfile, y=y, add_product_in_title=None,
                                                custom_plot_params=custom_plot_params, method='regrid_model_on_ref',
                                                apply_period_manager=apply_period_manager)
                if not do_cfile:
                   plots_crs.append(basin_zonmean_modelgrid)
                else:
                   index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
                for model in models:
                    basin_zonmean_modelgrid = zonal_mean_slice(model, variable, basin=basin, season=season,
                                                ref=ref, safe_mode=safe_mode, do_cfile=do_cfile, y=y, add_product_in_title=None,
                                                custom_plot_params=custom_plot_params, method='regrid_model_on_ref',
                                                apply_period_manager=apply_period_manager)
                    if not do_cfile:
                       plots_crs.append(basin_zonmean_modelgrid)
                    else:
                       index+=cell("", basin_zonmean_modelgrid, thumbnail=thumbsize_zonalmean, hover=hover, **alternative_dir)
                if do_cfile:
                   index+=close_line()+close_table()

    #
    if do_cfile:
       return index
    else:
       return plots_crs




