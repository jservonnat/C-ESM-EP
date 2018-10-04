# -----------------------------------------------------------------------------------
# --
# -- Main driver of the PMP - C-ESM-EP solution to:
# --   - compute metrics on demand
# --   - on simulations that are pre-treated with CliMAF
# --   - on a list of variables
# --   - and display the results on parallel coordinates plots
# --   - with columns sorted respective to the first provided simulation
# --
# -- Author: jerome.servonnat at lsce.ipsl.fr
# --
# -----------------------------------------------------------------------------------

# -- Import modules
from CM_atlas import *
from climaf.site_settings import atTGCC, onCiclad
import os, copy, subprocess, shlex
from datetime import datetime
from shutil import copyfile
from getpass import getuser
from PMP_MG.PMP_MG_time_manager import build_metric_outpath, get_keys_for_PMP_MG, build_input_climatology_filename, pysed, frequency_manager_for_diag_type, period_for_diag_manager 

clog('debug')

# -- Define the path to the main C-ESM-EP directory:
# -----------------------------------------------------------------------------------
rootmainpath = str.split(os.getcwd(),'C-ESM-EP')[0] + 'C-ESM-EP/'
if os.path.isfile(rootmainpath+'main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath
if os.path.isfile(rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/main_C-ESM-EP.py'):
   main_cesmep_path = rootmainpath+str.split(str.split(os.getcwd(),'C-ESM-EP')[1],'/')[1]+'/'

# ------------------------------------------------------------------------------------------- #
# -- START PARAMETERS MANAGEMENT                                                           -- #

# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------
from optparse import OptionParser
desc="\n\nParallel coordinates of the PCMDI Metrics"
parser = OptionParser(desc) ; parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("-p", "--params",
                  help="Parameter file for the Coupled Model atlas (.py)",
                  action="store",default=None)
parser.add_option("--datasets_setup",
                  help="Name of the file containing the list of dictionaries describing the datasets",
                  action="store",default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store",default=None)
parser.add_option("--sort",
                  help="Sort the columns with the first experiment of the highlights list",
                  action="store",default='TRUE')
parser.add_option("--highlights_only",
                  help="Specify if you want to see only the highlighted models in the legend (TRUE or FALSE)",
                  action="store",default=None)
parser.add_option("--lwd_background",
                  help="Line Width for background",
                  action="store",default=None)
parser.add_option("--lwd_highlights",
                  help="Line Width for highlighted experiments",
                  action="store",default=None)
parser.add_option("--image_size",
                  help="Size of the PNG image width*height (ex: 1000*600)",
                  action="store",default=None)
parser.add_option("--legend_ratio",
                  help="Ratio of the width of the image used for the legend",
                  action="store",default=None)
parser.add_option("--CMIP5_highlights",
                  help="Names of the CMIP5 models that will nbe highlighted (separated with commas: IPSL-CM5A-LR,CNRM-CM5))",
                  action="store",default=None)
parser.add_option("--CMIP5_highlights_first",
                  help="If True, we sort the results on the first model provided as highlight. If False, we use the first dataset provided in datasets_setup.py .",
                  action="store",default=None)
parser.add_option("--outfigdir",
                  help="Output directory for the figures",
                  action="store",default=None)
parser.add_option("--CMIP5_colors",
                  help="colors for the lines of the CMIP5 models",
                  action="store",default=None)
parser.add_option("--root_outpath",
                  help="Root of the output directory for the climatologies (netcdf files) used by the PMP to compute the metrics",
                  action="store",default=None)
parser.add_option("--reference",
                  help="Choose the reference against which you want the metrics: defaultReference, alternate1, ...",
                  action="store",default=None)
parser.add_option("--ref_parallel_coordinates",
                  help="Choose between CMIP5 and AMIP (results that will be used as background)",
                  action="store",default=None)
parser.add_option("--reference_data_path",
                  help="Path to a directory with the results that will be used as background for the plot",
                  action="store",default=None)
parser.add_option("--metrics_table",
                  help="Choose between Atmosphere and Ocean",
                  action="store",default=None)


(opts, args) = parser.parse_args()


# -- Parameters Level 0/ Default values for the parameters
# --------------------------------------------------------------------------------------------
datasets_setup         = "datasets_setup.py"
comparison             = None
image_size             = None
legend_ratio           = None
sort                   = 'TRUE'
#colors                 = None
CMIP5_colors           = []
CMIP5_highlights       = []
highlights_only        = "FALSE"
CMIP5_highlights_first = True
lwd_background         = 2
lwd_highlights         = 6
root_outpath           = None # -- For the links to the climatologies
force_compute_metrics  = False
reference              = None # -- defaultReference, alternate1...
template_paramfile_dir = '/home/jservon/Evaluation/PCMDI-MP/template_param_file'
rm_tmp_paramfile       = False
obs_data_path          = '/data/jservon/Evaluation/ReferenceDatasets/PMP_obs/obs'
outfigdir              = None
ref_parallel_coordinates = 'CMIP5'
reference_data_path      = None
metrics_table            = 'Atmosphere'
add_period_to_simname    = True
# - Palette that will be used by the R script 
#colorpalette = ['dodgerblue3','orangered','green','dodgerblue4','firebrick3','yellow1','royalblue','deepskyblue','mediumseagreen','violetred2','mediumturquoise','cadetblue','brown2','chartreuse1','burlywood3','coral1','burlywood4','darkgoldenrod2','darkolivegreen3','darkgoldenrod4','darkorchid']
# Use --colors to override the colors of a subset of highlights, or directly edit colorpalette in the param file
#parallel_coordinates_script = '/home/jservon/Evaluation/PCMDI-MP/R_script/parallel_coordinates.R'
parallel_coordinates_script = main_cesmep_path+'share/scientific_packages/parallel_coordinates/parallel_coordinates.R'
index_filename_root = 'parallel_coordinates'


# -- Get the default parameters from default_atlas_settings.py -> Priority = default
# -----------------------------------------------------------------------------------
default_file = '/share/default/default_atlas_settings.py'
while not os.path.isfile(os.getcwd()+default_file):
    default_file = '/..'+default_file
execfile(os.getcwd()+default_file)


# -- Parameters Level 1/ Parameters from the parameter file (if there is one)
# --------------------------------------------------------------------------------------------
if opts.params:
   # -- Get the parameters from the parameter file
   execfile(opts.params)


# -- Parameters Level 2/ Parameters from the command line
# --------------------------------------------------------------------------------------------
comparison     = opts.comparison # Mandatory
if opts.datasets_setup: datasets_setup = opts.datasets_setup
if opts.image_size:     image_size     = opts.image_size
if opts.legend_ratio:   legend_ratio   = opts.legend_ratio
if opts.sort:           sort           = opts.sort
if opts.CMIP5_colors:         CMIP5_colors         = opts.CMIP5_colors
if opts.CMIP5_highlights:      CMIP5_highlights = str.split(opts.CMIP5_highlights,',')
if opts.highlights_only: highlights_only = opts.highlights_only
if opts.lwd_background:  lwd_background  = opts.lwd_background
if opts.lwd_highlights:  lwd_highlights  = opts.lwd_highlights
if opts.outfigdir:       outfigdir       = opts.outfigdir
if opts.root_outpath:    root_outpath    = opts.root_outpath
if opts.reference:       reference       = opts.reference
if opts.ref_parallel_coordinates: ref_parallel_coordinates = opts.ref_parallel_coordinates
if opts.reference_data_path:      reference_data_path = opts.reference_data_path


# -- Parameters Level 3/ Build some variables depending on the values of the parameters
# --------------------------------------------------------------------------------------------
# -- Output directory for the figures
user_login = ( str.split(os.getcwd(),'/')[4] if getuser()=='fabric' else getuser() )
if not outfigdir:
    if onCiclad:
       outfigdir = '/prodigfs/ipslfs/dods/'+getuser()+'/C-ESM-EP/'+comparison+'_'+user_login+'/ParallelCoordinates_Atmosphere/'
       if not os.path.isdir(outfigdir):
          os.makedirs(outfigdir)
       else:
          os.system('rm -f '+outfigdir+'*.png')

# -- Reference (results displaid in background)
if not reference_data_path:
  if ref_parallel_coordinates in 'CMIP5':
    reference_data_path = '/data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016'
    #reference_data_path = main_cesmep_path+'scientific_packages/PCMDI_CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016'#'/data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016'
  if ref_parallel_coordinates in 'AMIP':
    reference_data_path = '/data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-amip/03Nov2016'

#if not vars:
if metrics_table=='Atmosphere':
   groups = ['LMDZ_PCMDI']
   if not vars:
      vars = ['pr','prw','tas','uas','vas','psl','rlut','rsut','rlutcs','rsutcs','huss',
              'ta_850','ta_200','ua_850','ua_200','va_850','va_200','zg_500','hus_850',
              'rtnetcre','rstcre','rltcre',
              'tauu','tauv']
   #
if metrics_table=='Ocean':
   groups = ['NEMO_PCMDI','NEMO_VertLevels']
   if not vars:
      vars = ['sos','tos','wfo','zos','mldpt',
             'tod_50','tod_100','tod_500','tod_1000',
             'sod_50','sod_100','sod_500','sod_1000']


# -- END PARAMETERS MANAGEMENT                                                             -- #
# ------------------------------------------------------------------------------------------- #




# -> Faire une boucle par datasets =>
#      recuperer simulation, model et experiment (si ils sont definis)
#      recuperer la frequency: 'seasonal' par defaut, 'monthly' possible
#      recuperer la periode, et analyser (last_10SE, list...)
#         => construire la liste de periodes correspondant a la requete
#      A partir de ces elements, faire une requete dans la base pour voir ce qui existe:
#         par dataset/period
#         => on met de cote tout ce qu'on a pas
#             - si frequency='seasonal', on lance le calcul avec run_SE...py
#             - si frequency='monthly', on lance le calcul avec climaf_pmp
#         => on verifie si on a pas deja les fichiers json dans les repertoires (faire une fonction pour construire le path)
#         => on enleve ce qu'on a deja
#         => Et on finit par faire une requete de calcul avec le script approprie
#         ...
#         => on recupere les paths vers les fichiers json
#         => et on depose dans la base
#         ...
#         => On appelle a nouveau la base
#         => On fait le plot avec le MG
#         => et on met le html dans l'arborescence 


# -- BLOCK 1 -------------------------------------------------------------------
# - Boucle sur models
# !!! Il faut constituer:
#   => Une liste de json que l'on donnera aux scripts de plot PCMDI
#   => un repertoire avec les json pour les deposer dans la base
#   => construire les requetes model/experiment/simulation/period pour faire une requete par dataset dans le MG
subdir = datetime.today().strftime("%Y-%m-%d")


# -- Get datasets_setup.py
#execfile(datasets_setup)
datasets_setup_available_period_set_file = str.replace(datasets_setup,'.py','_available_period_set.py')
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
else:
   execfile(datasets_setup)
   use_available_period_set = False

# -- Fix (in case)
if reference=='default': reference='defaultReference'

# - Si l'utilisateur donne un PMP_MG_clim_period qui est une liste de periodes a la mail, on reconstruit
#   une liste models (sans recherche de l'existant)
#models = split_periods_in_models(models)
#def period_manager_PMP_MG(models, diag='', diag_type='clim', testvar=None):
#    Wmodels = period_for_diag_manager(copy.deepcopy(models), diag=diag)
#    NewList_models = []
#    for Wmodel in Wmodels:
#        model = Wmodel.copy()
#        if testvar:
#            model.update(dict(variable=testvar))
#        else:
#            print '----> No testvar provided in period_manager_PMP_MG'
#        frequency_manager_for_diag_type(model, diag_type=diag_type)
#        wmodel = get_period_manager(model)
#        if isinstance(wmodel,dict):
#            NewList_models.append(wmodel)
#        if isinstance(wmodel,list):
#            NewList_models = NewList_models + wmodel
#
#    return NewList_models


if use_available_period_set:
   Wmodels = copy.deepcopy(Wmodels_clim)
else:
   #    -> On peut donc definir une liste de variable => la premiere variable de la liste
   #       est prise pour trouver la periode avec time_manager => On met a jour la liste Wmodels
   #Wmodels = period_manager_PMP_MG(models, diag='PMP_MG', diag_type='clim', testvar=vars[0])
   Wmodels = period_for_diag_manager(models, diag='clim')
   for dataset_dict in Wmodels:
       dataset_dict.update(dict(variable='tas'))
       frequency_manager_for_diag(dataset_dict, diag='clim')
       get_period_manager(dataset_dict)
       dataset_dict.pop('variable')

print '===========> Wmodels ', Wmodels


# -- creer la liste CMIP5_highlights et CMIP5_colors => issu de CMIP5_highlights de 
CMIP5_names = []
for elt in CMIP5_highlights:
    CMIP5_names.append(elt['model'])
    CMIP5_colors.append(elt['color'])


print 'CMIP5_highlights = ',CMIP5_highlights
print 'CMIP5_colors = ', CMIP5_colors
print 'CMIP5_names = ', CMIP5_names

import copy
testWmodels = copy.deepcopy(Wmodels)
print 'testWmodels before = ',testWmodels

# -- Si on a des CMIP5_names definis dans le params, ils s'accompagnent d'une couleur chacun
# -- Si on a des datasets CMIP5 definis depuis le datasets_setup, soit:
# --   - on utilise la couleur associee
# --   - on attribue une couleur prise dans colorpalette qui ne soit pas encore attribuee

for model in testWmodels:
    print '---'
    print 'After filtering = ', model
    print '---'

Wmodels = copy.deepcopy(testWmodels)


# -- END BLOCK 1 -------------------------------------------------------------------



# -- BLOCK 2 -------------------------------------------------------------------
#    -> A partir de cette periode (et de la definition du dataset), on va:
#         - verifier, dataset par dataset, et variable par variable, si la metrique est disponible dans la base;
#            -> Si non, on stocke la liste des variables qu'il manque pour cette simu
#               (trouver comment, probablement dans une liste)
# -- Loop on datasets

metric_json_filename = '_2.5x2.5_esmf_linear_metrics.json'

# -- Cette liste va recevoir les json files qui sont deja disponibles, mais pas encore deposes sur la base
# --> On mergera cette liste avec la liste des metriques que l'on viendra de calculer pour faire un 
#     repertoire temporaire tmp_hermes, puis les deposer dans la base
ok_json_files = []

if not root_outpath:
    if atTGCC: root_outpath = '${SCRATCHDIR}'
    if onCiclad: root_outpath = '/prodigfs/ipslfs/dods/'+getuser()

# -- Check if the tmp_hermes directory exists; if not, create it. If yes, clean it.
tmp_hermes_dir = root_outpath+'/PMP_OUT/metrics_results/tmp_hermes'
if not os.path.isdir(tmp_hermes_dir):
    os.makedirs(tmp_hermes_dir)
else:
    cmd = 'rm -rf '+tmp_hermes_dir+'/*'
    print cmd
    os.system(cmd)

# ---------------------------------------------------------------- #
# -- Verification de l'existant: boucles sur Wmodels
# -- et sur vars
# ---------------------------------------------------------------- #
for wmodel in Wmodels:
    #
    print '---'
    print '---'
    print '---> Working on dataset ',wmodel
    print '---> on variables:',vars
    print '---'
    print '---'
    # -- Loop on variables
    wvars = []
    for var_dict in vars:
        #
        if isinstance(var_dict,dict):
           var = var_dict['variable']
        else:
           var = var_dict
        if 'Ok':
            # Searching for the json file in the tree
            found = False
            for group in groups:
                check_json = build_metric_outpath(wmodel, group, root_outpath=root_outpath, subdir='*')+'/'+str.replace(var,'_','-')+metric_json_filename
                print 'check_json = ',check_json
                check = glob.glob(check_json)
                print 'check = ',check
                if len(check)==0:
                    print "==> Didn't find any json files matching the request :",check
                else:
                    # -- On enleve les fichiers qui sont dans tmp_hermes
                    #for tmpfile in check:
                    #    if 'tmp_hermes' in tmpfile: check.remove(tmpfile)
                    if len(check)==1:
                        print '==> json file exists :',check[0]
                        print '==> Stored to put in database --'
                        if check[0] not in ok_json_files:
                            ok_json_files.append(check[0])
                        found = True
                    else:
                        print '==> Found multiple json files matching the request :',check
                        print '==> Check the "not_defined" keys and specify them'
                        print '==> We remove the files to avoid mixing results, and recompute the metrics'
                        for check_file in check: os.remove(check_file)
                        found = False
            # -- If we didn't find it, we store the variable in the list of variables to compute
            #    the metrics with the PMP
            if not found:
                print '----> Need to compute the metrics for variable ',var_dict
                wvars.append(var_dict)
    # -- And now, we add the list of variables for which we have to compute the metrics with the PMP to wmodel
    wmodel.update( dict(metrics_variables=wvars) )
    if 'variable' in wmodel: wmodel.pop('variable')
    #


# -- BLOCK 3 -------------------------------------------------------------------
def run_CliMAF_PMP(models, group=None, variables=None, root_outpath=None,
                   obs_data_path = obs_data_path,
                   reference = 'default', targetGrid='2.5x2.5', force_compute_metrics=False,
                   template_paramfile_dir=template_paramfile_dir,
                   tmp_paramfiles_outpath='.', subdir=None, rm_tmp_paramfile=True
                  ):
    #
    # -- List of metrics files used by the PCMDI plot scripts
    metric_files_list = []
    #
    # -- Variables
    vars=variables
    #
    # -- Copy the initial models list
    Wmodels = copy.deepcopy(models)#period_for_diag_manager(models, diag='SE') #copy.deepcopy(models)
    #
    for model_dict in Wmodels:
        #
        # 0/ We start by translating the period provided by the user in models,
        #    like the last_SE, last_100yr, list of periods...
        #    and we return a new list of dataset dictionaries
        # 
        wmodel = model_dict.copy()
        
        # --> ($institute_id)
        if 'institute_id' in model_dict:
            institute_id = model_dict['institute_id']
        else:
            if model_dict['project'] in ['IGCM_OUT','LMDZ','NEMO']:
                institute_id = 'IPSL'
            else:
                institute_id = 'institute_id_not_defined'
        #
        # -- Dealing with the group related sets of variables
        if 'metrics_variables' in wmodel:
            vars = wmodel['metrics_variables']
        
        # -- Prepare the output directory for the temporary netcdf files that will be used
        # -- to compute the metrics (root_outpath can be None)
        metrics_output_path = build_metric_outpath(wmodel, group=group, subdir=subdir, root_outpath=root_outpath)
        if not os.path.isdir(metrics_output_path):
            os.makedirs(metrics_output_path)
        tmp_root = str.split(metrics_output_path,'PMP_OUT')[0]
        input_climatologies_dir = tmp_root+'/PMP_OUT/input_climatologies'
        if not os.path.isdir(input_climatologies_dir):
            os.makedirs(input_climatologies_dir)
        #
        # -- Verification de l'existant
        if force_compute_metrics:
            print '!! Force recomputing metrics !!'
            w_variables = vars
        else:
            w_variables = []
            for variable in vars:
                if isinstance(variable,dict):
                   #w_variable = variable.copy()
                   w_variable = variable['variable']
                   #w_variable_dict['variable'] = w_variable
                else:
                   w_variable = variable
                w_variable = str.replace(w_variable,'_','-')
                metric_json_file = metrics_output_path+'/'+w_variable+'_'+targetGrid+'_esmf_linear_metrics.json'
                if not os.path.isfile(metric_json_file):
                    print 'Missing ',metric_json_file
                    w_variables.append(variable)
                else:
                    print 'Already have ',metric_json_file
        
        # -- Si il y a des metriques a calculer...
        str_vars_list = []
        if w_variables:
            for var in w_variables:
                # -- Name of the temporary file (hard link)
                wmodel_dict = wmodel.copy()
                if isinstance(var,dict):
                   #w_variable = variable.copy()
                   strvar = var['variable']
                   wvar = str.split(var['variable'],'_')[0]
                   if 'project_specs' in var:
                      if wmodel_dict['project'] in var['project_specs']:
                         wmodel_dict.update(var['project_specs'][wmodel_dict['project']])
                   
                   #w_variable_dict['variable'] = w_variable
                else:
                   wvar = str.split(var,'_')[0]
                   strvar = var
                #
                #wvar = str.split(var,'_')[0]
                wmodel_dict.update(dict(variable=wvar))
                if wmodel_dict['project']=='CMIP5':
                   if not table in wmodel_dict:
                      wmodel_dict.update(dict(table='Amon'))
                if wmodel_dict['project']=='CMIP6':
                   if not 'table' in wmodel_dict:
                      wmodel_dict.update(dict(table='Amon'))
                   if not 'grid' in wmodel_dict:
                      wmodel_dict.update(dict(grid='gr'))
                # -- Fix!!! for tas IGCM_OUT we use ATM
                if wmodel['project']=='IGCM_OUT':
                   if not 'DIR' in wmodel_dict:
                      wmodel_dict.update(dict(DIR='ATM'))
                target_filename = build_input_climatology_filename(wmodel_dict)
                #
                # -- Do the hardlink (and all necessary alias, computation of derived variable behind...)
                model_ds = ds(**wmodel_dict)
                #
                # -- Vertical interpolation for LMDz
                #if 'LMDZ' in model_ds.kvp['project'] and wvar in ['ua','va','ta','zg']:
                #    model_ds_pres = ds(variable='pres', **model_dict)
                #    model_ds = ml2pl(model_ds,model_ds_pres)
                #
                #
                # -- If the variable is available for the simulation
                try:
                    if model_ds.frequency in ['monthly', '1M', 'MO']:
                        wmodel_ds = annual_cycle(model_ds)
                    else:
                        wmodel_ds = model_ds
                    cdrop(wmodel_ds)
                    print cfile(wmodel_ds,
                                target = input_climatologies_dir+'/'+target_filename,
                                ln = True)
                    if wmodel_dict['project']=='MGV':
                        print 'Rename time axis for MGV simulations ==> '
                        cmd = 'ncrename -v t_ave_02592000,time -d t_ave_02592000,time '+input_climatologies_dir+'/'+target_filename
                        print cmd
                        os.system(cmd)
                    # -- build the list of vars to be used for the parameter file
                    str_vars_list.append(strvar)
                except:
                    w_variables.remove(var)
                #
                # --> The files are now ready in the tmp directory (and in the CliMAF cache)
                metric_files_list.append(metrics_output_path+'/'+str.replace(strvar,'_','-')+'_'+targetGrid+'_esmf_linear_metrics.json')

            ### 2.1/ Copy the template parameter file

            # -- Path to the template file
            template_paramfile = template_paramfile_dir+'/input_parameters_CliMAF2PMP.py'
            # -- Construct the name of the temporary file with unique string (time in microseconds)
            delay = datetime.utcnow() - datetime(2015,1,1)
            additionnal = str(delay.microseconds)
            # -- we put the tmp paramfiles in the directory of the climatologies
            tmp_paramfiles_dir = tmp_paramfiles_outpath+'/tmp_paramfiles/'
            if not os.path.isdir(tmp_paramfiles_dir): os.makedirs(tmp_paramfiles_dir)
            tmp_paramfile = tmp_paramfiles_dir+os.path.basename(template_paramfile).replace('.py','_'+additionnal+'.py')
            print '==> Copying ',template_paramfile
            print '==> to :',tmp_paramfile
            copyfile(template_paramfile,tmp_paramfile)

            ### 2.2/ Edit the temporary parameter file
            file_pattern = input_climatologies_dir+'/'+target_filename.replace(wvar+'.nc','')

            # --> Variables
            str_vars = ','.join(str_vars_list)
            
            keys_wmodel = get_keys_for_PMP_MG(wmodel)
            # -- Fix when period='fx'
            if 'period' in keys_wmodel:
               if keys_wmodel['period']=='fx':
                  if 'clim_period' in keys_wmodel: keys_wmodel['period'] = keys_wmodel['clim_period']

            pysed(tmp_paramfile, '@file_pattern', file_pattern)
            pysed(tmp_paramfile, '@model', keys_wmodel['model'])
            pysed(tmp_paramfile, '@experiment', keys_wmodel['experiment'])
            pysed(tmp_paramfile, '@simulation', keys_wmodel['simulation'])
            pysed(tmp_paramfile, '@institute_id', institute_id)
            pysed(tmp_paramfile, '@reference', reference)
            pysed(tmp_paramfile, '@targetGrid', targetGrid)
            pysed(tmp_paramfile, '@obs_data_path', obs_data_path)
            pysed(tmp_paramfile, '@metrics_output_path', metrics_output_path)
            pysed(tmp_paramfile, '@str_vars', str_vars)
            pysed(tmp_paramfile, '@period', keys_wmodel['period'])
            pysed(tmp_paramfile, '@login', keys_wmodel['login'])
            print ''
            
            print ''
            print '-- tmp parameter file is ready to be used by the PMP --'
            print '-> '+tmp_paramfile


            ## Run the PMP with the edited parameter file

            cmd = 'pcmdi_metrics_driver.py -p '+tmp_paramfile
            print cmd

            p=subprocess.Popen(shlex.split(cmd))
            p.communicate()
            if rm_tmp_paramfile: os.system('rm -f '+tmp_paramfile+'*')
            # 
        print 'The results of the PMP are stored in :'
        print str.split(metrics_output_path,'raw')[0]+'raw'
        #        
        #
    # -- Renvoyer la liste des fichiers jsons => pour utilisation pour plot
    return metric_files_list

# Pour le depot dans la base
#metric_files_list = run_CliMAF_PMP(Wmodels, group=groups[0], variables=None,
metric_files_list = run_CliMAF_PMP(Wmodels, group=groups[0], variables=vars,
                                   root_outpath=root_outpath, force_compute_metrics = False,
                                   subdir=subdir, rm_tmp_paramfile=rm_tmp_paramfile)


# -- END BLOCK 3 ---------------------------------------------------------------



# -- BLOCK 4 -------------------------------------------------------------------
# On prend la metrics_files_list
# et on concatene avec ok_json_files
# On fait
requested_json_files = metric_files_list + ok_json_files

print 'ok_json_files = ',ok_json_files
print 'metric_files_list = ', metric_files_list
print 'requested_json_files = ', requested_json_files


os.system('rm -rf '+tmp_hermes_dir)
files_in_tmp_hermes = []
for path_filename in requested_json_files:
    print path_filename
    if os.path.isfile(path_filename):
        # -- Clean up the files that are empty of results
        if os.path.getsize(path_filename)<5000:
            os.system('rm -f '+path_filename)
        else:
            # -- Make the link between the list of files and the tmp_hermes subdirectory
            subdir = str.split( str.split(path_filename, 'metrics_results/')[1], '/')[0]
            link_path_filename = tmp_hermes_dir + str.split(path_filename,subdir)[1]
            link_path = os.path.dirname(link_path_filename)
            print link_path
            if not os.path.isdir(link_path): os.makedirs(link_path)

            cmd = 'ln -s '+path_filename+' '+link_path_filename
            print cmd
            os.system(cmd)
            files_in_tmp_hermes.append(link_path_filename)

# -- END BLOCK 4 ---------------------------------------------------------------




# -- BLOCK 5 -------------------------------------------------------------------
path_for_pmp_plot = [] # -- We store the paths to the metrics
for wmodel in Wmodels:
    print 'wmodel in block 5 : ',wmodel
    for key in wmodel:
        if wmodel[key]=='*': wmodel[key]=key+'_not_defined'
    if 'period' in wmodel:
       if wmodel['period']=='fx':
          if 'clim_period' in wmodel: wmodel['period']=wmodel['clim_period']
    #      
    tmp_path = build_metric_outpath(wmodel, group=groups[0], subdir='tmp_hermes', root_outpath=root_outpath)
    print 'tmp_path = ', tmp_path
    for file_hermes in files_in_tmp_hermes:
        if tmp_path in file_hermes and tmp_path not in path_for_pmp_plot:
            print '-> This goes in path_for_pmp_plot => tmp_path = ',tmp_path,' ; file_hermes = ',file_hermes
            path_for_pmp_plot.append(tmp_path)
        else:
            print '-> Rejected: not in path_for_pmp_plot => tmp_path = ',tmp_path,' ; file_hermes = ',file_hermes
print 'path_for_pmp_plot = ',path_for_pmp_plot


# -- END BLOCK 5 ---------------------------------------------------------------




# -- BLOCK 6 -------------------------------------------------------------------
# -- Test data sets
test_data_path = ','.join(path_for_pmp_plot)

print 'test_data_path 1 = ',test_data_path

# -- Customization
from CM_atlas import build_plot_title
customnames = []
correct_metric_path_list = []
colors=[]
i = 0
for model in Wmodels:
    customname = str.replace(build_plot_title(model, None),' ','_')
    if add_period_to_simname:
      if 'period' in model: wperiod=model['period']
      #if 'clim_period' in model: wperiod=model['clim_period']
      if 'clim_period' in model:
         wperiod=model['clim_period']
         if 'last' in wperiod or 'first' in wperiod: wperiod=model['period']
      if wperiod not in customname: customname = customname+'_'+wperiod
    if customname not in customnames:
       customnames.append(customname)

colors = colors_manager(Wmodels,cesmep_python_colors,colors_list=CMIP5_colors,method='start_with_colors_list')

print 'colors after colors_manager = ',colors

# -- Add the colors of the CMIP5 highlights, either before or after the simulations in datasets_setup
if CMIP5_highlights_first:
   str_highlights = ','.join(CMIP5_names + customnames)
else:
   str_highlights = ','.join(customnames + CMIP5_names)


colors = ','.join(colors)

# -- END BLOCK 6 ---------------------------------------------------------------




# -- BLOCK 7 -------------------------------------------------------------------
cmd_parallel_coordinates = 'Rscript '+parallel_coordinates_script+' --test_data_path '+test_data_path+' --reference_data_path '+reference_data_path
print 'reference_data_path = ',reference_data_path
print 'cmd_parallel_coordinates avant = ', cmd_parallel_coordinates

if CMIP5_names:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --highlights '+str_highlights
else:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --highlights '+','.join(customnames)
if customnames:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --customnames '+','.join(customnames)
if lwd_background:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --lwd_background '+str(lwd_background)
if lwd_highlights:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --lwd_highlights '+str(lwd_highlights)
if highlights_only:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --highlights_only '+highlights_only
if reference:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --reference '+reference
if sort:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --sort '+sort
if legend_ratio:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --legend_ratio '+str(legend_ratio)
if colors:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --colors "'+str(colors)+'"'
if image_size:
    cmd_parallel_coordinates = cmd_parallel_coordinates+' --image_size '+image_size
print 'cmd_parallel_coordinates apres = ', cmd_parallel_coordinates




# ----------------------------------------------------------- \
# --                                                           \
# -- Building the html page                                    /
# --                                                          /
# ---------------------------------------------------------- /
from climaf.html import *

# -- Index name, and web address of the html file
# --------------------------------------------------------- 
index_name = outfigdir+index_filename_root+'_'+comparison+'.html'
alt_dir_name = '/thredds/fileServer/IPSLFS'+str.split(outfigdir,'dods')[1]
root_url = "https://vesg.ipsl.upmc.fr"


# -- Start the html file
# ---------------------------------------------------------
index = header(atlas_head_title, style_file=style_file)


# -- One dictionary corresponds with one section;
# -- One line per region/season, with all the statistics
if not metrics_sections:
   metrics_sections = [
       dict(statistic=['rms_xyt','rmsc_xy','bias_xy','cor_xy'],
            region=['global','land','ocean'],
            season=['ann'],
            section_name='Global, land, ocean on annual cycle and annual mean (rms_xyt, rmsc_xyt, bias_xy and cor_xy)'),
       dict(statistic=['rms_xy','rmsc_xy','bias_xy','cor_xy'],
            region=['NHEX', 'TROPICS', 'SHEX'],
            season=['ann','djf','mam','jja','son'],
            section_name='NHEX (90N-20N), TROPICS (20N-20S), and SHEX (20S-90S), annual and seasonal means (rms_xy, rmsc_xy, bias_xy and cor_xy)'),
   ]

# -- Loop on the sections of metrics
# ---------------------------------------------------------
if not do_four_seasons_parcor:
 for metrics_section in metrics_sections:
   index += section(metrics_section['section_name'], level=4)
   # -- Start a section
   for region in metrics_section['region']:
       for season in metrics_section['season']:
           # -- Open a line
           index+=start_line(region+' '+season)
           #
           # -- Loop on the statistics
           for statistic in metrics_section['statistic']:
               #figname = outfigdir+statistic+'_'+season+'_'+region+'_'+comparison+'_parallel_coordinates.png'
               delay = datetime.utcnow() - datetime(2015,1,1) ; nb = str(delay.microseconds)
               figname = statistic+'_'+season+'_'+region+'_'+comparison+'_parallel_coordinates_'+nb+'.png'
               cmd_parallel_coordinates_final = cmd_parallel_coordinates+' --figname '+outfigdir+figname+' --statistic '+statistic+' --region '+region+' --season '+season
               print 'statistic = ',statistic
               print 'region = ', region
               print 'season = ',season
               print ' --> cmd_parallel_coordinates_final for statistic = '+statistic+' region = '+region+' season = '+season
               print cmd_parallel_coordinates_final
               p=subprocess.Popen(shlex.split(cmd_parallel_coordinates_final))
               p.communicate()
               index+=cell("", figname, thumbnail="600*300", hover=False)#, dirname=outfigdir)
               # -- Add the plot to the html line using figname
           index += close_line() + close_table()
           # -- Close line
    # -- Close table
else:
 for metrics_section in metrics_sections:
   index += section(metrics_section['section_name'], level=4)
   # -- Start a section
   for region in metrics_section['region']:
           # -- Open a line
           index+=start_line(region)
           #
           # -- Loop on the statistics
           for statistic in metrics_section['statistic']:
               #figname = outfigdir+statistic+'_'+season+'_'+region+'_'+comparison+'_parallel_coordinates.png'
               delay = datetime.utcnow() - datetime(2015,1,1) ; nb = str(delay.microseconds)
               figname = statistic+'_tas_pr_4_seasons_'+region+'_'+comparison+'_parallel_coordinates_'+nb+'.png'
               cmd_parallel_coordinates_final = cmd_parallel_coordinates+' --figname '+outfigdir+figname+' --statistic '+statistic+' --region '+region
               print 'statistic = ',statistic
               print 'region = ', region
               print ' --> cmd_parallel_coordinates_final for statistic = '+statistic+' region = '+region
               print cmd_parallel_coordinates_final
               p=subprocess.Popen(shlex.split(cmd_parallel_coordinates_final))
               p.communicate()
               index+=cell("", figname, thumbnail="600*300", hover=False)#, dirname=outfigdir)
               # -- Add the plot to the html line using figname
           index += close_line() + close_table()
           # -- Close line
    # -- Close table


# -- Add the compareCompanion
index += compareCompanion()

# -- Close html 
index += trailer()
outfile=index_name
with open(outfile,"w") as filout : filout.write(index)
print("index actually written as : "+outfile)
print("may be seen at "+root_url+outfile.replace(outfigdir,alt_dir_name))

# -- END BLOCK 7 ---------------------------------------------------------------





