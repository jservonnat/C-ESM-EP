
# --------------------------------------------------------------------------
# -- USER INTERFACE
# -- Specify your simulation/dataset request here
# -- This tool helps you to browse the existing results using '*'
# -- and refine your request

# -- Dictionary of your requested dataset -> same dictionary as in the models list in datasets_setup.py
dat_dict = dict(project = 'IGCM_OUT',
                root    = '/ccc/store/cont003/thredds',
                login   = 'p86denv',
                model   = 'IPSLCM6',
                experiment = 'historical',
                simulation = '*',
                period     = '0001_9998',
                frequency  = 'monthly',
                )

# -- Variable dictionary -> specifications that might be project-dependant to reach one file
var_dict = dict(variable = 'tas',
                DIR      = 'ATM')
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# -- CESMEP SIMU FINDER

from climaf.api import *

# -- Update dictionary
dat_dict.update(var_dict)

# -- Find the datasets
dat = ds(**dat_dict)

if dat.baseFiles():
   print '  '
   print '  '
   print '  '
   print ' CliMAF found those files with your request ',dat_dict
   print '-->  '
   for found_file in str.split(dat.baseFiles(),' '):
       print found_file
   print '  '
   print ' -- Check that your request points to only one simulation, variable and frequency (table)'
   print '  '
else:
   print '  '
   print '  '
   print '  '
   print 'No File found for your request -- ',dat_dict
   print '  '
# --------------------------------------------------------------------------

