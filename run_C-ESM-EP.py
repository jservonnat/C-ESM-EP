#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------------------------------
# -- This script run_C-ESM-EP.py runs the C-ESM-EP and builds the C-ESM-EP html
#    frontpage for the comparison.
# -- It will:
# --     - prepare the frontpage for the comparison and copy it on a web server (provided by user)
# --     - and submit one job per component
# --     - indicate the status of the jobs to the user from the frontpage:
# --         * jobs are running: the user finds a 'Atlas is running' message in place
#              of the atlas html page (copy of an html page for each component just before
#              job submission)
# --         * job is successful: the atlas is available when following the link
# --         * job failed: the user finds an 'Error' page in place of the atlas html page
# --           (copy of an 'error' html page in place of the atlas html page if the job fails)
# --
# --
# -- We use it like this:
# --    python run_C-ESM-EP.py comparison [component1,component2 [ run_label ]]
# --        -> comparison is the name of the comparison directory
#
# --        -> component1,component2 is optional (denoted by the []); if the user provides
#              them, the script will submit jobs only for theses components (separated by
#              commas in case of multiple components)
#
# --           If you provide 'url' instead of components, the script will only print
#                   the url address of the frontpage and the corresponding filename (which
#                   root usually differ)
#
# --           If you provide 'clean' instead of components, the script will erase output
#                   directories and the climaf cache (the one indicated by env variable
#                   CESMEP_CLIMAF_CACHE, if set, otherwise the C-ESM-EP default one).
#                   At TGCC and IDRIS , outputs on thredds are included.
#
# --            Fourth optional argument run_label is used in reporting mails and defaults
#                   to "nolabel"
#
# --    Examples:
# --      > python run_C-ESM-EP.py comparison # runs all the components available in comparison
# --      > python run_C-ESM-EP.py comparison comp1,comp2 # submit jobs for comp1 and comp2 in comparison
# --      > python run_C-ESM-EP.py comparison url # returns the url of the frontpage
# --
# -- Note : atIDRIS, we forward the value of env variable 'singularity_container'
#           to launched jobs, in order to allow full control on the container used
# --
# -- Author: Jerome Servonnat (LSCE-IPSL-CEA)
# -- Contact: jerome.servonnat@lsce.ipsl.fr
# --
# --
# -------------------------------------------------------------------------------------------- #

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division
import subprocess
from subprocess import getoutput, getstatusoutput

# -- Import python modules ----------------------------------------------------------------
import os
import sys
import getpass
import re
from locations import path_to_cesmep_output_rootdir, \
    path_to_cesmep_output_rootdir_on_web_server, root_url_to_cesmep_outputs, climaf_cache

# -- 0/ Identify where we are, based on CliMAF logics
# -----------------------------------------------------------------------------------------
from locations import atCNRM, onCiclad, onSpirit, atTGCC, atIDRIS, atCerfacs

if onCiclad:
    print("Ciclad is nor more supported")
    sys.exit(1)

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

# -- Get account, used at TGCC and IDRIS
try:
    from settings import account
except:
    print("Importing account from settings failed")
    account = None


# -- Get email
try:
    from settings import email, one_mail_per_component
    if email == "None":
        email = None
except:
    email = None
    one_mail_per_component = False

# -- Use specific location for CLIMAF_CACHE if set
cesmep_climaf_cache = os.getenv("CESMEP_CLIMAF_CACHE", climaf_cache)

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
metrics_components = ['ParallelCoordinates_Atmosphere',
                      'Seasonal_one_variable_parallel_coordinates']

run_label = "nolabel"
# -- Get the arguments passed to the script
# --> If we do not specify the component(s), run all available components
if len(args) == 1:
    print('Provide the name of a comparison setup as argument of the script')
    exit(1)
else:
    comparison = args[1].replace('/', '')
    argument = 'None'
    if len(args) >= 3:
        argument = args[2].replace('/', '')
        if argument.lower() in ['url', 'clean']:
            components = allcomponents
        elif argument == 'OA':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean',
                          'NEMO_main', 'NEMO_zonmean', 'NEMO_depthlevels',
                          'Atlantic_Atmosphere_Surface', 'ENSO', 'NEMO_PISCES']
        elif argument == 'LMDZ':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean', 'Atmosphere_StdPressLev',
                          'NH_Polar_Atmosphere_Surface', 'SH_Polar_Atmosphere_Surface',
                          'NH_Polar_Atmosphere_StdPressLev', 'SH_Polar_Atmosphere_StdPressLev']
        elif argument == 'LMDZOR':
            components = ['Atmosphere_Surface', 'Atmosphere_zonmean',
                          'Atmosphere_StdPressLev', 'ORCHIDEE']
        elif argument == 'NEMO':
            components = ['NEMO_main', 'NEMO_zonmean',
                          'NEMO_depthlevels', 'NEMO_PISCES']
        else:
            components = argument.split(',')
        if len(args) == 4:
            run_label = args[3]
    else:
        components = allcomponents

# -- 1.1/ Prepare the html template
# --      => add the modules available in the comparison directory
# -----------------------------------------------------------------------------------------
template = 'share/fp_template/C-ESM-EP_template.html'

if argument.lower() in ['url', 'clean']:
    do_print = False
else:
    do_print = True

# -- Get the subdirectories available in the comparison directory
# --> we will extract the available components from this list
subdirs = next(os.walk(comparison))[1]
# -> We loop on all the potentially available and check whether they
# -> are available in the comparison directory or not. The goal of this
# -> step is essentially to keep the same order of appearance of the
# -> links on front page
available_components = []

# -> First, we work on the known components listed in
# -> allcomponents. If they are in readable subdirs, we add them to
for component in allcomponents:
    if component in subdirs:
        # if 'ParallelCoordinates_Atmosphere' in component or
        # os.access(comparison + "/" + component, os.R_OK):
        if os.access(comparison + "/" + component, os.R_OK):
            available_components.append(component)
        else:
            if do_print:
                print("Skipping component", component,
                      "which dir is not readable")

# -> Then, we check whether there are some components not listed in allcomponents;
# if yes, they will be added at the end of the list
for subdir in subdirs:
    if subdir not in allcomponents and subdir not in 'tmp_paramfiles':
        available_components.append(subdir)

# If the user runs the C-ESM-EP by default, it runs all the available components
if components == allcomponents:
    components = available_components

# -- We get the atlas_head_title variable in the params_component.py
# -- file to have a more explicit string for the links
cesmep_modules = []

tested_available_components = []

# -- Define a directory common to all components
comparison_dir = main_cesmep_path + '/' + comparison

for component in available_components:
    atlas_head_title = None
    submitdir = comparison_dir + '/' + component
    diag_filename = submitdir + '/diagnostics_' + component + '.py'
    params_filename = submitdir + '/params_' + component + '.py'

    if not os.path.isfile(diag_filename):
        diag_filename = main_cesmep_path + \
            '/share/cesmep_diagnostics/diagnostics_' + component + '.py'
    # paramfile = comparison+'/'+component+'/diagnostics_'+component+'.py'
    # Allow to de-activate a component by setting read attribute to false
    try:
        with open(diag_filename, 'r') as content_file_diag:
            content_diag = content_file_diag.read()
        with open(params_filename, 'r') as content_file_params:
            content_params = content_file_params.read()
        # content.splitlines()
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
            print("Skipping component ", component,
                  " which diagnostic file is not readable")
            # available_components.remove(component)
            continue

available_components = tested_available_components

# Skip some standard comparison at CNRM (not available)
if atCNRM and "ORCHIDEE" in available_components:
    available_components.remove("ORCHIDEE")

# -> Adding the links to the html lines
new_html_lines = open(template).readlines()
for cesmep_module in cesmep_modules:
    newline = '<li><a href="%%target_' + \
        cesmep_module[0] + '%%" target="_blank">' + \
        cesmep_module[1] + '</a></li>'
    new_html_lines.append(newline)

# -- Add the path to the working directory:
newline = '<h2>Comparison directory: ' + \
    main_cesmep_path + '/' + comparison + '</h2>'
new_html_lines.append(newline)

# -- Add links to C-ESM-EP and CliMAF documentation:
new_html_lines += ['<li><a href="https://github.com/jservonnat/C-ESM-EP/wiki">C-ESM-EP Wiki - Documentation</a></li>',
                   '<li><a href="https://climaf.readthedocs.io/en/master/">CliMAF documentation</a></li>']

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
path_to_comparison_outdir = path_to_cesmep_output_rootdir + suffix_to_comparison

# -- Path to the directories actually accessible from the web
path_to_comparison_on_web_server = path_to_cesmep_output_rootdir_on_web_server + \
    suffix_to_comparison

# -- URL  to the comparison
comparison_url = root_url_to_cesmep_outputs + suffix_to_comparison

# -- URL to C-ESM-EP frontpage
frontpage_address = comparison_url + frontpage_html

# -- outdir_workdir = path to the work equivalent of the scratch
if atTGCC:
    path_to_comparison_outdir_workdir_tgcc = path_to_comparison_outdir.replace(
        'scratch', 'workflash')
if atIDRIS:
    path_to_comparison_outdir_workdir_tgcc = path_to_comparison_outdir.replace(
        'scratch', 'work')
if atTGCC or atIDRIS:
    if not os.path.isdir(path_to_comparison_outdir_workdir_tgcc):
        os.makedirs(path_to_comparison_outdir_workdir_tgcc)

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
if argument.lower() not in ['url', 'clean']:
    for component in available_components:
        if component not in metrics_components:
            atlas_url = comparison_url + component + '/atlas_' + \
                component + '_' + comparison + '.html'
        else:
            atlas_url = comparison_url + component + '/' + \
                component + '_' + comparison + '.html'
        if onSpirit or atCNRM or atIDRIS:
            if component in job_components:
                atlas_pathfilename = atlas_url.replace(
                    comparison_url, path_to_comparison_outdir)
                if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
                    os.makedirs(os.path.dirname(atlas_pathfilename))
                # -- Copy an html template to say that the atlas is not yet available
                # 1. copy the template to the target html page
                os.system(
                    'cp -f share/fp_template/Running_template.html ' + atlas_pathfilename)
                # 2. Edit target_component and target_comparison
                pysed(atlas_pathfilename, 'target_component', component)
                pysed(atlas_pathfilename, 'target_comparison', comparison)
                if atIDRIS:
                    # 3. First clean target, then thredds_cp
                    destdir = path_to_comparison_on_web_server + component
                    rmcmd = 'mfthredds -r ' + destdir + '/' + \
                        atlas_pathfilename.split("/")[-1]
                    cmd = rmcmd + '; mfthredds -d ' + destdir + ' ' + atlas_pathfilename
                    #print("cmd=", cmd)
                    os.system(cmd)

        if atTGCC:
            if component in job_components:
                atlas_pathfilename = atlas_url.replace(
                    comparison_url, path_to_comparison_outdir_workdir_tgcc)
                if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
                    os.makedirs(os.path.dirname(atlas_pathfilename))
                # -- Copy an html template to say that the atlas is not yet available
                # 1. copy the template to the target html page
                os.system(
                    'cp share/fp_template/Running_template.html ' + atlas_pathfilename)
                # 2. Edit target_component and target_comparison
                pysed(atlas_pathfilename, 'target_component', component)
                pysed(atlas_pathfilename, 'target_comparison', comparison)
                # 3. thredds_cp
                os.system('thredds_cp ' + atlas_pathfilename +
                          ' ' + path_to_comparison_on_web_server + component)

    # Create an empty file for accumulating launched jobs ids
    launched_jobs = comparison_dir + "/launched_jobs"
    os.system("cat /dev/null >" + launched_jobs)

# -- Submit the jobs
all_submits_OK = True
for component in job_components:
    if do_print:
        print()
        print('  -- component = ', component)
    # -- Define where the directory where the job is submitted
    submitdir = comparison_dir + '/' + component
    jobname = component + '_' + comparison + '_C-ESM-EP'
    #
    # -- Do we execute the code in parallel?  We execute the
    # -- params_${component}.py file to get the do_parallel variable
    # -- if set to True
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
        diag_filename = main_cesmep_path + \
            '/share/cesmep_diagnostics/diagnostics_' + component + '.py'
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
        atlas_url = comparison_url + component + '/atlas_' + \
            component + '_' + comparison + '.html'
    else:
        atlas_url = comparison_url + component + '/' + \
            component + '_' + comparison + '.html'
    if component in job_components:
        atlas_pathfilename = atlas_url.replace(
            comparison_url, path_to_comparison_outdir)

    # -- Specify the job script (only for Parallel coordinates)
    if component not in metrics_components:
        job_script = 'job_C-ESM-EP.sh'
    else:
        job_script = 'job_PMP_C-ESM-EP.sh'
    #
    # -- Build the command line and submit the job
    # ---------------------------------------------------

    if atTGCC:
        if email is not None and one_mail_per_component is True:
            add_email = ' -@ ' + email
        else:
            add_email = ''
        if account is None:
            # Deduce account from CCCHOME
            account = os.getenv("CCCHOME").split("/")[4]
        if component in metrics_components:
            continue  # metrics_components are not tested at TGCC
        if component != 'NEMO_zonmean':
            partition = '-q skylake'
        else:
            partition = '-q xlarge'
        cmd = 'cd ' + submitdir + ' ; export ' +\
            ' comparison=' + comparison +\
            ' component=' + component +\
            ' cesmep_frontpage=' + frontpage_address +\
            ' CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache +\
            ' PYTHONPATH=' + os.getenv("PYTHONPATH", "") +\
            ' ; ccc_msub' + add_email +\
            ' -r ' + jobname + ' -o ' + jobname + '_%I.out' + ' -e ' + jobname + '_%I.out' +\
            ' -n 1 -T 36000 ' + partition + ' -Q normal -A ' + account +\
            ' -m store,work,scratch ' +\
            '../../job_C-ESM-EP.sh'
        # -- Submit job
        if do_print:
            exitcode, output = getstatusoutput(cmd)
            if exitcode == 0:
                jobid = output.split(' ')[3]
                with open(launched_jobs, "a") as lj:
                    lj.write(jobid+"\n")
            else:
                print(f"\n\nIssue submitting that job:{cmd}\n\n{output}\n")
                all_submits_OK = False

    #
    # -- Case onSpirit and atIDRIS : use SBATCH
    if onSpirit or atIDRIS:
        # -- Start the job_options variables: a string that will
        #    contain all the job options to be passed to qsub
        job_options = ''
        #
        # -- email
        if email and one_mail_per_component:
            job_options += ' --mail-type=END --mail-user=' + email
        #
        # -- Set the partition and account
        if not queue:
            if onSpirit:
                queue = 'zen16'
            elif atIDRIS:
                queue = 'prepost'
        if atIDRIS:
            account_options = " --hint=nomultithread"
            if account is None:
                # Use default account
                account = getoutput("idrproj | grep default | cut -d ' ' -f 3") \
                    + "@cpu"
            account_options += f" --account={account}"
        else:
            account_options = ""
        account_options += ' --partition=' + queue.replace('\n', '')
        #
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
                print('    -> Memory (mem) = ' + memory)
        #
        # -- If the user specified do_parallel=True in parameter file,
        # -- we ask for a given number of cores
        if do_parallel:
            nprocs = str(nprocs).replace('\n', '')
            parallel_instructions = ' --ntasks=' + nprocs
            # -- add it to job_options
            job_options += parallel_instructions
            if do_print:
                print('    -> Parallel execution: nprocs = ' + nprocs)
        #

        # -- Build the job command line
        job_options += ' --time=480'
        env_variables = ' --export=ALL' + \
            ',component=' + component + \
            ',comparison=' + comparison + \
            ',WD=${PWD},cesmep_frontpage=' + frontpage_address + \
            ',CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache
        if atIDRIS:
            env_variables += ',singularity_container=' + \
                os.getenv('singularity_container', '')
        cmd = '\n\ncd ' + submitdir + ' ;\n\n'\
            'sbatch --job-name=' + jobname + ' ' + job_options + \
            account_options + env_variables + ' ../../' + job_script

        # -- Submit job
        if do_print:
            exitcode, output = getstatusoutput(cmd)
            if exitcode != 0:
                print(f"\n\nIssue submitting that job:{cmd}\n\n{output}\n")
                all_submits_OK = False
            else:
                # JobId is last string of last line od output
                jobid = output.split("\n")[-1].split(' ')[-1]
                with open(launched_jobs, "a") as lj:
                    lj.write(jobid+"\n")
                error_job = f'cd {submitdir} ; sbatch --dependency=afternotok:{jobid} ' + \
                    env_variables + f',atlas_pathfilename={atlas_pathfilename}  ' + \
                    f'--job-name=err_on_{jobname}' + account_options +\
                    ' ../../share/fp_template/copy_html_error_page.sh'
                os.system(error_job)

    #
    if atCNRM:
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
        cmd = '\n\t cd ' + submitdir + ' ; \n\n' + \
              '\t sqsub \\\n\t\t-e \"' + variables + '\"' + \
              ' \\\n\t\t-b "--partition=P8HOST --job-name=' + jobname + \
              ' --time=03:00:00 --nodes=1' + mail + ' " \\\n\t\t../../' + job_script

        if do_print:
            exitcode, output = getstatusoutput(cmd)
            if exitcode != 0:
                print(f"\n\nIssue submitting that job:{cmd}\n\n{output}\n")
                all_submits_OK = False
            else:
                jobid = output.split(' ')[3]
                with open(launched_jobs, "a") as lj:
                    lj.write(jobid+"\n")
                error_job = f' cd {submitdir}; ' + \
                    f'sqsub -b \"--partition=P8HOST -d afternotok:{jobid}\" ' + \
                    f'-e \"atlas_pathfilename={atlas_pathfilename},' + variables + '\"' + \
                    ' ../../share/fp_template/copy_html_error_page.sh >/dev/null 2>&1 \n'
                os.system(error_job)

    if atCerfacs:
        #
        if do_print:
            print(component)
            print(comparison)
            cmd = 'set -x ; cd ' + submitdir + ' ; export comparison=' + comparison + \
                ' ; export component=' + component + \
                ' ; export cesmep_frontpage=' + frontpage_address +\
                ' ; export CESMEP_CLIMAF_CACHE=' + cesmep_climaf_cache + \
                ' ; sbatch --job-name=CESMEP --partition=prod --nodes=1 --ntasks-per-node=1 ' + \
                ' --output=cesmep.o --error=cesmep.e -w gsa4 ../../' + job_script
            print(cmd)
            os.system(cmd)

    #
    # -- Provide a copy of job submission command
    # --------------------------------------------------------------------------------------
    if argument.lower() not in ['url', 'clean']:
        # print("cmd=",cmd)
        jobfile = comparison + "/" + component + "/job.in"
        with open(jobfile, "w") as job:
            job.write(cmd)
        print("-- See job in ", jobfile)
#
# -- 4/ Create the C-ESM-EP html front page for 'comparison' from the template
# ----------------------------------------------------------------------------

if argument.lower() not in ['url', 'clean']:
    # -- Loop on the components and edit the html file with pysed
    for component in available_components:
        prefix = "/atlas_"
        if component in metrics_components:
            prefix = "/"
        url = comparison_url + component + prefix + \
            component + '_' + comparison + '.html'
        pysed(frontpage_html, '%%target_' + component + '%%', url)

    # -- Edit the comparison name
    pysed(frontpage_html, 'target_comparison', comparison)

    # -- Copy the edited html front page
    if atTGCC or atIDRIS:
        cmd1 = 'cp ' + frontpage_html + ' ' + path_to_comparison_outdir_workdir_tgcc
        if do_print:
            print("First copying html front page to workdir: ", cmd1)
        os.system(cmd1)
        html_file = path_to_comparison_outdir_workdir_tgcc + frontpage_html
        if atTGCC:
            cmd = 'thredds_cp ' + html_file + ' ' + path_to_comparison_on_web_server +\
                '; chmod +r ' + path_to_comparison_on_web_server + '/' + frontpage_html
        if atIDRIS:
            rmcmd = "mfthredds -r " + path_to_comparison_on_web_server + \
                '/' + html_file.split("/")[-1]
            cmd = rmcmd + ";mfthredds -d " + path_to_comparison_on_web_server + ' ' + html_file
        cmd += ' ; rm ' + frontpage_html
    #
    if onSpirit or atCNRM or atCerfacs:
        cmd = f'mv -f {frontpage_html} {path_to_comparison_on_web_server}'
    #
    # print(os.getcwd())
    # print(cmd)
    os.system(cmd)

    # -- Copy the top image
    if not os.path.isfile(path_to_comparison_on_web_server + '/CESMEP_bandeau.png'):
        if atTGCC or atIDRIS:
            os.system('cp share/fp_template/CESMEP_bandeau.png ' +
                      path_to_comparison_outdir_workdir_tgcc)
            if atTGCC:
                cmd = 'thredds_cp ' + path_to_comparison_outdir_workdir_tgcc + \
                    'CESMEP_bandeau.png ' + path_to_comparison_on_web_server
            if atIDRIS:
                rmcmd = 'mfthredds -r  ' + path_to_comparison_on_web_server + '/' + \
                    'CESMEP_bandeau.png '
                cmd = rmcmd + ';mfthredds -d  ' + path_to_comparison_on_web_server + ' ' + \
                    path_to_comparison_outdir_workdir_tgcc + 'CESMEP_bandeau.png '
        if onSpirit or atCNRM or atCerfacs:
            cmd = 'cp -f share/fp_template/CESMEP_bandeau.png ' + \
                path_to_comparison_on_web_server
    os.system(cmd)

    # -- Launch a job that sends a mail when all atlas jobs are completed
    if one_mail_per_component is False and email is not None:
        job_ids = ""
        with open(launched_jobs) as lj:
            for line in lj:
                job_ids = job_ids + line.replace("\n", ",")
        if len(job_ids) > 0:
            job_ids = job_ids.rstrip(",")
            job_name = run_label
            job_content = f"#!/bin/bash" +\
                "\necho This is a job launched for sending a mail on completion " +\
                f"of C-ESM-EP run for comparison {comparison} and label {run_label}." +\
                f"\necho The atlas is available at {frontpage_address}"
            with open(f"{comparison_dir}/mailjob", "w") as mj:
                mj.write(job_content)
            cmd = ""
            out = 'completion.out'
            if atTGCC:
                cmd = f"cd {comparison_dir} ; "
                cmd += f" ccc_msub  -@ {email} -r {job_name} -m store,work,scratch "
                cmd += f"-o {out} -e {out} -n 1 -T 300 -q skylake "
                cmd += f"-Q normal -A {account}  -a {job_ids} mailjob; "
                cmd += f"rm -f mailjob {launched_jobs}"
            if onSpirit or atIDRIS:
                job_ids = job_ids.replace(",", ":")
                cmd = f"cd {comparison_dir} ; "
                cmd += f" sbatch --job-name={job_name} --dependency=afterany:{job_ids} "
                if atIDRIS:
                    cmd += f" --account={account}"
                cmd += f" --mail-type=END --mail-user={email} -o {out} -e {out} mailjob;"
                cmd += f" rm -f mailjob {launched_jobs}"
            #print('mail cmd=', cmd)
            os.system(cmd)


# -- Final: Print the final message with the address of the C-ESM-EP front page
# ----------------------------------------------------------------------------------


if argument.lower() not in ['clean']:
    print('')
    print('-- The CliMAF ESM Evaluation Platform atlas is available here: ')
    print('--')
    print('--   ' + frontpage_address)
    print('--')
    print('--')
    print('-- The html file is here: ')
    if not atIDRIS:
        print('-- ' + path_to_comparison_on_web_server + frontpage_html)
    else:
        print('-- ' + html_file)

if argument.lower() in ['clean']:
    os.system("rm -fr " + cesmep_climaf_cache)
    os.system("rm -fr " + path_to_comparison_on_web_server)
    if atTGCC:
        os.system("rm -fr " + path_to_comparison_outdir_workdir_tgcc)
    else:
        os.system("rm -fr " + path_to_comparison_outdir)

if not all_submits_OK:
    exit(1)
