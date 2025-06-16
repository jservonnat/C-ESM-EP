import sys

from scipy import ndimage

import xarray as xr
import os
import matplotlib.pyplot as plt

import numpy as np

import warnings

from numpy import linspace
from scipy import stats

import matplotlib.dates as dplt
import locale
import pandas as pd

# returns seasonal cycle of sea ice metric - sea ice surface temperature here


def get_seasonal_sistemp(file_siconc, file_sistem, hem): #hem = 'n' or 's'
    
    # open model file
    mod_ds = xr.open_dataset(file_siconc,decode_times=True)
    
    if hem == 'n':
        mod_ds = mod_ds.where(mod_ds['nav_lat'] > 50)
        idx = [11,0,1]

    elif hem == 's':
        mod_ds = mod_ds.where(mod_ds['nav_lat'] < -50)
        idx = [6,7,8]

    siconc = mod_ds['siconc']

    mod_sistem = xr.open_dataset(file_sistem,decode_times=True)
    sistem = mod_sistem['sistem']    
    met_skt = sistem.where(siconc > 0.15).mean(dim=('x','y')) 
    
    
    #model metrics & error
    met_seas_mod = met_skt.groupby("time_counter.month").mean()
    err_seas_mod = met_skt.groupby("time_counter.month").std()
    
    # open obs. file and calculate metrics & errors

    # SS - comment out what concerns obs

#     file_obs = '/scratchu/khimmich/CMIP7_EVAL_OBS/metrics/' + 'metskt' + '_clim_err_'+hem+'h.nc' 
#     obs_ds = xr.open_dataset(file_obs,decode_times=True)
#     met_seas_obs = obs_ds['metskt']    
#     err_seas_obs1 = np.sqrt(obs_ds['err_obs1']**2 + obs_ds['err_var']**2)
#     err_seas_obs2 = np.sqrt(obs_ds['err_obs2']**2 + obs_ds['err_var']**2)

    # create output dataset
    out = xr.Dataset({
        # SS - comment out what concerns obs
        # 'sea_ice_stemp_obs' : xr.DataArray(
        #     data   =  met_seas_obs.values,
        #     dims   = ['month'],
        #     coords = [np.asarray(range(1,13))]),

        'sea_ice_stemp_model' : xr.DataArray(
        data   =  met_seas_mod.values,
        dims   = ['month'],
        coords = [np.asarray(range(1,13))]),       
    })
    
    # SS - comment out what concerns obs
    # out["sea_ice_stemp_obs"].attrs["long_name"] = "Sea ice surface temperature"
    # out["sea_ice_stemp_obs"].attrs["units"] = "°C"  
    
    out["sea_ice_stemp_model"].attrs["long_name"] = "Sea ice surface temperature"
    out["sea_ice_stemp_model"].attrs["units"] = "°C"  
    
    return(out) 

    
if __name__ == "__main__":
  hem = sys.argv[1]
  file_siconc = sys.argv[2]
  file_sistem = sys.argv[3]
  file_out = sys.argv[4]
  #file_out_obs = sys.argv[5]
  #
  out=get_seasonal_sistemp(file_siconc, file_sistem, hem)
  print(out)
  out.to_netcdf(file_out)
  


    
