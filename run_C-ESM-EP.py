#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------------------------------
# -- This script run_C-ESM-EP.py runs the C-ESM-EP and builds the C-ESM-EP html frontpage for the comparison.
# -- It will:
# --     - prepare the frontpage for the comparison and copy it on a web server (provided by user)
# --     - and submit one job per component
# --     - indicate the status of the jobs to the user from the frontpage:
# --         * jobs are running: the user finds a 'Atlas is running' message in place of the atlas html page
# --           (copy of an html page for each component just before job submission)
# --         * job is successful: the atlas is available when following the link
# --         * job failed: the user finds an 'Error' page in place of the atlas html page
# --           (copy of an 'error' html page in place of the atlas html page if the job fails)
# --
# --
# -- We use it like this:
# --    python run_C-ESM-EP.py comparison [component1,component2]
# --        -> comparison is the name of the comparison directory
# --        -> component1,component2 is optional (denoted by the []); if the user provides them, the script
# --           will submit jobs only for theses components (separated by commas in case of multiple components)
# --           If you provide url instead of components, the script will only return the address of the frontpage
# --    Examples:
# --      > python run_C-ESM-EP.py comparison # runs all the components available in comparison
# --      > python run_C-ESM-EP.py comparison comp1,comp2 # submit jobs for comp1 and comp2 in comparison
# --      > python run_C-ESM-EP.py comparison url # returns the url of the frontpage
# --
# -- Author: Jerome Servonnat (LSCE-IPSL-CEA)
# -- Contact: jerome.servonnat@lsce.ipsl.fr
# --
# --
# -------------------------------------------------------------------------------------------------------------------- #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division

# -- Import python modules ----------------------------------------------------------------
import os
import sys
import getpass
import re
from locations import path_to_cesmep_output_rootdir, \
    path_to_cesmep_output_rootdir_on_web_server, root_url_to_cesmep_outputs, climaf_cache

# -- 0/ Identify where we are, based on CliMAF logics
# -----------------------------------------------------------------------------------------
from locations import atCNRM, onCiclad, onSpirit, atTGCC, atCerfacs

# -- Working directory
main_cesmep_path = os.getcwd()
# Special case at CNRM for directory /cnrm, which is a link 
if atCNRM:
    main_cesmep_path = re.sub('^/mnt/nfs/d[0-9]*/', '/cnrm/', main_cesmep_path)

# -- Get user name
username = getpass.getuser()
if username == 'fabric':
    user_login = os.getcwd().split('/')[4]
else:
    user_login = username

# -- Get account, used at TGCC
try :
    from settings import account
except:
    account = None 

    
# -- Get email
try :
    from settings import email
except:
    email=None
    
# -- Use specific location for CLIMAF_CACHE if set
cesmep_climaf_cache=os.getenv("CESMEP_CLIMAF_CACHE",'')

# -- Def pysed
def pysed(file, old_pattern, new_pattern):
    with open(file, "r") as sources:
        lines = sources.readlines()
    with open(file, "w") as sources:
        for line in lines:
            sources.write(re.sub(old_pattern, new_pattern, line))
    return ''


# -- 1/ Get the arguments / Name of the comparison (comparison)
# --    and components to be run (components)
# -----------------------------------------------------------------------------------------
args = sys.argv

# -- List of all existing components
allcomponents = ['MainTimeSeries',
                 'TuningMetrics',
                 'ParallelCoordinates_Atmosphere',
                 'Atmosphere_Surface',
                 'NH_Polar_Atmosphere_Surface',
                 'SH_Polar_Atmosphere_Surface',
                 'Atmosphere_StdPressLev',
                 'NH_Polar_Atmosphere_StdPressLev',
                 'SH_Polar_Atmosphere_StdPressLev',
                 'Atmosphere_zonmean',
                 'NEMO_main',
                 'NEMO_depthlevels',
                 'NEMO_zonmean',
                 'Atlantic_Atmosphere_Surface',
                 'Focus_Atlantic_AMOC_Surface',
                 'NEMO_PISCES',
                 'ENSO',
                 'ORCHIDEE',
                 'TurbulentAirSeaFluxes',
                 'HotellingTest',
                 'AtlasExplorer',
                 'Essentials_CM6011_CM6012',
                 'Monsoons',
                 'ORCHIDEE_DR_CMIP6',
                 ]

# -- Component that runs the PCMDI Metrics Package (specific job script)
metrics_components = ['ParallelCoordinates_Atmosphere', 'Seasonal_one_variable_parallel_coordinates']

# -- Get the arguments passed to the script
# --> If we do not specify the component(s), run all available components
if len(args) == 1:
    print('Provide the name of a comparison setup as argument of the script')
else:
    comparison = args[1].replace('/', '')
    argument = 'None'
    if len(args) == 3:
        argument = args[2].replace('/', '')
        if argument.lower() in ['url']:
            components = allcomponents
        elif argument == 'OA':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean', 'NEMO_main', 'NEMO_zonmean', 'NEMO_depthlevels',
                          'Atlantic_Atmosphere_Surface', 'ENSO', 'NEMO_PISCES']
        elif argument == 'LMDZ':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean', 'Atmosphere_StdPressLev',
                          'NH_Polar_Atmosphere_Surface', 'SH_Polar_Atmosphere_Surface',
                          'NH_Polar_Atmosphere_StdPressLev', 'SH_Polar_Atmosphere_StdPressLev']
        elif argument == 'LMDZOR':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean', 'Atmosphere_StdPressLev', 'ORCHIDEE']
        elif argument == 'NEMO':
            components = ['NEMO_main', 'NEMO_zonmean', 'NEMO_depthlevels', 'NEMO_PISCES']
        else:
            components = argument.split(',')
    else:
        components = allcomponents

# -- 1.1/ Prepare the html template
# --      => add the modules available in the comparison directory
# -----------------------------------------------------------------------------------------
template = 'share/fp_template/C-ESM-EP_template.html'

if argument.lower() not in ['url']:
   do_print = True
else:
   do_print = False

# -- Get the subdirectories available in the comparison directory
# --> we will extract the available components from this list
subdirs = next(os.walk(comparison))[1]
# -> We loop on all the potentially available and check whether they are available in the comparison directory or not
# -> The goal of this step is essentially to keep the same order of appearance of the links on front page
available_components = []
# -> First, we work on the known components listed in allcomponents. If they are in readable subdirs, we add them to 
for component in allcomponents:
    if component in subdirs:
        #if 'ParallelCoordinates_Atmosphere' in component or os.access(comparison + "/" + component, os.R_OK):
        if os.access(comparison + "/" + component, os.R_OK):
            available_components.append(component)
        else:
            # pass
            if do_print:
                print("Skipping component", component, "which dir is not readable")

# -> Then, we check whether there are some components not listed in allcomponents;
# if yes, they will be added at the end of the list
for subdir in subdirs:
    if subdir not in allcomponents and subdir not in 'tmp_paramfiles':
        available_components.append(subdir)

# If the user runs the C-ESM-EP by default, it runs all the available components
if components == allcomponents:
    components = available_components

# -- We get the atlas_head_title variable in the params_component.py file to have a more explicit string for the links
cesmep_modules = []

tested_available_components = []
for component in available_components:
    atlas_head_title = None
    # paramfile = comparison+'/'+component+'/params_'+component+'.py'
    submitdir = main_cesmep_path + '/' + comparison + '/' + component
    diag_filename = submitdir + '/diagnostics_' + component + '.py'
    params_filename = submitdir + '/params_' + component + '.py'

    if not os.path.isfile(diag_filename):
        diag_filename = main_cesmep_path + '/share/cesmep_diagnostics/diagnostics_' + component + '.py'
    # paramfile = comparison+'/'+component+'/diagnostics_'+component+'.py'
    # Allow to de-activate a component by setting read attribute to false
    try:
        with open(diag_filename, 'r') as content_file_diag:
            content_diag = content_file_diag.read()
        with open(params_filename, 'r') as content_file_params:
            content_params = content_file_params.read()
        #content.splitlines()
        module_title = None
        for tmpline in content_diag.splitlines()+content_params.splitlines():
            if 'atlas_head_title' in tmpline.split('=')[0]:
                if '"' in tmpline:
                    sep = '"'
                if "'" in tmpline:
                    sep = "'"
                module_title = tmpline.split(sep)[1]
        if module_title:
            name_in_html = module_title
        else:
            name_in_html = component
        cesmep_modules.append([component, name_in_html])
        tested_available_components.append(component)
    except:
        if do_print:
            print("Skipping component ", component, " which diagnostic file is not readable")
            #available_components.remove(component)
            continue
        
available_components = tested_available_components


# -> Adding the links to the html lines
#new_html_lines = html.splitlines()
new_html_lines = open(template).readlines()
for cesmep_module in cesmep_modules:
    newline = '<li><a href="%%target_' + cesmep_module[0] + '%%" target="_blank">' + cesmep_module[1] + '</a></li>'
    new_html_lines.append(newline)

# -- Add the path to the working directory:
newline = '<h2>Comparison directory: ' + main_cesmep_path + '/' + comparison + '</h2>'
new_html_lines.append(newline)

# -- Add links to C-ESM-EP and CliMAF documentation:
new_html_lines += [ '<li><a href="https://github.com/jservonnat/C-ESM-EP/wiki">C-ESM-EP Wiki - Documentation</a></li>',
                    '<li><a href="https://climaf.readthedocs.io/en/master/">CliMAF documentation</a></li>' ]

# -> Add the end of the html file
new_html_lines = new_html_lines + ['', '</body>', '', '</html>']

# -> We concatenate all the lines together
new_html = ''
for new_html_line in new_html_lines:
    new_html = new_html + new_html_line + '\n'

# -> Save as the html file that will be copied on the web server
frontpage_html = 'C-ESM-EP_' + comparison + '.html'
with open(frontpage_html, "w") as filout:
    filout.write(new_html)

# -- 2/ Set the paths (one per requested component) and url for the html pages
# -----------------------------------------------------------------------------------------

# -- Initialize positioning variables
if not path_to_cesmep_output_rootdir_on_web_server:
    path_to_cesmep_output_rootdir_on_web_server = path_to_cesmep_output_rootdir

# -- C-ESM-EP tree from the C-ESM-EP output rootdir
suffix_to_comparison = '/C-ESM-EP/' + comparison + '_' + user_login + '/'

# -- path_to_cesmep_output_rootdir = Path to the root of the C-ESM-EP atlas outputs
#  -> path_to_comparison_outdir = path to the comparison directory
#     (containing the frontpage and all atlas subdirectories)
path_to_comparison_outdir = path_to_cesmep_output_rootdir + '/' + suffix_to_comparison

# -- Path to the directories actually accessible from the web 
path_to_comparison_on_web_server = path_to_cesmep_output_rootdir_on_web_server + suffix_to_comparison

# -- URL  to the comparison
comparison_url = root_url_to_cesmep_outputs + suffix_to_comparison

# -- URL to C-ESM-EP frontpage
frontpage_address = comparison_url + frontpage_html


if atTGCC:
    # -- outworkdir = path to the work equivalent of the scratch
    path_to_comparison_outdir_workdir_tgcc = path_to_comparison_outdir.replace('scratch', 'work')
    if not os.path.isdir(path_to_comparison_outdir_workdir_tgcc):
        os.makedirs(path_to_comparison_outdir_workdir_tgcc)
    #thredds_cp = "/ccc/cont003/home/igcmg/igcmg/Tools/irene/thredds_cp" 
    thredds_cp = "thredds_cp"   # actual complete path is a matter of user environment

# -- Create the output directory for the comparison if they do not exist
if not os.path.isdir(path_to_comparison_on_web_server):
    os.makedirs(path_to_comparison_on_web_server)


# -- 3/ Submit the jobs (one per requested component)
# -----------------------------------------------------------------------------------------

# -- Loop on the components
job_components = []
for component in components:
    if component in available_components and component not in job_components:
        job_components.append(component)

# -- Loop on the components and edit the html file with pysed
if argument.lower() not in ['url']:
    for component in available_components:
        if component not in metrics_components:
            atlas_url = comparison_url + component + '/atlas_' + component + '_' + comparison + '.html'
        else:
            atlas_url = comparison_url + component + '/' + component + '_' + comparison + '.html'
        if onCiclad or onSpirit or atCNRM:
            if component in job_components:
                atlas_pathfilename = atlas_url.replace(comparison_url, path_to_comparison_outdir)
                if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
                    os.makedirs(os.path.dirname(atlas_pathfilename))
                # -- Copy an html template to say that the atlas is not yet available
                # 1. copy the template to the target html page
                os.system('cp -f share/fp_template/Running_template.html ' + atlas_pathfilename)
                # 2. Edit target_component and target_comparison
                pysed(atlas_pathfilename, 'target_component', component)
                pysed(atlas_pathfilename, 'target_comparison', comparison)
        if atTGCC:
            if component in job_components:
                atlas_pathfilename = atlas_url.replace(comparison_url, path_to_comparison_outdir_workdir_tgcc)
                if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
                    os.makedirs(os.path.dirname(atlas_pathfilename))
                # -- Copy an html template to say that the atlas is not yet available
                # 1. copy the template to the target html page
                os.system('cp share/fp_template/Running_template.html ' + atlas_pathfilename)
                # 2. Edit target_component and target_comparison
                pysed(atlas_pathfilename, 'target_component', component)
                pysed(atlas_pathfilename, 'target_comparison', comparison)
                # 3. thredds_cp
                os.system(thredds_cp  + ' ' +  atlas_pathfilename + ' ' + path_to_comparison_on_web_server + component)
                pysed(atlas_pathfilename, 'target_comparison', comparison)
                pysed(atlas_pathfilename, 'target_comparison', comparison)


# -- Submit the jobs
for component in job_components:
    if do_print:
        print()
        print('  -- component = ', component)
    # -- Define where the directory where the job is submitted
    submitdir = main_cesmep_path + '/' + comparison + '/' + component
    #
    # -- Do we execute the code in parallel?
    # -- We execute the params_${component}.py file to get the do_parallel variable if set to True
    do_parallel = False
    nprocs = '32'
    memory = None
    queue = None
    param_lines = []
    if os.path.isfile(submitdir + '/params_' + component + '.py'):
        param_filename = open(submitdir + '/params_' + component + '.py')
        if do_print:
            print('param file = ', submitdir + '/params_' + component + '.py')
        param_lines = param_filename.readlines()
    #
    diag_filename = submitdir + '/diagnostics_' + component + '.py'
    if not os.path.isfile(diag_filename):
        diag_filename = main_cesmep_path + '/share/cesmep_diagnostics/diagnostics_' + component + '.py'
    if do_print:
        print('diag_file = ', diag_filename)
    diag_file = open(diag_filename)
    diag_lines = diag_file.readlines()
    param_lines = param_lines + diag_lines
    for param_line in param_lines:
        if 'do_parallel' in param_line and param_line[0] != '#':
            if 'True' in param_line and do_print:
                print('param_line =', param_line)
                do_parallel = True
        if 'nprocs' in param_line and param_line[0] != '#':
            nprocs = param_line.replace(' ', '').split('=')[1].split('#')[0]
        if 'memory' in param_line and param_line[0] != '#':
            memory = param_line.replace(' ', '').split('=')[1].split('#')[0]
        if 'queue' in param_line and param_line[0] != '#':
            queue = param_line.replace(' ', '').split('=')[1].split('#')[0]

    #
    # -- Needed to copy the html error page if necessary
    if component not in metrics_components:
        atlas_url = comparison_url + component + '/atlas_' + component + '_' + comparison + '.html'
    else:
        atlas_url = comparison_url + component + '/' + component + '_' + comparison + '.html'
    if component in job_components:
        atlas_pathfilename = atlas_url.replace(comparison_url, path_to_comparison_outdir)
    #
    # -- Build the command line that will submit the job
    # ---------------------------------------------------
    # -- Case atTGCC
    if atTGCC:
        name = component + '_' + comparison + '_C-ESM-EP'
        if email:
            add_email = ' -@ ' + email
        else:
            add_email = ''
        if account is None:
            # Deduce account from CCCHOME
            account=os.getenv("CCCHOME").split("/")[4]
        if component not in metrics_components:
            cmd = 'cd ' + submitdir + ' ; export ' +\
                ' comparison=' + comparison +\
                ' component=' + component +\
                ' cesmep_frontpage=' + frontpage_address +\
                ' CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache +\
                ' ; ccc_msub' + add_email +\
                ' -r ' + name + ' -o ' + name + '_%I.out' + ' -e ' + name + '_%I.out' +\
                ' -n 1 -T 36000 -q skylake -Q normal -A ' + account +\
                ' -m store,work,scratch ' +\
                '../job_C-ESM-EP.sh ; cd -'
    #
    # -- Case onCiclad
    if onCiclad:
        # -- Start the job_options variables: a string that will contain all the job options
        #    to be passed to qsub
        job_options = ''
        #
        # -- For all the components but for the parallel coordinates, we do this...
        if email:
            add_email = ' -m e -M ' + email
            # -- add it to job_options
            job_options += add_email
        #
        # -- Set the queue
        if not queue:
            queue = 'h12'
        # -- add it to job_options
        job_options += ' -q ' + queue.replace('\n', '')
        if do_print:
            print('    -> queue = ' + queue)
        #
        # -- Specify the job script (only for Parallel coordinates)
        if component not in metrics_components:
            job_script = 'job_C-ESM-EP.sh'
        else:
            job_script = 'job_PMP_C-ESM-EP.sh'
        #
        # -- Set the memory (if provided by the user)
        # -- If memory is not set, we set one by default for NEMO atlases
        if not memory:
            if 'NEMO' in component or 'Turbulent' in component:
                memory = '30'
                vmemory = '32'
        if memory:
            # -- Set virtual memory = memory + 2
            vmemory = str(int(memory) + 2)
            memory = str(int(memory))
            # -- Set total memory instructions
            memory_instructions = ' -l mem=' + memory + 'gb -l vmem=' + vmemory + 'gb'
            # -- add it to job_options
            job_options += memory_instructions
            if do_print:
                print('    -> Memory (mem) = ' + memory + ' ; Virtual Memory (vmem) = ' + vmemory)
        #
        # -- If the user specified do_parallel=True in parameter file, we ask for one node and 32 cores
        if do_parallel:
            nprocs = str(nprocs).replace('\n', '')
            parallel_instructions = ' -l nodes=1:ppn=' + nprocs
            # -- add it to job_options
            job_options += parallel_instructions
            if do_print:
                print('    -> Parallel execution: nprocs = ' + nprocs)
        #
        # -- Build the job command line
        cmd = 'cd ' + submitdir + ' ; jobID=$(qsub ' + job_options + ' -j eo '+\
            '-v component=' + component + ',comparison='+\
             comparison + ',WD=${PWD},cesmep_frontpage='+frontpage_address+\
            ',CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache +\
            ' -N '+ component + '_' + comparison + '_C-ESM-EP ../' + job_script +\
            ') ; qsub -j eo -W "depend=afternotok:$jobID" -v atlas_pathfilename=' + atlas_pathfilename +\
            ',WD=${PWD},component=' + component + ',comparison=' + comparison +\
            ',CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache +\
            ' ../../share/fp_template/copy_html_error_page.sh ; cd -'
        print("cmd=",cmd)
    #
    # -- Case onSpirit : use SBATCH
    if onSpirit:
        # -- Start the job_options variables: a string that will contain all the job options
        #    to be passed to qsub
        job_options = ''
        #
        # -- email
        if email:
            job_options += ' --mail-type=END --mail-user=' + email
        #
        # -- Set the partition
        if not queue:
            queue = 'zen16'
        job_options += ' --partition ' + queue.replace('\n', '')
        if do_print:
            print('    -> partition = ' + queue)
        #
        # -- Specify the job script (only for Parallel coordinates)
        if component not in metrics_components:
            job_script = 'job_C-ESM-EP.sh'
        else:
            job_script = 'job_PMP_C-ESM-EP.sh'
        #
        # -- Set the memory (if provided by the user)
        # -- If memory is not set, we set one by default for NEMO atlases
        if not memory:
            if 'NEMO' in component or 'Turbulent' in component:
                memory = '30'
        if memory:
            memory = str(int(memory))
            # -- Set total memory instructions (convert to MB)
            memory_instructions = ' --mem=' + memory + '000'
            # -- add it to job_options
            job_options += memory_instructions
            if do_print:
                print('    -> Memory (mem) = ' + memory )
        #
        # -- If the user specified do_parallel=True in parameter file, we ask for a given numvber of cores
        if do_parallel:
            nprocs = str(nprocs).replace('\n', '')
            parallel_instructions = ' --ntasks=' + nprocs
            # -- add it to job_options
            job_options += parallel_instructions
            if do_print:
                print('    -> Parallel execution: nprocs = ' + nprocs)
        #
        # -- Build the job command line
        job_options += ' --time 480'
        jobname=component + '_' + comparison + '_C-ESM-EP'
        env_variables = ' --export=component=' + component + ',comparison=' + comparison + \
            ',WD=${PWD},cesmep_frontpage=' + frontpage_address + ',CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache  
        cmd = '\n\ncd ' + submitdir + ' ;\n\n'\
            'jobID=$(sbatch --job-name=' + jobname + ' ' + job_options + env_variables + ' ../' + job_script + \
            ' | awk "{print \$4}" ) ; \n'+\
            '\n'+\
            'sbatch --dependency=afternotok:$jobID '+ env_variables + \
            ',atlas_pathfilename=' + atlas_pathfilename + ' ' + \
            '--job-name=err_on_' + jobname + ' ../../share/fp_template/copy_html_error_page.sh ; \n\ncd -'
    #
    if atCNRM:
        jobname = component + '_' + comparison + '_C-ESM-EP'
        if component not in metrics_components:
            job_script = 'job_C-ESM-EP.sh'
        else:
            job_script = 'job_PMP_C-ESM-EP.sh'
        #
        variables = 'component=' + component
        variables += ',comparison=' + comparison
        variables += ',WD=$(pwd)'
        variables += ',cesmep_frontpage=' + frontpage_address
        variables += ',CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache
        #
        mail = ''
        if email is not None:
            mail = ' --mail-type=END --mail-user=%s' % email

        # at CNRM, we use sqsub on PCs for launching on aneto; env vars are sent using arg '-e'
        cmd = '( \n\t cd ' + submitdir + ' ; \n\n' + \
              '\t sqsub \\\n\t\t-e \"' + variables + '\"' + \
              ' \\\n\t\t-b "--partition=P8HOST --job-name=' + jobname + \
              ' --time=03:00:00 --nodes=1' + mail + ' " \\\n\t\t../' + job_script + \
              ' > jobname.tmp  2>&1; \n\n' + \
 \
              ' \tjobId=$(cat jobname.tmp | cut -d \" \" -f 4 jobname.tmp); rm jobname.tmp  ; \n' + \
 \
              '\t echo -n Job submitted : $jobId\n\n' + \
 \
              ' \t sqsub -b \"--partition=P8HOST -d afternotok:$jobID\" ' + \
              '-e \"atlas_pathfilename=' + atlas_pathfilename + ',' + variables + '\"' + \
              ' ../../share/fp_template/copy_html_error_page.sh >/dev/null 2>&1 \n)\n'

    if atCerfacs:
        jobname = component + '_' + comparison + '_C-ESM-EP'
        if component not in metrics_components:
            job_script = 'job_C-ESM-EP.sh'
        else:
            job_script = 'job_C-ESM-EP.sh'
            #job_script = 'job_PMP_C-ESM-EP.sh'
        #
        if do_print:
            print(component)
            print(comparison)
            cmd = 'set -x ; cd ' + submitdir + ' ; export comparison=' + comparison + \
                ' ; export component=' + component + ' ; export cesmep_frontpage=' + frontpage_address +\
                ' ; export CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache + \
                ' ; sbatch --job-name=CESMEP --partition=prod --nodes=1 --ntasks-per-node=1 '+ \
                ' --output=cesmep.o --error=cesmep.e -w gsa4 ../' + job_script              
            print(cmd)

    #
    # -- If the user provides URL or url as an argument (instead of components), the script only returns the URL of the
    # frontpage
    # -- Otherwise it submits the jobs
    # ------------------------------------------------------------------------------------------------------------------
    if do_print:
        #print("cmd=",cmd)
        os.system(cmd)
        jobfile = comparison + "/" + component + "/job.in"
        with open(jobfile, "w") as job:
            job.write(cmd)
        print("-- See job in ", jobfile)
#
# -- 4/ Create the C-ESM-EP html front page for 'comparison' from the template
# -----------------------------------------------------------------------------------------

# -- Loop on the components and edit the html file with pysed
for component in available_components:
    prefix="/atlas_"
    if component in metrics_components:
        prefix="/"
    url = comparison_url + component + prefix + component + '_' + comparison + '.html'
    pysed(frontpage_html, '%%target_' + component + '%%', url)

# -- Edit the comparison name
pysed(frontpage_html, 'target_comparison', comparison)

# -- Copy the edited html front page
if atTGCC:
    cmd1 = 'cp ' + frontpage_html + ' ' + path_to_comparison_outdir_workdir_tgcc
    print(cmd1)
    os.system(cmd1)
    cmd = thredds_cp + ' ' + path_to_comparison_outdir_workdir_tgcc + frontpage_html + ' ' + path_to_comparison_on_web_server\
          + ' ; rm ' + frontpage_html

if onCiclad or onSpirit or atCNRM or atCerfacs:
    cmd = 'mv -f ' + frontpage_html + ' ' + path_to_comparison_on_web_server
os.system(cmd)

# -- Copy the top image
if not os.path.isfile(path_to_comparison_on_web_server + '/CESMEP_bandeau.png'):
    if atTGCC :
        os.system('cp share/fp_template/CESMEP_bandeau.png ' + path_to_comparison_outdir_workdir_tgcc)
        cmd = thredds_cp + ' ' + path_to_comparison_outdir_workdir_tgcc + 'CESMEP_bandeau.png ' + \
              path_to_comparison_on_web_server
    if onCiclad or onSpirit or atCNRM or atCerfacs:
        cmd = 'cp -f share/fp_template/CESMEP_bandeau.png ' + path_to_comparison_on_web_server
    os.system(cmd)

# -- Final: Print the final message with the address of the C-ESM-EP front page
# -----------------------------------------------------------------------------------------

print('')
print('-- The CliMAF ESM Evaluation Platform atlas is available here: ')
print('--')
print('--   ' + frontpage_address)
print('--')
print('--')
print('-- The html file is here: ')
print('-- ' + path_to_comparison_on_web_server + frontpage_html)
