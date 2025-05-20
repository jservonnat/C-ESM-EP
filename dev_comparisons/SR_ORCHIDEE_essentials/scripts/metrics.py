import sys
from pathlib import Path
import xarray as xr
xr.set_options(keep_attrs=True)
import numpy as np
import pandas as pd

#from sklearn.metrics import root_mean_squared_error

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
#import seaborn as sns

from random import choices
from string import ascii_uppercase

import warnings
warnings.simplefilter("ignore")

#%%
def exploratory_stats(ref_filename, sim_filename, agg, figure_filename):  
#    try:     
#        ref = xr.open_dataset(ref_filename)
#    except TypeError:
#        print("Invalid NETCDF file variable")  
#    
#    try:
#        sim = xr.open_dataset(sim_filename)
#    except TypeError:
#        print("Invalid NETCDF file variable")
#
#    if agg not in {'Global', 'North', 'Tropics', 'South'}:
#        raise Exception("Invalid region aggregation")
#    
#    #%% WEIGHT OF TRANSCOM REGIONS
#    mask_filepath = Path('/home/ssenesi/cesmep/data/regs_360720.nc')
#    try:     
#        transcom = xr.open_dataset(mask_filepath)
#    except TypeError:
#        print("Invalid NETCDF file mask")      
#    
#    if agg == 'Global':
#        regions = ['Northern Land', 'Tropical Land', 'Southern Land']
#    elif agg == 'North':
#        regions = ['Boreal North America', 'Temperate North America', 'Europe', 'Boreal Asia', 'Temperate Asia']
#    elif agg == 'Tropics':
#        regions = ['Tropical South America', 'North Africa', 'Tropical Asia']
#    elif agg == 'South':
#        regions = ['Temperate South America', 'South Africa', 'Australia & New Zealand']
#    ## other possible aggregations based on transcom ?
#    
#    
#    ## region_idx ({name : index value})
#    region_idx = dict(zip(transcom['reg_label'].values, transcom['reg_label']['reg'].values))
#    
#    grid_points_number = []
#    
#    for label in regions:
#        j = region_idx[label]
#        
#        grid_points_number.append(int(transcom['reg_mask'].sel(reg=j).sum().values)) 
#    
#    ## add aggregation type at the beginning
#    regions.insert(0, agg)
#    grid_points_number.insert(0, sum(grid_points_number))
#    
#    grid_dim = dict(zip(regions, grid_points_number))
#    
#    #%% RANDOM SAMPLING ON EACH REGION
#    varname_ref = list(ref.keys())[1]
#    
#    data, data_sampled_df = [], [], 
#    metrics = []
#    N = 1000
#    
#    for label in regions[1:]:
#        j = region_idx[label]
#    
#        """
#        we recover only the elements of ref affected by the mask,  
#        to then take int(s*(N_reg/N)) random samples, 
#        with : s = 1000, N_reg the number of mask points, and N the number of aggregated mask points
#        """    
#        var_reg = ((transcom['reg_mask'].sel(reg=j).where(transcom['reg_mask'].sel(reg=j) == 1).values)*(ref[varname_ref] -sim[varname_ref]))
#        
#        var_reg_flat = var_reg.values.flatten() 
#        var_reg_flat_notnull = var_reg_flat[~np.isnan(var_reg_flat)]
#        
#        data.append(var_reg_flat_notnull)
#    
#        weight = int(N*grid_dim[label]/grid_dim[regions[0]])
#        #data_sampled.append(np.random.choice(var_reg_flat_notnull, weight))
#        
#        df = pd.DataFrame(data=np.random.choice(var_reg_flat_notnull, weight), columns=['value'])
#        df['region'] = label
#        df['subregion'] = label
#            
#        data_sampled_df.append(df)
#    
#    #    metrics.append(root_mean_squared_error(var_reg_flat_notnull, np.zeros(var_reg_flat_notnull.size)))
#    
#    # global data
#    data.insert(0, np.concatenate(data).ravel())
#    
#    data_sampled_reg = pd.concat(data_sampled_df, axis=0)
#    data_sampled_regsub = data_sampled_reg.copy(deep=True)
#    data_sampled_regsub['region'] = regions[0]
#    
#    data_sampled = pd.concat([data_sampled_regsub, data_sampled_reg], axis=0)
#    
#    #%% Plot customization
#    color = [   "#B2BEB5", "#D3D3D3", #gray
#                "#1f77b4", "#aec7e8", #blue
#                "#ff7f0e", "#ffbb78", #orange
#    			"#2ca02c", "#98df8a", #green
#    			"#d62728", "#ff9896", #red
#    			"#9467bd", "#c5b0d5", #purple
#    			"#8c564b", "#c49c94", #brown
#    			"#e377c2", "#f7b6d2", #pink			
#    			"#bcbd22", "#dbdb8d", #olive green
#    			"#17becf", "#9edae5"  #cyan 
#    			]
#    
#    dark_palette = color[0:2*len(regions):2]
#    light_palette = color[1:2*len(regions):2]
#    
#    xlabel = ref[varname_ref].attrs['long_name'] if ('long_name' in ref[varname_ref].attrs) else varname_ref
#    ylabel = ref[varname_ref].attrs['units'] if ('units' in ref[varname_ref].attrs) else ''
#    
#    PROPS = {
#        'boxprops':{'facecolor':'none', 'edgecolor':'black', "linewidth": 0.25},
#        'medianprops':{'color':'black', "linewidth": 1},
#        'whiskerprops':{'color':'black', "linewidth": 0.25},
#        'capprops':{'color':'black', "linewidth": 1}
#    }
#    
#    #%% PLOT PRODUCTION
#    fig, ax = plt.subplots(figsize=(12,8), dpi=600)
#    sns.set_style("darkgrid")
#    
#    ax = sns.boxplot(data[0], showfliers = False, **PROPS)
#    
#    ax = sns.violinplot(data=data, density_norm="width", palette=light_palette, inner=None, linewidth=0.75)
#    plt.setp(ax.collections, alpha=.75)
#    
#    ax = sns.swarmplot(data=data_sampled, x='region', y='value', hue='subregion', palette=dark_palette[1:], edgecolor="gray", s=3, legend=False)
#    
#    ax.set_xticks(list(range(len(regions))), regions)
#    ax.set_xlabel(xlabel)
#    ax.set_ylabel(ylabel) #r'${0}$'.format(ylabel)
#
#    figure_filename = "{0}_ORCHIDEE-exploratory_{1}_{2}.png".format(varname_ref, agg, ''.join(choices(ascii_uppercase, k=10)))
#    fig.savefig(fname=figure_filename)
#
#    return figure_filename

    fig, ax = plt.subplots(figsize=(12,8), dpi=600)
    #figure_filename = "{0}_ORCHIDEE-exploratory_{1}.png".format(agg, ''.join(choices(ascii_uppercase, k=10)))
    fig.savefig(fname=figure_filename)

    #return figure_filename

#%% assign inputs
if __name__ == "__main__":
    print("Received args:", sys.argv)

    agg = sys.argv[1] 
    
    ref_filename = sys.argv[2]
    sim_filename = sys.argv[3]
    figure_filename = sys.argv[4]
    
    exploratory_stats(ref_filename, sim_filename, agg, figure_filename)
