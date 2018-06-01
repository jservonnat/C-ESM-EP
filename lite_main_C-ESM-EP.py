# ------------------------------------------------------------------------------------ #
# -- Welcome in the lite_main_C-ESM-EP.py!
# -- 
# -- This is a lite version of the main_C-ESM-EP.py script that is central to the C-ESM-EP.
# -- This version differs from main_C-ESM-EP.py only withing part 2: there are only
# -- atlas explorer and an example left in the available diags.
# -- You are invited to incorporate your new diagnostics within part 2.
# -- There is no need to modify part 1 and 3.
# --
# -- Enjoy!
# -- 
# -- Created by Jerome Servonnat (LSCE - IPSL - CEA)
# -- contact : jerome.servonnat at lsce.ipsl.fr
# ------------------------------------------------------------------------------------ #







# ------------------------------------------------------------------------------------ #
# -- Header of the atlas.py ; import the useful python modules (CliMAF, NEMO_atlas, -- #
# -- and potentially your own stuff stored in my_plot_functions.py in the current   -- #
# -- working directory.                                                             -- #
# ------------------------------------------------------------------------------------ #
from climaf.api import *
from climaf.html import * 
from climaf import cachedir
from CM_atlas import *
from climaf.site_settings import onCiclad, atTGCC
from getpass import getuser
from climaf import __path__ as cpath
import json
import os, copy, subprocess, shlex



# -----------------------------------------------------------------------------------
# --   PART 1: Get the instructions from:
# --              - the default values
# --              - the parameter file (priority 2)
# --              - the command line (priority 1)
# -----------------------------------------------------------------------------------


# -- Description of the atlas
# -----------------------------------------------------------------------------------
desc="\n\nAtlas Comparaisons de simulations (par rapport a une simulation de ref)"


# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser(desc) ; parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("-p", "--params",
                  help="Parameter file for the Coupled Model atlas (.py)",
                  action="store",default="params_couple.py")
parser.add_option("-s", "--season",
                  help="Season for the atlas",
                  action="store",default=None)
parser.add_option("--proj",
                  help="Projection: choose among GLOB, NH30, SH30",
                  action="store",default=None)
parser.add_option("--index_name",
                  help="Name of the html file (atlas)",
                  action="store",default=None)
parser.add_option("--clean_cache",
                  help="Set to 'True' or 'False' to clean the CliMAF cache (default: 'False')",
                  action="store",default=None)
parser.add_option("--datasets_setup",
                  help="Name of the file containing the list of dictionaries describing the datasets",
                  action="store",default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store",default=None)

(opts, args) = parser.parse_args()


print 'opts.comparison = ', opts.comparison

# -- Get the default parameters from default_atlas_settings.py -> Priority = default
# -----------------------------------------------------------------------------------
default_file = '/share/default/default_atlas_settings.py'
while not os.path.isfile(os.getcwd()+default_file):
    default_file = '/..'+default_file
execfile(os.getcwd()+default_file)


# -- If we specify a datasets_setup from the command line, we use 'models' from this file
# -----------------------------------------------------------------------------------
if opts.datasets_setup:
   datasets_setup_available_period_set_file = str.replace(opts.datasets_setup,'.py','_available_period_set.py')
   if os.path.isfile(datasets_setup_available_period_set_file):
      use_available_period_set = True
      execfile(datasets_setup_available_period_set_file)
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
      execfile(opts.datasets_setup)
      use_available_period_set = False


# -- Get the parameters from the param file -> Priority = 2
# -----------------------------------------------------------------------------------
execfile(opts.params)


# -- Get the command line arguments -> Priority = 1
# -----------------------------------------------------------------------------------
if opts.season:
   season = opts.season
if opts.proj:
   proj = opts.proj
if opts.index_name:
   index_name = opts.index_name
if opts.clean_cache:
   clean_cache = opts.clean_cache



# -- Add the season to the html file name
# -----------------------------------------------------------------------------------
if not index_name:
   tmp_param_filename = str.split(opts.params,'/')
   index_name = str.replace(tmp_param_filename[len(tmp_param_filename)-1],'params_','')
   if opts.comparison:
      index_name = str.replace(index_name,'.py', '_'+opts.comparison+'.html')
   index_name = str.replace(index_name,'.py','.html')


# -- Add the user to the html file name
# -----------------------------------------------------------------------------------
user_login = ( str.split(getcwd(),'/')[4] if getuser()=='fabric' else getuser() )
index_name = 'atlas_'+index_name



# -> Clean the cache if specified by the user
# -----------------------------------------------------------------------------------
print 'clean_cache = ',clean_cache
if clean_cache=='True':
   print '!!! Full clean of the cache !!!'
   craz()
   print '!!! Cache cleaned !!!'


# -> Specific Ciclad (fabric): set the url of the web server and the paths where the
# -> images are stored
# -----------------------------------------------------------------------------------
if onCiclad:
   # Create a directory: /prodigfs/ipslfs/dods/user/CESMEP/comparison
   # The atlas will be available in a self-consistent directory, containing the html and the figures.
   # This way it is possible to clean the cache without removing the figures.
   # It is also possible to copy the directory somewhere else (makes it transportable)
   # subdir = '/prodigfs/ipslfs/dods/user/CESMEP/comparison'
   from climaf import cachedir
   component = str.replace( str.replace( str.replace( index_name, '_'+opts.comparison, '' ), '.html',''), 'atlas_', '')
   subdir = '/prodigfs/ipslfs/dods/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component
   if not os.path.isdir(subdir):
      os.makedirs(subdir)
   else:
      os.system('rm -f '+subdir+'/*.png')
   alt_dir_name = "/thredds/fileServer/IPSLFS"+str.split(subdir,'dods')[1]
   root_url = "https://vesg.ipsl.upmc.fr"



# -> Specif TGCC: Creation du repertoire de l'atlas, ou nettoyage de celui-ci si il existe deja
# -----------------------------------------------------------------------------------
if atTGCC:
   component_season = str.replace( str.replace( str.replace(index_name,'.html',''), 'atlas_', ''), '_'+opts.comparison, '' )
   CWD = os.getcwd()
   if '/dsm/' in CWD: wspace='dsm'
   if '/gencmip6/' in CWD: wspace='gencmip6'
   scratch_alt_dir_name = '/ccc/scratch/cont003/'+wspace+'/'+user_login+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component_season+'/'
   work_alt_dir_name = scratch_alt_dir_name.replace('scratch', 'work')
   root_url = "https://vesg.ipsl.upmc.fr"
   alt_dir_name = scratch_alt_dir_name
   if not os.path.isdir(scratch_alt_dir_name):
      os.makedirs(scratch_alt_dir_name)
   else:
      os.system('rm -f '+scratch_alt_dir_name+'/*.png')

# -> Specif TGCC: Copy the empty.png image in the cache
# -----------------------------------------------------------------------------------
if atTGCC:
   from climaf import cachedir
   if not os.path.isdir(cachedir):
      os.makedirs(cachedir)
   if not os.path.isfile(cachedir+'/Empty.png'):
      cmd = 'cp '+cpath+'/plot/Empty.png '+cachedir
      print cmd
      os.system(cmd)


# -> Differentiate between Ciclad and TGCC -> the first one allows working
# -> directly on the dods server ; the second one needs to go through a dods_cp 
# -> That's why we set a 'dirname' on TGCC (copied with dods_cp afterwards)
# -> and an 'altdir' on Ciclad
# -----------------------------------------------------------------------------------
if atTGCC:   alternative_dir = {'dirname': scratch_alt_dir_name}
if onCiclad: alternative_dir = {'dirname' : subdir}



# -- Set the verbosity of CliMAF (minimum is 'critical', maximum is 'debug',
# -- intermediate -> 'warning')
# -----------------------------------------------------------------------------------
clog(verbose)



# -- Control the 'force' option (by default set to None)
# -----------------------------------------------------------------------------------
for model in models:
    if 'force' not in model:
        model.update({'force': None})


# -- Print the models
# -----------------------------------------------------------------------------------
print '==> ----------------------------------- #'
print '==> Working on models:'
print '==> ----------------------------------- #'
print '  '
for model in models:
    for key in model:
        print '  '+key+' = ',model[key]
    print '  --'
    print '  --'



# -- Define the path to the main C-ESM-EP directory:
# -----------------------------------------------------------------------------------
rootmainpath = str.split(os.getcwd(),'C-ESM-EP')[0] + 'C-ESM-EP/'
if os.path.isfile(rootmainpath+'main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath
if os.path.isfile(rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/'


# -----------------------------------------------------------------------------------
# --   End PART 1 
# -- 
# -----------------------------------------------------------------------------------






# -----------------------------------------------------------------------------------
# --   PART 2: Build the html
# --              - the header
# --              - and the sections of diagnostics:
# --                 * Atlas Explorer
# --                 * and anything you want!
# --                   This is your working space.
# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
# - Init html index
# -----------------------------------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)







# ----------------------------------------------
# --                                             \
# --  Atlas Explorer                              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------



# ---------------------------------------------------------------------------------------- #
# -- Plotting the maps of the Atlas Explorer                                            -- #
if do_atlas_explorer:
    print '---------------------------------'
    print '-- Processing Atlas Explorer   --'
    print '-- do_atlas_explorer = True    --'
    print '-- atlas_explorer_variables =  --'
    print '-> ',atlas_explorer_variables
    print '--                             --'
    # -- Period Manager
    if not use_available_period_set:
       Wmodels = period_for_diag_manager(models, diag='atlas_explorer')
       apply_period_manager = True
    else:
       Wmodels = copy.deepcopy(Wmodels_clim)
       apply_period_manager = False
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = None
    index += section_2D_maps(Wmodels, reference, proj, season, atlas_explorer_variables,
                             'Atlas Explorer', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             add_line_of_climato_plots=add_line_of_climato_plots,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager, thumbnail_size=thumbN_size)
    if atlas_explorer_climato_variables:
       index += section_climato_2D_maps(Wmodels, reference, proj, season, atlas_explorer_climato_variables,
                             'Atlas Explorer Climatologies', domain=domain, custom_plot_params=custom_plot_params,
                             add_product_in_title=add_product_in_title, safe_mode=safe_mode,
                             alternative_dir=alternative_dir, custom_obs_dict=custom_obs_dict,
                             apply_period_manager=apply_period_manager, thumbnail_size=thumbN_size)




# ----------------------------------------------
# --                                             \
# --  Add your own CliMAF diagnostic              \
# --                                              /
# --                                             /
# --                                            /
# ---------------------------------------------


# ---------------------------------------------------------------------------------------- #
# -- Your own diagnostic script                                                         -- #
# -- This section is a copy of the previous section; it is a good example               -- #
# -- of how to add your own script/diagnostic                                           -- # 
# -- The section starting with comments with ==> at the beginning are mandatory to      -- #
# -- build a section in the C-ESM-EP. The comments starting with /// identify code that -- #
# -- is specific to the diagnostic presented here.                                      -- #
if do_my_own_climaf_diag:
    #
    # ==> -- Open the section and an html table
    # -----------------------------------------------------------------------------------------
    index += section("My own CliMAF diagnostic", level=4)
    #
    # ==> -- Control the size of the thumbnail -> thumbN_size
    # -----------------------------------------------------------------------------------------
    if thumbnail_size:
       thumbN_size = thumbnail_size
    else:
       thumbN_size = thumbnail_size_global
    #
    # ==> -- Open the html line with the title
    # -----------------------------------------------------------------------------------------
    index += open_table()
    line_title = 'Diag #1 = amplitude of the annual cycle'
    index+=start_line(line_title)
    #
    # ==> -- Apply the period_for_diag_manager (not actually needed here)
    # -----------------------------------------------------------------------------------------
    Wmodels = copy.deepcopy(models)
    #
    # -- Define plot parameters per variable -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_plot_params = dict(
       tas = dict(contours=1, min=0, max=60, delta=5, color='precip3_16lev'),
       pr  = dict(contours=1, min=0, max=30, delta=2, color='precip_11lev', scale=86400.),

    )
    #
    # -- Loop on the variables defined in my_own_climaf_diag_variables -> better if in the params file
    # -----------------------------------------------------------------------------------------
    my_own_climaf_diag_variables = ['tas', 'pr']
    for variable in my_own_climaf_diag_variables:
        #
        # -- Loop on the models
        # -----------------------------------------------------------------------------------------
        for model in Wmodels:
            #
            # -- preliminary step = copy the model dictionary to avoid modifying the dictionary
            # -- in the list models, and add the variable
            # -----------------------------------------------------------------------------------------
            wmodel = model.copy() # - copy the dictionary to avoid modifying the original dictionary
            wmodel.update(dict(variable=variable)) # - add a variable to the dictionary with update
            #
            # ==> -- Apply frequency and period manager
            # -----------------------------------------------------------------------------------------
            # ==> -- They aim at finding the last SE or last XX years available when the user provides
            # ==> -- clim_period='last_SE' or clim_period='last_XXY'...
            # ==> -- and get_period_manager scans the existing files and find the requested period
            # ==> -- !!! Both functions modify the wmodel so that it will point to the requested period
            frequency_manager_for_diag(wmodel, 'clim')
            get_period_manager(wmodel)
            #
            # /// -- Get the dataset and compute the annual cycle
            # -----------------------------------------------------------------------------------------
            dat = annual_cycle( ds(**wmodel) )
            #
            # -- Compute the amplitude of the annual cycle (max - min)
            # -----------------------------------------------------------------------------------------
            amp = minus( ccdo(dat, operator='timmax'), ccdo(dat, operator='timmin') )
            #
            # /// -- Build the titles
            # -----------------------------------------------------------------------------------------
            title = build_plot_title(wmodel,None) # > returns the model name if project=='CMIP5'
            #                                         otherwise it returns the simulation name
            #                                         It returns the name of the reference if you provide
            #                                         a second argument ('dat1 - dat2')
            LeftString = variable
            RightString = build_str_period(wmodel)  # -> finds the right key for the period (period of clim_period)
            CenterString = 'Seas cyc. amplitude'
            #
            # -- Plot the amplitude of the annual cycle
            # -----------------------------------------------------------------------------------------
            plot_amp = plot(amp, title=title, gsnLeftString = LeftString, gsnRightString = RightString, gsnCenterString = CenterString,
                            **my_own_climaf_diag_plot_params[variable] )
            #
            # ==> -- Add the plot to the line
            # -----------------------------------------------------------------------------------------
            index += cell("",safe_mode_cfile_plot(plot_amp, safe_mode=safe_mode),
                          thumbnail=thumbN_size, hover=hover, **alternative_dir)
            #
        # ==> -- Close the line and the table for this section
        # -----------------------------------------------------------------------------------------
        index+=close_line() + close_table()




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
# -- On Ciclad we feed directly the cache located on the dods server
# -- and point at this web address.
# -- At TGCC we need to:
# --   - feed the cache on $SCRATCHDIR (set in your environment) and make a hard link in
# --     a target directory (alt_dir_name, based on the current working directory and
# --     subdir)
# --   - at the end of the atlas, we copy the target directory (alt_dir_name) on the
# --     $WORKDIR (work_alt_dir_name) before copying it on the dods with dods_cp
# --   - Eventually, we dods_cp the directory work_alt_dir_name
# --     on the /ccc/work/cont003/dods/public space

# -- Adding the compareCompanion JavaScript functionality to make a selection of images
if add_compareCompanion:
   index += compareCompanion()

index += trailer()
import os 
if alt_dir_name :
    #
    if onCiclad:
       outfile=subdir+"/"+index_name
       print 'outfile = ',outfile
       with open(outfile,"w") as filout : filout.write(index)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       print("index written as : "+outfile)
       print("Available at this address "+root_url+outfile.replace(subdir,alt_dir_name))
    #
    if atTGCC:
       # -- Ecriture du fichier html dans le repertoire sur scratch
       outfile=scratch_alt_dir_name+index_name
       with open(outfile,"w") as filout : filout.write(index)
       print("index actually written as : "+outfile)
       if not os.path.isdir(work_alt_dir_name):
          os.makedirs(work_alt_dir_name)
       else:
          print 'rm -rf '+work_alt_dir_name+'/*'
          os.system('rm -rf '+work_alt_dir_name+'/*')
       cmd1 = 'cp -r '+scratch_alt_dir_name+'* '+work_alt_dir_name
       print cmd1
       os.system(cmd1)
       #
       # Rajouter thredds si sur gencmip6
       # -- dods_cp du repertoire copie sur le work
       if 'gencmip6' in getcwd():
          public_space = '/ccc/work/cont003/thredds/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login
       if 'dsm' in getcwd():
          public_space = '/ccc/work/cont003/dods/public/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login
       cmd12 = 'rm -rf '+public_space+'/'+component_season
       print cmd12
       os.system(cmd12)
       cmd2 = 'dods_cp '+work_alt_dir_name+' '+public_space+'/'
       print cmd2
       os.system(cmd2)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       if 'gencmip6' in getcwd():
          print('Index available at : https://vesg.ipsl.upmc.fr/thredds/fileServer/work_thredds/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component_season+'/'+index_name)
       if '/dsm/' in getcwd():
          print('Index available at : https://vesg.ipsl.upmc.fr/thredds/fileServer/work/'+getuser()+'/C-ESM-EP/'+opts.comparison+'_'+user_login+'/'+component_season+'/'+index_name)

    #
else :
    with open(index_name,"w") as filout : filout.write(index)
    print("The atlas is ready as %s"%index_name)


# -----------------------------------------------------------------------------------
# --   End PART 3
# --
# -----------------------------------------------------------------------------------


# -- Systematically clean the cache
if routine_cache_cleaning:
   if not isinstance(routine_cache_cleaning,list): routine_cache_cleaning = [routine_cache_cleaning]
   for clean_args in routine_cache_cleaning:
       print 'clean_args = ',clean_args
       crm(**clean_args)

# -----------------------------------------------------------------------------------
# -- End of the atlas                                                                
# -----------------------------------------------------------------------------------

