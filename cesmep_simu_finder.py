
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


# -- Get the comparison name and build the datasets_setup.py file name
args = sys.argv
dataset_number = None
models = None
if len(args)>=2:
    comparison = args[1]
    if not comparison[len(comparison)-1]=='/': comparison+='/'
    datasets_setup_file = comparison+'datasets_setup.py'
    execfile(datasets_setup_file)
if len(args)==3:
    dataset_number = int(args[2])


# -- Analyse if we use the datasets_setup of a comparison or dat_dict (provided by the user)
if not models:
   models = [ dat_dict ]

if not dataset_number:
   ind = range(len(models))
else:
   ind = [ dataset_number - 1 ]

# -- Loop on models
for i in ind:

  model = models[i]

  # -- Update dictionary
  model.update(var_dict)

  # -- Apply frequency and period manager
  frequency_manager_for_diag(model, diag='clim')
  get_period_manager(model)
  
  # -- Find the datasets
  dat = ds(**model)

  if dat.baseFiles():
     print '  '
     print '  '
     print '  '
     print ' CliMAF found those files with your request ',model
     print '-->  '
     for found_file in str.split(dat.baseFiles(),' '):
         print found_file
     print '  '
     print ' -- Check that your request points to only one simulation, variable and frequency (and table for MIP simulations)'
     print '  '
  else:
     print '  '
     print '  '
     print '  '
     print 'No File found for your request -- ',model
     print '  '
# --------------------------------------------------------------------------

