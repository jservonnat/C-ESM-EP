#%% AUXILIARY FUNCTIONS
def preprocess_hydro(ds, var_name, RIVER):    
    """
    It makes ORCv2 and v4 variable names compatible, extracts the data from station locations, 
    computes the climatological monthly mean, and concats everything into a single file.
    """
    
    if var_name == "hydrographs":
        if var_name in ds.data_vars:
            ds = ds[[var_name]]
    
            lat, lon = "lat", "lon"
                    
        elif 'routing_hydrographs_r' in ds.data_vars:        
            ds = ds[['routing_hydrographs_r']]
            ds = ds.rename({'routing_hydrographs_r': var_name})
            
            lat, lon = "lat2", "lon2"
        else:
            raise ValueError("Neither 'hydrographs' nor 'routing_hydrographs_r' found in dataset")    
    else:
        raise ValueError(f"preprocess_hydro does not currently support {var_name} variable")
        
    points = [ds.sel(lat=meta[lat], lon=meta[lon], method="nearest") for meta in RIVER]        
    sub = xr.concat(points, dim="location")

    ## DATA CAN START ON 0000-01-01: we use "decode_times=False" in open_mfdataset to fix this manually
    units = sub['time_counter'].attrs["units"]
    calendar = sub['time_counter'].attrs.get("calendar", "standard")
    
    sub['time_counter'] = xr.DataArray(
        [cftime.num2date(t, units, calendar, has_year_zero=True) for t in sub['time_counter'].values],
        dims='time_counter'
    )

    return sub.groupby("time_counter.month").mean("time_counter", skipna=True)
 
def lighten_color(color, amount=0.5):
    c = to_rgb(color)
    white = (1.0, 1.0, 1.0)
    return tuple((1 - amount) * comp + amount * white[i] for i, comp in enumerate(c))

def map_colorPalette():
    pastel_colors = [
        "white", 
        "#d5a6bd",      # 1- orchid (pink-purple)
        "#b0d4e6",      # 2- dusty blue 
        "#f4cccc",      # 3- blush (soft red)
        "#aec6cf",      # 4- pastel blue
        "#d7ecb5",      # 5- lime wash
        "#cbaacb",      # 6- pastel purple
        "#b4ddb4",      # 7- sage green
        "#ffb7ce",      # 8- pastel pink
        "#d0e0e3",      # 9- soft aqua
        "#c2dfff",      # 10- light periwinkle
        "#e9aeb0",      # 11- soft rose     
        "#b6e2d3",      # 12- light eucalyptus (green)
        "#e6e6fa",      # 13- lavender (cool violet)
        "#add8e6",      # 14- classic light blue
        "#e2cfe3",      # 15- lilac grey (neutral)
        "#bdd7ee",      # 16- soft sky blue    
    ]

    lightened_pastels = [lighten_color(c, amount=0.4) for c in pastel_colors]
    return lightened_pastels

def ts_colorPalette():
    color_palette  = ["orangered", "#66AA55", "#3366AA", "#EE7722", "#11AA99", "#992288", "#CCCC55", "#777777"]
    return color_palette

#%% packages and arguments
if __name__ == '__main__':
    import argparse
    
    import numpy as np
    from functools import partial
    
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.colors import ListedColormap, BoundaryNorm, to_rgb
    from matplotlib.patches import Rectangle
    import matplotlib.ticker as mticker
    
    import cartopy.crs as ccrs
        
    import xarray as xr
    #import nc_time_axis
    import cftime
    import calendar
        
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--variable', action='store', default=None, help="'hydrographs' (includes 'routing_hydrographs_r')")
    parser.add_argument('--reference', action='store', default=None, help="reference path")
    parser.add_argument('--ref_label', action='store', default="ref", help="ref label")    
    parser.add_argument('--simulations', action='store', default=None, help="simulations paths, separated by a single whitespace")
    parser.add_argument('--sim_labels', action='store', default=None, help="simulation labels, separated by a single whitespace or dollar sign '$'")
    parser.add_argument('--basinmap', action='store', default=None, help="basinmap path (used for representation only)")
    #
    parser.add_argument('--colors', action='store', default=None, help='colors separated a single whitespace')
    parser.add_argument('--region_boxes', action='store', default=False)
    parser.add_argument('--outfig', action='store', default=None)
    
    args, unknown = parser.parse_known_args()
    
    var_name = args.variable
    ref_filename = args.reference    
    
    sim_filenames = args.simulations.split(' ')
    basinmap_filename = args.basinmap
    #
    map_region_boxes = args.region_boxes
    #
    if ('$' in args.sim_labels):
        sim_labels = args.sim_labels.split('$')
    else:
        sim_labels = args.sim_labels.split(' ')

    ref_label = args.ref_label
    outfig = args.outfig

    ## inherited from MAPPER
    ## lon2,lat2 modified after discussing with A. Bierjon (2025-06-03) 
    RIVER = [
        dict(arrow = ( 1.15, -0.15), name = "YUKO", basin = 28, 
            lon = -162.75, lat = 62.25, lon2 = -161.75, lat2 = 61.75, #lon2 = -162.75, lat2 = 62.25, 
            lonx = -162.8830, latx = 61.9340, 
            ind = 2942-1, year1 = 1981, year2 = 1995, longname = "Yukon", station = "Pilot station"),
        dict(arrow = ( 0.5,  -0.15), name = "MCKZ", basin = 14, 
            lon = -133.25, lat = 67.50, lon2 = -131.75, lat2 = 67.25, #lon2 = -133.25, lat2 = 67.25, 
            lonx = -133.7447, latx = 67.4583, 
            ind = 2734-1, year1 = 1981, year2 = 2010, longname = "McKenzie", station = "Arctic red river"),
        dict(arrow = ( 1.15,  0.5),  name = "MISS", basin =  4, 
            lon =  -90.75, lat = 30.5,  lon2 =  -91.25, lat2 = 31.75, #lon2 =  -90.75, lat2 = 30.25, 
            lonx =  -90.9058, latx = 32.3150, 
            ind = 1392-1, year1 = 1981, year2 = 2010, longname = "Mississippi",  station = "Vicksburg"),    
        #
        dict(arrow = ( 1.15,  0.5),  name = "ORIN", basin = 22, 
            lon =  -63.50, lat =  7.75, lon2 =  -64.25, lat2 =  7.75, #lon2 =  -63.75, lat2 =  7.75, 
            lonx =  -63.6000, latx =  8.1500, 
            ind = 4212-1, year1 = 1981, year2 = 1989, longname = "Orinico", station = "Puente Angostura"),
        dict(arrow = ( 1.15,  1.15), name = "AMAZ", basin =  1, 
            lon =  -53,    lat = -1.5,  lon2 =  -55.25, lat2 = -1.75, #lon2 =  -53.25, lat2 = -1.75, 
            lonx =  -55.5110, latx = -1.9470, 
            ind = 1196-1, year1 = 1981, year2 = 2005, longname = "Amazon", station = "Obidos"),
        dict(arrow = ( 0.5,   1.15), name = "TOCA", basin = 36, 
            lon =  -49.25, lat = -5.25, lon2 =  -49.25, lat2 = -5.25, 
            lonx =  -49.3242, latx = -5.1281, 
            ind = 4980-1, year1 = 1981, year2 = 2010, longname = "Tocantins", station = "Itupiranga"),
        #
        dict(arrow = ( 0.5,  -0.15), name = "DANU", basin = 34, 
            lon =   28.75, lat = 45.25, lon2 =   29.25, lat2 = 45.25, #lon2 =   28.75, lat2 = 45.25, 
            lonx =   28.7167, latx = 45.2167, 
            ind = 4047-1, year1 = 1981, year2 = 2010, longname = "Danube", station = "Ceatal Izmail"),
        dict(arrow = ( 0.5,   1.15), name = "NIG",  basin = 10, 
            lon =    3.50, lat = 11.75, lon2 =    3.25, lat2 = 12.25, #lon2 =    3.25, lat2 = 11.75, 
            lonx =    3.3833, latx = 11.8667, 
            ind = 2119-1, year1 = 1982, year2 = 1994, longname = "Niger", station = "Malanville"),
        dict(arrow = ( 0.5,   1.15), name = "CONG", basin =  3, 
            lon =   15.25, lat = -4.25, lon2 =   15.75, lat2 = -3.75, #lon2 =   15.25, lat2 = -4.25, 
            lonx =   15.3000, latx = -4.3000, 
            ind = 1995-1, year1 = 1981, year2 = 2010, longname = "Congo", station = "Kinshasa"),
        #
        dict(arrow = ( 0.5,  -0.15), name = "OB",   basin =  8, 
            lon =   66.75, lat = 66.50, lon2 =   68.75, lat2 = 66.75, #lon2 =   66.75, lat2 = 66.75, 
            lonx =   66.5300, latx = 66.5700, 
            ind = 5217-1, year1 = 1981, year2 = 2010, longname = "Ob", station = "Salekhard"),
        dict(arrow = (-0.15, -0.15), name = "YENI", basin =  7, 
            lon =   86.75, lat = 68.25, lon2 =   86.75, lat2 = 67.75, #lon2 =   86.75, lat2 = 67.25, 
            lonx =   86.5000, latx = 67.4800, 
            ind =  500-1, year1 = 1981, year2 = 2010, longname = "Yenisei", station = "Igarka"),
        dict(arrow = (-0.15,  0.5),  name = "LENA", basin =  9, 
            lon =  127.25, lat = 70.75, lon2 =  127.25, lat2 = 71.25, #lon2 =  127.25, lat2 = 70.75, 
            lonx =  127.6500, latx = 70.7000, 
            ind = 4292-1, year1 = 1981, year2 = 2010, longname = "Lena", station = "Kusur"),
        #
        dict(arrow = (-0.15,  1.15), name = "BRAH", basin = 15, 
            lon =   89.75, lat = 25.25, lon2 =   89.75, lat2 = 24.75, #lon2 =   89.75, lat2 = 25.25, 
            lonx =   89.6700, latx = 25.1800, 
            ind = 2789-1, year1 = 1985, year2 = 1991, longname = "Brahmaputra", station = "Bahadurabad"),
        dict(arrow = (-0.15,  0.5),  name = "CHAN", basin = 13, 
            lon =  117.75, lat = 30.75, lon2 =  118.25, lat2 = 31.25, #lon2 =  117.75, lat2 = 30.75, 
            lonx =  117.6200, latx = 30.7700, 
            ind = 1947-1, year1 = 1981, year2 = 1988, longname = "Yangzi Jiang", station = "Datong"),
    ]

    # region boxes
    regions = [{"name": "North America", "lon": -170, "lat": 25, "w": 95, "h": 50},
               {"name": "South America", "lon": -85, "lat": -25, "w": 42.5, "h": 40},
               {"name": "Europe & Africa", "lon": -17.5, "lat": -17.5, "w": 55, "h": 75},
               {"name": "Boreal Asia", "lon": 55, "lat": 40, "w": 90, "h": 40},
               {"name": "Tropical Asia", "lon": 67.5, "lat": 15, "w": 60, "h": 22.5},           
    ]            

    ## figure attributes
    fig = plt.figure(figsize = (14,12))
    row_ratios=[1, 1, 1, 1, 1]
    nrows=5
    ncols=5
    
    gs = gridspec.GridSpec(nrows=nrows, ncols=ncols, height_ratios=row_ratios)
    
    fontsize_suptitle = 16
    fontsize_regions = 14
    fontsize_stations = 12
    fontsize_legend = 12
    
    title = "River discharge [m3/s]" if (var_name == 'hydrographs') else "Precipitation [mm/d]"
    """
    #if not difyears: ax0.set_title("%s-%s" % (sims[0].year1, sims[0].year2), loc="left")
    #ax0.set_title("%s [%s]" % (var.get("longname"), var.get("units") if var.get("units_ts") is None else var.get("units_ts")) if var.get("units") != "" else var.get("longname"))
    """
    plt.suptitle(title, fontsize=fontsize_suptitle)    
    
    ## MAP OF BASINS (TO IMPROVE)
    proj = ccrs.LambertCylindrical()
    ax_map = fig.add_subplot(gs[0:2, :], projection=proj, zorder=1)
    
    # remark : the original code takes basinmap from the first simulation
    for sim in ([basinmap_filename] if basinmap_filename else sim_filenames):       
        try:             
            basin = xr.open_dataset(sim)["basinmap"]        
            break

        except:
            basin = None
            pass
    
    #plot masks
    if basin is not None: 
        mask = xr.full_like(basin, fill_value=-1)
        
        for i, meta in enumerate(RIVER):                    
            mask = mask.where(basin != meta["basin"], i+1)
        
        # Plot masks
        cmap_palette = map_colorPalette()
        cmap = ListedColormap(cmap_palette)
            
        ax_map.pcolormesh(basin["lon"], basin["lat"], mask, 
                              cmap=cmap, norm=BoundaryNorm(np.arange(-0.5, cmap.N+0.5, 1), cmap.N), transform=ccrs.PlateCarree())            

    ax_map.coastlines(linewidth=0.5)
    ax_map.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
    
    # gridlines
    gl = ax_map.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    # longitude/latitude ticks, tick size
    gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, 60))
    gl.ylocator = mticker.FixedLocator(np.arange(-90, 91, 30))
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}
    
    # markers & regions
    x = [meta["lon"] for meta in RIVER]
    y = [meta["lat"] for meta in RIVER]
    ax_map.scatter(x, y, s=80, marker="v", color="red", edgecolor="k", transform=ccrs.PlateCarree(), zorder=12)
    
    for idx, meta in enumerate(RIVER):    
        ax_map.text(x[idx]+2, y[idx], f"{idx+1}", transform=ccrs.PlateCarree(), 
                    ha="left", va="center_baseline", fontsize=14, family="monospace", weight="bold",
                    bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0", alpha=0.25),
                    zorder=11)    

        row = idx % 3
        col = idx // 3
        
        if (row == 0) and (map_region_boxes):
            ax_map.add_patch(Rectangle((regions[col]["lon"], regions[col]["lat"]), regions[col]["w"], regions[col]["h"], 
                                       facecolor="white", edgecolor="black", linestyle="--", alpha=0.25, 
                                       transform=ccrs.PlateCarree(), zorder=11))
        
            ax_map.text(regions[col]["lon"]+1, regions[col]["lat"], regions[col]["name"], transform=ccrs.PlateCarree(), 
                        ha="left", va="bottom", fontsize=11, 
                        bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.2", alpha=0.85),
                        zorder=10)

    ## TIMESERIES
    if var_name == "hydrographs":
        try :
            obs = xr.open_dataset(ref_filename)["mergedhydro"]
        except :
            raise ValueError("'mergedhydro' not found in reference dataset")
    else:
        """
        obs[var].setGrid(grid = task["grid"], area = task["area"], contfrac = task["contfrac"] if task["contfrac"] != "auto" else task["path_contfrac"])
        obs[var].setReadfiles("%s-%s" % (sims[0].year1, min(2018, sims[0].year2)))
        obs[var].calcVarMaps(dict(id = var))
        obs[var].maps["basinmap"] = obs[var].readVar(obs[var].readfiles[0], dict(id = "basinmap"))        
        """
        raise ValueError(f"river_discharge.py does not currently support {var_name} variable")
            
    partial_hydro = partial(preprocess_hydro, var_name=var_name, RIVER=RIVER)        
    ds = xr.open_mfdataset(sim_filenames, combine="nested", concat_dim="simulation", 
                            decode_times=False,
                            preprocess=partial_hydro,
                            compat="override", coords="minimal",
                            chunks={"time_counter": 365})
    ds = ds.compute()

    # (2025-06-05) temporary fix: remove null hydrographs
    drop_sim_index = [s for s in ds['simulation'].values if (ds[var_name].sel(simulation=s) > 0).sum().item() == 0]

    ds = ds.sel(simulation=~ds.simulation.isin(drop_sim_index))    
    drop_sim_labels = [sim_labels[v] for v in drop_sim_index]
    keep_sim_labels = [v for v in sim_labels if v not in drop_sim_index]
    
    if drop_sim_index:    
        print(f"'hydrographs' is null for {drop_sim_labels} and hence has been removed. Possibly 'routing_hydrographs_r' exists, but it is not available")

    #plot figures
    labels = [ref_label] +keep_sim_labels

    if args.colors: 
        colors = args.colors.split(' ')
    else:
        colors = ts_colorPalette()

    for idx, meta in enumerate(RIVER):
        row = idx % 3
        col = idx // 3
    
        if (row == 0):
            gs_col = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=gs[2:,col])
            
            ax_regTitle = fig.add_subplot(gs_col[:])
            ax_regTitle.axis("off")
            ax_regTitle.text(0.5, 1.055, regions[col]["name"],
                             ha="center", va="bottom",
                             fontsize=fontsize_regions, weight="bold",
                             transform=ax_regTitle.transAxes
            )
        
        ax_ts = fig.add_subplot(gs_col[row, 0])
        ax_ts.set_prop_cycle("color", colors)
    
        # observations (mean)
        if (var_name in 'routing_hydrographs_r'):        
            obs_mean = obs.sel(stations=meta["ind"]).groupby("time.month").mean("time", skipna=True)
            obs_mean = obs_mean.compute()
            
            obs_mean_padded = xr.concat([obs_mean.sel(month=12).assign_coords(month=0),
                                         obs_mean,
                                         obs_mean.sel(month=1).assign_coords(month=13)], dim="month")
        else:
            raise ValueError(f"river_discharge.py does not currently support {var_name} variable")
        
            """
            ys = obs[:, meta["ind"]].reshape((-1,12)).mean(axis=0)
            else:
            mask = np.where(obs.maps["basinmap"] == item["basin"], 1, 0)
            ys = obs.grid.meanmask(obs.maps[var.get("id")][:12], mask)
            """            

        l1 = ax_ts.plot(obs_mean_padded, color="k", linewidth=2)
    #    l1 = obs_mean_padded.plot(ax=ax_ts, color="k", linewidth=2)
        
        # simulations (plot all in one call)
        sim_data = ds[var_name].isel(location=idx)
    
        sim_data_padded = xr.concat([sim_data.sel(month=12).assign_coords(month=0),
                                     sim_data,
                                     sim_data.sel(month=1).assign_coords(month=13)], dim="month")
        
        l2 = ax_ts.plot(sim_data_padded.squeeze().values.T, linewidth=1.5) 
        
        #plot properties    
        ax_ts.set_title(f"{meta['longname']} ({idx+1})", fontsize=fontsize_stations)
    
        ax_ts.set_xlim(0.5,12.5)    
        ax_ts.set_xticks(range(1,13))
        ax_ts.set_xticklabels([calendar.month_abbr[i][0] for i in range(1, 13)], fontsize=10)
    
        ax_ts.set_ylim([0, ax_ts.get_ylim()[1]])
        if len(ax_ts.get_yticks()) > 6: 
            ax_ts.set_yticks(ax_ts.get_yticks()[::2])
    
        #legend (see below)
        if idx == 0:
            lines = l1 + l2
            #label = "%s (%s-%s)" % (obs.label, obs.year1, obs.year2) if difyears or obs.year1 != sims[0].year1 or obs.year2 != sims[0].year2 else obs.label
    
    # legend
    ax_legend = fig.add_subplot(gs_col[row+1, 0])
    ax_legend.axis("off")
    ax_legend.legend(handles=lines, labels=labels,
                     loc="upper center",
                     frameon=True, 
                     fontsize=fontsize_legend)
    
    plt.subplots_adjust(bottom=0.05, top=0.95, left=0.1, right=0.95, wspace=0.6, hspace=0.6)
    if outfig is not None:
        plt.savefig(outfig)
    plt.close()    
