"""
Try to make a simple script for bottom T
"""

import xarray as xr
import sys

file_thetao = xr.open_dataset(sys.argv[1])
file_so = xr.open_dataset(sys.argv[2])
file_output = str(sys.argv[3])

mask_ocean = file_so['so'].isel(time_counter=0).drop('time_counter') > 0
vert_diff_minus_all = (mask_ocean - mask_ocean.shift(deptht=-1)).isel(deptht=range(1,len(mask_ocean.deptht)))
bot_depth_all = (mask_ocean.deptht * vert_diff_minus_all).where(vert_diff_minus_all > 0).sum('deptht').astype('float')

bot_depth_all_wo0 = bot_depth_all.where(bot_depth_all != 0, 5.057600e-01)
Tbot = file_thetao['thetao'].sel(deptht=bot_depth_all_wo0).where(bot_depth_all > 0)

Tbot.drop('deptht').to_dataset(name='T_bottom').to_netcdf(file_output)