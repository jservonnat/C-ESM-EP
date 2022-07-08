#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------- #
# -- Header of the atlas.py ; import the useful python modules (CliMAF, NEMO_atlas, -- #
# -- and potentially your own stuff stored in my_plot_functions.py in the current   -- #
# -- working directory.                                                             -- #
# ------------------------------------------------------------------------------------ #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
#from __future__ import unicode_literals, print_function, absolute_import, division
from __future__ import unicode_literals, print_function, division

# -- Imports
from climaf.api import *
from climaf.html import * 
from CM_atlas import *
from env.site_settings import onCiclad, onSpirit, atTGCC, atCNRM
#from climaf.utils import Climaf_Error
from getpass import getuser
from climaf import __path__ as cpath
import json
import os
import copy
import subprocess
import shlex
from optparse import OptionParser
from locations import path_to_cesmep_output_rootdir, path_to_cesmep_output_rootdir_on_web_server, \
    root_url_to_cesmep_outputs

csync(True)

# -----------------------------------------------------------------------------------
# --   PART 1: Get the instructions from:
# --              - the default values
# --              - the parameter file (priority 2)
# --              - the command line (priority 1)
# -----------------------------------------------------------------------------------


# -- Description of the atlas
# -----------------------------------------------------------------------------------
desc = "\n\nCliMAF Earth System Model Evaluation Platform: comparing multiple simulations against references " \
       "(https://github.com/jservonnat/C-ESM-EP/wiki)"


# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------
parser = OptionParser(desc)
parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("--index_name",
                  help="Name of the html file (atlas)",
                  action="store", default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store", default=None)
parser.add_option("--component",
                  help="Name of the component - set of diagnostics",
                  action="store", default=None)
parser.add_option("--cesmep_frontpage",
                  help="URL to C-ESM-EP frontpage",
                  action="store", default=None)

(opts, args) = parser.parse_args()


# -- Define the path to the main C-ESM-EP directory:
# -----------------------------------------------------------------------------------
rootmainpath = os.getcwd()
print('rootmainpath = ',rootmainpath)
if os.path.isfile(rootmainpath+'main_C-ESM-EP.py'):
     main_cesmep_path = rootmainpath
if os.path.isfile(rootmainpath+'/../main_C-ESM-EP.py'):
     main_cesmep_path = rootmainpath+'/../'
if os.path.isfile(rootmainpath+'/../../main_C-ESM-EP.py'):
      main_cesmep_path = rootmainpath+'/../../'


# -- Get the default parameters from default_atlas_settings.py -> Priority = default
# -----------------------------------------------------------------------------------
default_file = '/share/default/default_atlas_settings.py'
#execfile(main_cesmep_path+default_file)
exec(open(main_cesmep_path+default_file).read())

# -- Get the values for comparison and component
# -----------------------------------------------------------------------------------
component = opts.component
comparison = opts.comparison
index_name = opts.index_name
cesmep_frontpage = opts.cesmep_frontpage

# -- Build the paths to:
# -----------------------------------------------------------------------------------
#     - the datasets_setup.py
#     - the parameter file
#     - the diagnostics file
datasets_setup = main_cesmep_path + comparison + '/datasets_setup.py'
param_file = main_cesmep_path + comparison + '/' + component + '/params_' + component + '.py'
diagnostics_file = param_file.replace('params_', 'diagnostics_')
if not os.path.isfile(diagnostics_file):
    diagnostics_file = main_cesmep_path + 'share/cesmep_diagnostics/diagnostics_' + component + '.py'
print('-- Use diagnostics_file =', diagnostics_file)


# -- If we specify a datasets_setup from the command line, we use 'models' from this file
# -----------------------------------------------------------------------------------
datasets_setup_available_period_set_file = datasets_setup.replace('.py', '_available_period_set.py')
if os.path.isfile(datasets_setup_available_period_set_file):
    use_available_period_set = True
    exec(open(datasets_setup_available_period_set_file).read())
    # Create Wmodels_ts and Wmodels_clim from Wmodels
    Wmodels_clim = copy.deepcopy(Wmodels)
    for item in Wmodels_clim:
        clim_period_args = copy.deepcopy(item['clim_period'])
        item.pop('clim_period')
        item.pop('ts_period')
        item.update(clim_period_args)
    #
    Wmodels_ts = copy.deepcopy(Wmodels)
    for item in Wmodels_ts:
        ts_period_args = copy.deepcopy(item['ts_period'])
        item.pop('ts_period')
        item.pop('clim_period')
        item.update(ts_period_args)
else:
    exec(open(datasets_setup).read())
    use_available_period_set = False


# -- Get the username ; if we work on fabric (ciclad), we get the manually attributed username
# -----------------------------------------------------------------------------------
username = getuser()
user_login = (os.getcwd().split('/')[4] if username == 'fabric' else username)


# -- Get the site specifications:
# -----------------------------------------------------------------------------------
# -> path_to_cesmep_output_rootdir = where (directory) we physically store the results of the C-ESM-EP
# (root directory of the whole atlas tree)
# -> path_to_cesmep_output_rootdir_on_web_server = path to the results on the web server (which are
# soft- or hard-linked to results on path_to_cesmep_output_rootdir, or even copied from there)
# -> root_url_to_cesmep_outputs = URL of the root directory of the C-ESM-EP atlas (need to add 'C-ESM-EP',
# comparison and component to reach the atlas)

# -- Location of the directory where we will store the results of the atlas
atlas_dir = path_to_cesmep_output_rootdir + '/C-ESM-EP/' + comparison + '_' + user_login + '/' + component

# -- Url of the atlas (without the html file)
atlas_url = atlas_dir.replace(path_to_cesmep_output_rootdir, root_url_to_cesmep_outputs)



# -- We create the atlas directory if it doesn't exist, or remove the figures
# -----------------------------------------------------------------------------------
if atCNRM or atTGCC or onCiclad or onSpirit:
    if not os.path.isdir(atlas_dir):
        os.makedirs(atlas_dir)
    else:
        os.system('rm -f '+atlas_dir+'/*.png')


# -- Specify the directory where we will output the atlas html file and the figures
# -----------------------------------------------------------------------------------
alternative_dir = {'dirname': atlas_dir}


# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug',
# -- intermediate -> 'warning')
# -----------------------------------------------------------------------------------
clog(verbose)


# -- Print the models
# -----------------------------------------------------------------------------------
print('==> ----------------------------------- #')
print('==> Working on models:')
print('==> ----------------------------------- #')
print('  ')
for model in models:
    for key in model:
        print('  '+key+' = ', model[key])
    print('  --')
    print('  --')

print('==> ----------------------------------- #')
print('==> Against reference:')
print('==> ----------------------------------- #')
print('  ')
if reference=='default':
   print('  reference = default')
   print('  --> you are using the catalog of pre-defined references (in share/cesmep_modules/reference/reference.py)')
   print('  --> you can setup you own references in custom_obs_dict.py for each variable independently')
else:
   for key in reference:
        print('  '+key+' = ', reference[key])
   print('  --')
   print('  --')


# -----------------------------------------------------------------------------------
# --   End PART 1 
# -- 
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
# --   PART 2: Build the html
# --              - the header
# --              - and the sections of diagnostics:
# --                 * Atlas Explorer
# --                 * Atmosphere
# --                 * Blue Ocean - physics
# --                 * White Ocean - Sea Ice 
# --                 * Green Ocean - Biogeochemistry
# --                 * Land Surfaces
# --                 ...
# -----------------------------------------------------------------------------------


# -- Setup a css style file
# ---------------------------------------------------------------------------- >
style_file = main_cesmep_path+'share/fp_template/cesmep_atlas_style_css'


# -- Head title of the atlas -> default value should be override from diagnostics_${comp}.py
# ---------------------------------------------------------------------------- >
atlas_head_title = component


# -- Get the parameters from the param file -> Priority = 2
# -----------------------------------------------------------------------------------
if os.path.isfile(param_file):
    exec(open(param_file).read())


# -- Add the season to the html file name
# -----------------------------------------------------------------------------------
if not index_name:
    index_name = 'atlas_'+component+'_'+comparison+'.html'


# -- Automatically zoom on the plot when the mouse is on it
# ---------------------------------------------------------------------------- >
hover = False


# -- Add the compareCompanion (P. Brockmann)
# --> Works as a 'basket' on the html page to select some figures and
# --> display only this selection on a new page
# ---------------------------------------------------------------------------- >
add_compareCompanion = True


# -> Clean the cache if specified by the user
# -----------------------------------------------------------------------------------
if clean_cache and not clean_cache == 'False':
    print('!!! Fully clean the cache before starting the atlas !!!')
    craz()
    print('!!! Cache cleaned !!!')


# -- Execute the diagnostic file ${comparison}/${component}/diagnostics_${component}.py
# -----------------------------------------------------------------------------------
exec(open(diagnostics_file).read())


# -----------------------------------------------------------------------------------
# --   End PART 2
# --
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
# --   PART 3: Finalize the index by replacing the paths to the cache for the paths
# --   to the alternate directory
# -----------------------------------------------------------------------------------
# --   ONLY FOR DEVELOPERS - users shouldn't need to modify this section
# --   Contact jerome.servonnat@lsce.ipsl.fr
# -----------------------------------------------------------------------------------
# -- Here we can work either on Ciclad or at TGCC
# -- On Ciclad we feed directly the cache located on the thredds server
# -- and point at this web address.
# -- At TGCC we need to:
# --   - feed the cache on $SCRATCHDIR (set in your environment) and make a hard link in
# --     a target directory (alt_dir_name, based on the current working directory and
# --     subdir)
# --   - at the end of the atlas, we copy the target directory (alt_dir_name) on the
# --     $WORKDIR (work_alt_dir_name) before copying it on the thredds with thredds_cp
# --   - Eventually, we thredds_cp the directory work_alt_dir_name
# --     on the /ccc/work/cont003/thredds/public space

# -- Adding the compareCompanion JavaScript functionality to make a selection of images
if add_compareCompanion:
    print('Add compareCompanion')
    index += compareCompanion()

# -- End the index
index += trailer()


# -- Add link to main frontpage
climaf_doc_url = 'https://climaf.readthedocs.io/en/master/'
# -- Replace url to CliMAF documentation with url to C-ESM-EP frontpage
index = index.replace(climaf_doc_url, cesmep_frontpage)
# -- Replace CliMAF documentation with C-ESM-EP frontpage of comparison COMPARISON
index = index.replace('CliMAF documentation', 'Back to C-ESM-EP frontpage of comparison: '+comparison)

# -- Write the atlas html file
outfile = atlas_dir + "/" + index_name
print('outfile = ', outfile)
with open(outfile, "w") as filout:
    filout.write(index)

blabla = None
if onCiclad or onSpirit:
   # -- Copy on thredds... 
   # ----------------------------------------------------------------------------------------------
   # -- thredds directory (web server)
   threddsdir = str.replace(atlas_dir,'scratchu','thredds/ipsl')
   os.system('rm -rf '+threddsdir)
   th_dir = str.replace(threddsdir,'/'+component,'')
   if not os.path.isdir(th_dir):
        os.makedirs(th_dir)
   os.system('cp -r '+atlas_dir+' '+th_dir)
   print("index copied in : "+threddsdir)

   # -- Url to use to access the page from the web
   #alt_dir_name = "/thredds/fileServer/IPSLFS"+str.split(threddsdir,'thredds/ipsl')[1]+'/'+subdir
   alt_dir_name = "/thredds/fileServer/IPSLFS"+str.split(threddsdir,'thredds/ipsl')[1]
   root_url = "https://vesg.ipsl.upmc.fr"

   # -- and return the url of the atlas
   # ----------------------------------------------------------------------------------------------
   print("Available at this address "+root_url+outfile.replace(atlas_dir,alt_dir_name))


#

#
if atTGCC:
    # -- Ecriture du fichier html dans le repertoire sur scratch
    path_to_comparison_outdir_workdir_tgcc = atlas_dir.replace('scratch', 'work')
    if not os.path.isdir(path_to_comparison_outdir_workdir_tgcc):
        os.makedirs(path_to_comparison_outdir_workdir_tgcc)
    else:
        print('rm -rf '+path_to_comparison_outdir_workdir_tgcc+'/*')
        os.system('rm -rf '+path_to_comparison_outdir_workdir_tgcc+'/*')
    cmd1 = 'cp -r '+atlas_dir+'* '+path_to_comparison_outdir_workdir_tgcc
    print(cmd1)
    os.system(cmd1)
    #
    # -- thredds_cp du repertoire copie sur le work
    path_to_comparison_on_web_server = path_to_cesmep_output_rootdir_on_web_server + '/C-ESM-EP/' + comparison + '_' + \
                                       user_login
    cmd12 = 'rm -rf '+path_to_comparison_on_web_server+'/'+component
    print(cmd12)
    os.system(cmd12)
    cmd2 = 'thredds_cp '+path_to_comparison_outdir_workdir_tgcc+' '+path_to_comparison_on_web_server+'/'
    print(cmd2)
    os.system(cmd2)

print(' -- ')
print(' -- ')
print(' -- ')
print('Index available at : ' + outfile.replace(path_to_cesmep_output_rootdir, root_url_to_cesmep_outputs))

if atTGCC:
    print("The atlas is ready as ", index_name.replace(atlas_dir, path_to_comparison_outdir_workdir_tgcc))
else:
    print("The atlas is ready as ", index_name)

# -----------------------------------------------------------------------------------
# --   End PART 3
# --
# -----------------------------------------------------------------------------------


# -- Systematically clean the cache
if isinstance(routine_cache_cleaning, list) or isinstance(routine_cache_cleaning, dict):
    if not isinstance(routine_cache_cleaning, list):
        routine_cache_cleaning = [routine_cache_cleaning]
    for clean_args in routine_cache_cleaning:
        print('clean_args = ', clean_args)
        crm(**clean_args)
elif routine_cache_cleaning == 'figures_only':
    craz()

# -----------------------------------------------------------------------------------
# -- End of the atlas
# -----------------------------------------------------------------------------------


