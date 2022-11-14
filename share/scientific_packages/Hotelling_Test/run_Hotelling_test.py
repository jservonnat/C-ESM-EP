# -----------------------------------------------------------------------------------
# --
# -- Main driver to perform the Hotelling test from the C-ESM-EP:
# --   - takes a comparison as argument
# --   - performs the Hotelling test presented in Servonnat et al. 2017 (Clim.Dyn) on the datasets
# --   - adds the results of the CMIP5 coupled or amip models
# --   - pre-treatments of the datasets with CliMAF (and use of the cache)
# --   - on a list of variables
# --   - and display the results in pdf plots => Then gathered in an html page with CliMAF
# --     (syntax of the figure names is hardcoded)
# --
# -- Author: jerome.servonnat at lsce.ipsl.fr
# --
# -----------------------------------------------------------------------------------

# --> The script will:
# -->   1/ prepare the annual cycle files for the list of variables and the list of datasets
# -->   2/ run the Hotelling test with main_Hotelling.R for all the variables and datasets
# -->      => the Hotelling-test.R script will save one json file per dataset and variable
# -->         The plot script will take as argument a list of json files and will scan the content and merge them. OK.
# -->   3/ Run the plot script = one variable per plot
# -->      The user need to be able to provide arguments to the plot script to customize the plot.

# -- Import CliMAF and the C-ESM-EP atlas modules
import json
from CM_atlas import *
from climaf.site_settings import atTGCC, onCiclad
import os
import copy
import subprocess
import shlex
from datetime import datetime
from shutil import copyfile
from getpass import getuser
from PMP_MG import *
from optparse import OptionParser
from climaf.chtml import *


clog('debug')

# ------------------------------------------------------------------------------------------- #
# -- START PARAMETERS MANAGEMENT                                                           -- #


# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------

desc = "\n\nParallel coordinates of the PCMDI Metrics"
parser = OptionParser(desc)
parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("-p", "--params",
                  help="Parameter file for the Coupled Model atlas (.py)",
                  action="store", default=None)
parser.add_option("--datasets_setup",
                  help="Name of the file containing the list of dictionaries describing the datasets",
                  action="store", default=None)
parser.add_option("--comparison",
                  help="Name of the comparison",
                  action="store", default=None)
parser.add_option("--plot_margins",
                  help="Margins of the plot (if you need to adjust)",
                  action="store", default=None)
parser.add_option("--image_size",
                  help="Size of the PDF image width*height in inches (ex: 10*6)",
                  action="store", default=None)
parser.add_option("--reference_results",
                  help="Choose between CMIP5 and AMIP (default is CMIP5) to add the results of CMIP5 or AMIP to the "
                       "plot",
                  action="store", default=None)
# parser.add_option("--CMIP5_colors",
#                  help="colors for the lines of the CMIP5 models",
#                  action="store",default=None)
parser.add_option("--common_grid",
                  help='Common grid used to regrid all the models and the references for the comparison (CDO grid)',
                  action="store", default='r180x90')
parser.add_option("--common_space",
                  help='Common EOFs space used to compute the Hotelling test; choose between CCM '
                       '(for Common Covariance Matrix) and CMR (Covariance Matrix of the Reference mean)',
                  action="store", default='CCM')
parser.add_option("-o", "--atlas_outdir",
                  help="Ouput directory for the atlas",
                  action="store", default=None)

(opts, args) = parser.parse_args()

# -- Parameters Level 0/ Default values for the parameters
# --------------------------------------------------------------------------------------------
datasets_setup = "datasets_setup.py"
comparison = None
plot_margins = None
image_size = None
reference_results = 'CMIP5'
# CMIP5_colors           = []
common_grid = opts.common_grid
common_space = opts.common_space
variables = ['hfls']  # , 'hfss']#, 'tauu', 'tauv']
force_compute = False
# - Palette that will be used by the R script
# colorpalette = ['dodgerblue3','orangered','green','dodgerblue4','firebrick3','yellow1','royalblue','deepskyblue',
# 'mediumseagreen','violetred2','mediumturquoise','cadetblue','brown2','chartreuse1','burlywood3','coral1','burlywood4',
# 'darkgoldenrod2','darkolivegreen3','darkgoldenrod4','darkorchid']


# -- Parameters Level 1/ Parameters from the parameter file (if there is one)
# --------------------------------------------------------------------------------------------
if opts.params:
    # -- Get the parameters from the parameter file
    execfile(opts.params)

# -- Parameters Level 2/ Parameters from the command line
# --------------------------------------------------------------------------------------------
comparison = opts.comparison  # Mandatory
if opts.datasets_setup:
    datasets_setup = opts.datasets_setup
if opts.image_size:
    image_size = opts.image_size
# if opts.CMIP5_colors:      CMIP5_colors      = opts.CMIP5_colors
if opts.reference_results:
    reference_results = opts.reference_results

# -- Parameters Level 3/ Build some variables depending on the values of the parameters
# --------------------------------------------------------------------------------------------
# -- Output directory for the figures
user_login = (str.split(os.getcwd(), '/')[4] if getuser() == 'fabric' else getuser())
if not opts.atlas_outdir:
    if onCiclad:
        outputrootdir = '/prodigfs/ipslfs/dods/' + getuser() + '/C-ESM-EP/'
        hotelling_outputdir = outputrootdir + 'Hotelling_test_results/'
        if not os.path.isdir(hotelling_outputdir):
            os.makedirs(hotelling_outputdir)
        atlas_outdir = outputrootdir + comparison + '_' + user_login + '/Hotelling_Test/'
        if not os.path.isdir(atlas_outdir):
            os.makedirs(atlas_outdir)
        else:
            os.system('rm -f ' + atlas_outdir + '*')

# -- END PARAMETERS MANAGEMENT                                                             -- #
# ------------------------------------------------------------------------------------------- #

# Les figures des resultats des statistics vont directement dans le repertoire de la comparaison:
# ils sont directement lies a la comparaison definie
# Les figures des CEOFs, et les json de resultats, peuvent eux aller dans le repertoire principal
# On stocke tous les resultats qui peuvent etre mis en communs dans une arborescence de l'utilisateur.

# 1. Repertoire racine des resultats de tests de Hotelling produits par l'utilisateur => dependant du calculateur
# outputrootdir = '/prodigfs/ipslfs/dods/jservon/C-ESM-EP/'

# 2. Racine de l'arborescece des resultats
# hotelling_outputdir = outputrootdir + 'Hotelling_test_results/'
# => /prodigfs/ipslfs/dods/jservon/C-ESM-EP/Hotelling_test_results/

# 3. Repertoire contenant les fichiers json de resultats
# hotelling_outputdir+ 'results_json_files/' => cree par Hotelling_routine.R
# => /prodigfs/ipslfs/dods/jservon/C-ESM-EP/Hotelling_test_results/results_json_files/

# 4. Repertoire contenant les figures de CEOFs
# hotelling_outputdir+ 'CEOFs_plots/variables*/*.pdf => cree par script de plot
# => /prodigfs/ipslfs/dods/jservon/C-ESM-EP/Hotelling_test_results/CEOFs_plots/variables*/*.pdf

# 5. Chemin vers le repertoire de l'atlas Hotelling de la comparaison
# atlas_outputdir = outputrootdir + 'comparison_jservon/Hotelling_Test/' + [figures*.pdf, atlas.html]
# => /prodigfs/ipslfs/dods/jservon/C-ESM-EP/comparison_jservon/Hotelling_Test/atlas.html

# => do the hard links manually!


# ------------------------------------------------------------------------------------------- #
# -- START INPUT DATASET MANAGEMENT

# -- Get datasets_setup.py => models
execfile(datasets_setup)

#    -> On peut donc definir une liste de variable => la premiere variable de la liste
#       est prise pour trouver la periode avec time_manager => On met a jour la liste Wmodels
Wmodels = period_for_diag_manager(models, diag='atlas_explorer')  # , diag_type='clim', testvar='hfls')

# comparison = 'all_CMIP5_coupled_models_historical'

# 1.1 Get the list of datasets (python dictionaries) from dataset_setup.py
if reference_results in ['CMIP5', 'AMIP']:
    common_keys = dict(project='CMIP5',
                       experiment='historical',
                       frequency='monthly',
                       realm='atmos',
                       period='1980-2005')
    if reference_results == 'CMIP5':
        common_keys.update(dict(experiment='historical'))
    if reference_results == 'AMIP':
        common_keys.update(dict(experiment='amip'))

    # -- First, scan the CMIP5 archive to find the available models
    dum = ds(variable='hfls', model='*', **common_keys)
    cmip5_models = []
    for dumfile in str.split(dum.baseFiles(), ' '):
        cmip5_models.append(str.split(dumfile, '/')[6])
    cmip5_models = list(set(cmip5_models))
    cmip5_models.remove('MIROC4h')

    # -- Add the CMIP5 models to the list...
    for cmip5_model in cmip5_models:
        reference_models.append(dict(model=cmip5_model, **common_keys))
    #
    # --> Used to highlight CMIP5 models...
    # for model in models: print 'model = ', model
    # for model in models:
    #    if model['model']=='IPSL-CM5A-LR': model.update(dict(R_color='dodgerblue3'))
    #    if model['model']=='IPSL-CM5A-MR': model.update(dict(color='blue'))
    #    if model['model']=='IPSL-CM5B-LR': model.update(dict(color='red'))
    #    if model['model']=='CNRM-CM5': model.update(dict(R_color='green3'))

# ----------------------------------------------------------- \
# --                                                           \
# -- Building the html page                                    /
# --                                                          /
# ---------------------------------------------------------- /

# -- Index name, and web address of the html file
# ---------------------------------------------------------
index_name = atlas_outdir + 'Hotelling_test_atlas_' + comparison + '.html'
# !!!! HARD CODED
alt_dir_name = '/thredds/fileServer/IPSLFS' + str.split(atlas_outdir, 'dods')[1]
root_url = "https://vesg.ipsl.upmc.fr"

# -- Start the html file
# ---------------------------------------------------------
index = header('Hotelling')
# !!!! HARD CODED


# -- Loop on the variables
for variable in variables:

    # --------------------------------------------------------------------------------------------- #
    # -->   1/ prepare the annual cycle files for the list of variables and the list of datasets
    # --------------------------------------------------------------------------------------------- #
    # -- Create the json file RefFiles.json
    RefFileName = 'reference_json_files/reference_files_GB2015_' + variable + '.json'

    if not os.path.isfile(RefFileName) or force_compute:
        # -- Get the reference files
        RefFiles = dict()
        # Scan the available files for variable
        listfiles = ds(project='ref_climatos', variable=variable)
        files = set(str.split(listfiles.baseFiles(), ' '))
        # -- list_of_ref_products is the predefined list of reference products of the GB2015 ensemble
        list_of_ref_products = ['OAFlux', 'NCEP', 'NCEP2', 'CORE2', 'FSU3', 'NOCS-v2', 'J-OFURO2', 'GSSTFM3', 'IFREMER',
                                'DFS4.3', 'TropFlux', 'DASILVA', 'HOAPS3', 'ERAInterim']
        for f in files:
            if get_product(f) in list_of_ref_products:
                refdat = regridn(ds(variable=variable, project='ref_climatos', product=get_product(f)),
                                 cdogrid=common_grid, option='remapdis')
                RefFiles.update({get_product(f): dict(variable=variable, file=cfile(refdat))})
        #
        # -- Create the json file RefFiles.json
        with open(RefFileName, 'w') as fp:
            json.dump(RefFiles, fp)
        fp.close()

    # -- Get the tested datasets
    TestFiles = dict()
    for model in Wmodels:
        wmodel = model.copy()
        print 'wmodel = ', wmodel
        wmodel.update(dict(variable=variable))  # Just Added
        frequency_manager_for_diag(wmodel, diag='SE')  # Just Added
        get_period_manager(wmodel)  # Just Added

        dat = regridn(annual_cycle(ds(**wmodel)), cdogrid=common_grid, option='remapdis')
        # dat = regridn( annual_cycle( ds(variable=variable, **wmodel) ), cdogrid=common_grid, option='remapdis')
        #
        # -- Get the name that will be used in the plot
        if 'customname' in wmodel:
            customname = wmodel['customname']
        else:
            customname = str.replace(build_plot_title(wmodel, None), ' ', '_')
            if 'clim_period' in wmodel:
                wperiod = wmodel['clim_period']
            # if 'period' in wmodel: wperiod=wmodel['period']
            if wmodel['period'] not in 'fx':
                wperiod = wmodel['period']
            if wperiod not in customname:
                customname = customname + '_' + wperiod
        #
        # -- Build a string that identifies the dataset (to be used in the file names)
        dataset_name_in_filename = ''
        for key in ['project', 'model', 'login', 'experiment', 'simulation', 'realization']:
            ds_for_keys = ds(**wmodel)
            # ds_for_keys = ds(variable=variable, **wmodel)
            if key in ds_for_keys.kvp:
                if ds_for_keys.kvp[key] not in '*':
                    if dataset_name_in_filename == '':
                        dataset_name_in_filename = ds_for_keys.kvp[key]
                    else:
                        dataset_name_in_filename += '_' + ds_for_keys.kvp[key]
        # Add the customname if the user provided one (this for plotting issues)
        if 'customname' in wmodel:
            dataset_name_in_filename += '_' + str.replace(customname, ' ', '_')
        else:
            # Add the period
            dataset_name_in_filename += '_' + wperiod
        output_res_hotelling_json_file = hotelling_outputdir + 'results_json_files/Res-Hotelling_' +\
                                         dataset_name_in_filename + '-' + variable + '.json'
        #
        # -- Add the path to the netcdf file
        wmodel.update(dict(file=cfile(dat), variable=variable, dataset_name_in_filename=dataset_name_in_filename,
                           output_res_hotelling_json_file=output_res_hotelling_json_file))
        if os.path.isfile(output_res_hotelling_json_file) and not force_compute:
            # -- Add the dictionary to the TestFiles dictionary
            wmodel.update(dict(compute_hotelling='FALSE'))
        else:
            wmodel.update(dict(compute_hotelling='TRUE'))
        TestFiles.update({customname: wmodel})
    #
    # -- Create the json file TestFiles.json
    TestFileName = 'test_json_files/test_files_' + comparison + '_' + variable + '.json'
    with open(TestFileName, 'w') as fp:
        json.dump(TestFiles, fp)
    fp.close()
    #
    cmd = 'Rscript --vanilla main_Hotelling.R --test_json_file ' + TestFileName + ' --reference_json_file ' + \
          RefFileName + ' --outputdir ' + hotelling_outputdir
    print cmd
    p = subprocess.Popen(shlex.split(cmd))
    p.communicate()

    # -- Start an html section to receive the plots   
    index += section('Hotelling Test Metrics vs GB2015', level=4)
    index += start_line(varlongname(variable) + ' (' + variable + ')')

    # --> Make the plot now with the list of datasets in input
    stat = 'T2'
    figname = atlas_outdir + comparison + '_' + variable + '_' + stat + '_hotelling_statistic.pdf'
    cmd = 'Rscript --vanilla Plot-Hotelling-test-results-one-variable.R --test_json_files ' + TestFileName + \
          ' --figname ' + figname
    print cmd
    p = subprocess.Popen(shlex.split(cmd))
    p.communicate()
    # -- Add the figure (hard coded) to the html line in a cell (climaf.html function)
    pngfigname = str.replace(figname, 'pdf', 'png')
    os.system('convert -density 150 ' + figname + ' -quality 90 ' + pngfigname)
    index += cell("", os.path.basename(pngfigname), thumbnail="600*450", hover=False)
    # -- Make a hard link to the atlas directory
    # cmd = 'ln '+figname+' '+str.replace()
    index += close_line() + close_table()

# -- Add the compareCompanion
index += compareCompanion()

# -- Close html
index += trailer()
outfile = index_name
with open(outfile, "w") as filout:
    filout.write(index)
print("index actually written as : " + outfile)
print("may be seen at " + root_url + outfile.replace(atlas_outdir, alt_dir_name))

# --> Use existing results??
