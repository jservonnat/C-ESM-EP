"""
Try to make a simple script for bottom S
"""

import xarray as xr
import sys

file_so = xr.open_dataset(sys.argv[1])
file_output = str(sys.argv[2])

mask_ocean = file_so['so'].isel(time_counter=0).drop('time_counter') > 0
vert_diff_minus_all = (mask_ocean - mask_ocean.shift(deptht=-1)).isel(deptht=range(1,len(mask_ocean.deptht)))
bot_depth_all = (mask_ocean.deptht * vert_diff_minus_all).where(vert_diff_minus_all > 0).sum('deptht').astype('float')

bot_depth_all_wo0 = bot_depth_all.where(bot_depth_all != 0, 5.057600e-01)
Sbot = file_thetao['so'].sel(deptht=bot_depth_all_wo0).where(bot_depth_all > 0)

Sbot.drop('deptht').to_dataset(name='S_bottom').to_netcdf(file_output)
