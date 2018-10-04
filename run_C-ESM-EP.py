#!/bin/python
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
# --------------------------------------------------------------------------------------------------------------------- #


# -- Provide your e-mail if you want to receive an e-mail at the end of the execution of the jobs
#email = "senesi@meteo.fr" 
email = "jerome.servonnat@lsce.ipsl.fr"
#email=None

# -- Import python modules ----------------------------------------------------------------
import os, sys
import getpass
import re


# -- 0/ Identify where we are...
# -----------------------------------------------------------------------------------------

# -- Working directory
WD=os.getcwd()
# Special case at CNRM for directory /cnrm, which is a link 
atCNRM = os.path.exists('/cnrm')
if atCNRM :
   WD=re.sub('^/mnt/nfs/d[0-9]*/','/cnrm/',WD)

# -- Get user name
username=getpass.getuser()
if username=='fabric':
   user_login = str.split(os.getcwd(),'/')[4]
else:
   user_login = username

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
allcomponents=['MainTimeSeries',
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
metrics_components = ['ParallelCoordinates_Atmosphere','Seasonal_one_variable_parallel_coordinates']

# -- Get the arguments passed to the script
# --> If we do not specify the component(s), run all available components
if len(args)==1:
   print 'Provide the name of a comparison setup as argument of the script'
else:
   comparison=str.replace(args[1],'/','')
   argument='None'
   if len(args)==3:
      argument=args[2]
      if argument.lower() in ['url']:
         components=allcomponents
      elif argument=='OA':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','NEMO_main','NEMO_zonmean','NEMO_depthlevels','Atlantic_Atmosphere_Surface','ENSO','NEMO_PISCES']
      elif argument=='LMDZ':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','Atmosphere_StdPressLev','NH_Polar_Atmosphere_Surface','SH_Polar_Atmosphere_Surface','NH_Polar_Atmosphere_StdPressLev','SH_Polar_Atmosphere_StdPressLev']
      elif argument=='LMDZOR':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','Atmosphere_StdPressLev','ORCHIDEE']
      elif argument=='NEMO':
         components = ['NEMO_main','NEMO_zonmean','NEMO_depthlevels','NEMO_PISCES']
      else:
         components=str.split(argument,',')
   else:
      components=allcomponents



# -- 1.1/ Prepare the html template
# --      => add the modules available in the comparison directory
# -----------------------------------------------------------------------------------------
template = 'share/fp_template/C-ESM-EP_template.html'
from urllib import urlopen

# -> First, we read the template of the html file in share/fp_template
url = template    
html = urlopen(template).read()    

# -- Get the subdirectories available in the comparison directory
# --> we will extract the available components from this list
subdirs = next(os.walk(comparison))[1]
# -> We loop on all the potentially available and check whether they are available in the comparison directory or not
# -> The goal of this step is essentially to keep the same order of appearance of the links on front page
available_components = []
# -> First, we work on the known components listed in allcomponents. If they are in readable subdirs, we add them to 
for component in allcomponents:
  if component in subdirs :
     if os.access(comparison+"/"+component,os.R_OK):
        available_components.append(component)
     else:
        #pass
        print "Skipping component",component,"which dir is not readable"
# -> Then, we check whether there are some components not listed in allcomponents;
# if yes, they will be added at the end of the list
for subdir in subdirs:
  if subdir not in allcomponents and subdir not in 'tmp_paramfiles':
     available_components.append(subdir)

# If the user runs the C-ESM-EP by default, it runs all the available components
if components==allcomponents: components = available_components

# -- We get the atlas_head_title variable in the params_component.py file to have a more explicit string for the links
cesmep_modules = []
for component in available_components:
    atlas_head_title = None
    paramfile = comparison+'/'+component+'/params_'+component+'.py'
    # Allow to de-activate a component by setting read attribute to false
    try :
       with open(paramfile, 'r') as content_file:
          content = content_file.read()
    except :
       print "Skipping component ",component, " which param file is not readable"
       available_components.remove(component)
       continue
    content.splitlines()
    module_title = None
    for tmpline in content.splitlines():
        if 'atlas_head_title' in tmpline:
            if '"' in tmpline: sep = '"'
            if "'" in tmpline: sep="'"
            module_title = str.split(tmpline,sep)[1]
    if module_title:
        name_in_html = module_title
    else:
        name_in_html = component
    cesmep_modules.append([component,name_in_html])

# -> Adding the links to the html lines
new_html_lines = html.splitlines()
for cesmep_module in cesmep_modules:
    newline = '<li><a href="target_'+cesmep_module[0]+'" target="_blank">'+cesmep_module[1]+'</a></li>'
    new_html_lines.append(newline)

# -> Add the end of the html file
new_html_lines = new_html_lines + ['','</body>','','</html>']

# -> We concatenate all the lines together
new_html = ''
for new_html_line in new_html_lines: new_html = new_html+new_html_line+'\n'

# -> Save as the html file that will be copied on the web server
frontpage_html='C-ESM-EP_'+comparison+'.html'
with open(frontpage_html,"w") as filout : filout.write(new_html)

# -- 2/ Set the paths (one per requested component) and url for the html pages
# -----------------------------------------------------------------------------------------

# -- Initialize positioning variables
atTGCC   = False
onCiclad = False

from locations import path_to_cesmep_output_rootdir, path_to_cesmep_output_rootdir_on_web_server, root_url_to_cesmep_outputs

if not path_to_cesmep_output_rootdir_on_web_server:
   path_to_cesmep_output_rootdir_on_web_server = path_to_cesmep_output_rootdir



# -- C-ESM-EP tree from the C-ESM-EP output rootdir
suffix_to_comparison = '/C-ESM-EP/'+comparison+'_'+user_login+'/'

# -- path_to_cesmep_output_rootdir = Path to the root of the C-ESM-EP atlas outputs
#  -> path_to_comparison_outdir = path to the comparison directory (containing the frontpage and all atlas subdirectories)
path_to_comparison_outdir = path_to_cesmep_output_rootdir + '/' + suffix_to_comparison

# -- Path to the directories actually accessible from the web 
path_to_comparison_on_web_server = path_to_cesmep_output_rootdir_on_web_server + suffix_to_comparison

# -- Path 



# -- URL  to the comparison 
comparison_url = root_url_to_cesmep_outputs + suffix_to_comparison



if os.path.exists ('/ccc') and not os.path.exists ('/data')  :
    atTGCC   = True
    # -- outworkdir = path to the work equivalent of the scratch
    path_to_comparison_outdir_workdir_tgcc = str.replace(path_to_comparison_outdir,'scratch','work')
    if not os.path.isdir(path_to_comparison_outdir_workdir_tgcc): os.makedirs(path_to_comparison_outdir_workdir_tgcc)

if 'ciclad' in os.uname()[1].strip().lower():
    onCiclad = True

if os.path.exists('/cnrm'):
    atCNRM = True
    from locations import climaf_cache


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
       atlas_url = comparison_url+'/'+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       atlas_url = comparison_url+'/'+component+'/'+component+'_'+comparison+'.html'
    if onCiclad or atCNRM :
       if component in job_components:
          atlas_pathfilename = str.replace(atlas_url, comparison_url, path_to_comparison_outdir)
          if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
             os.makedirs(os.path.dirname(atlas_pathfilename))
          # -- Copy an html template to say that the atlas is not yet available
          # 1. copy the template to the target html page
          os.system('cp -f share/fp_template/Running_template.html '+atlas_pathfilename)
          # 2. Edit target_component and target_comparison
          pysed(atlas_pathfilename, 'target_component', component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
    if atTGCC:
       if component in job_components:
          atlas_pathfilename = str.replace(atlas_url, comparison_url, path_to_comparison_outdir_workdir_tgcc)
          if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
             os.makedirs(os.path.dirname(atlas_pathfilename))
          # -- Copy an html template to say that the atlas is not yet available
          # 1. copy the template to the target html page
          os.system('cp share/fp_template/Running_template.html '+atlas_pathfilename)
          # 2. Edit target_component and target_comparison
          pysed(atlas_pathfilename, 'target_component', component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
          # 3. dods_cp
          os.system('dods_cp '+atlas_pathfilename+' '+path_to_comparison_on_web_server+component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
          pysed(atlas_pathfilename, 'target_comparison', comparison)


# -- Submit the jobs
for component in job_components:
    print '  -- component = ',component
    # -- Define where the directory where the job is submitted
    submitdir = WD+'/'+comparison+'/'+component
    #
    # -- Do we execute the code in parallel?
    # -- We execute the params_${component}.py file to get the do_parallel variable if set to True
    do_parallel=False
    nprocs = '32'
    memory = None
    queue = None
    param_filename = open(submitdir+'/params_'+component+'.py')
    param_lines = param_filename.readlines()
    for param_line in param_lines:
        if 'do_parallel' in param_line and param_line[0]!='#':
           if 'True' in param_line: do_parallel = True
        if 'nprocs' in param_line and param_line[0]!='#':
           nprocs = str.split(str.split(str.replace(param_line,' ',''),'=')[1], '#')[0]
        if 'memory' in param_line and param_line[0]!='#':
           memory = str.split(str.split(str.replace(param_line,' ',''),'=')[1], '#')[0]
        if 'queue' in param_line and param_line[0]!='#':
           queue  = str.split(str.split(str.replace(param_line,' ',''),'=')[1], '#')[0]
    #
    # -- Needed to copy the html error page if necessary
    if component not in metrics_components:
       atlas_url = comparison_url+'/'+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       atlas_url = comparison_url+'/'+component+'/'+component+'_'+comparison+'.html' 
    if component in job_components:
       atlas_pathfilename = str.replace(atlas_url, comparison_url, path_to_comparison_outdir)
    #
    # -- Build the command line that will submit the job
    # ---------------------------------------------------
    # -- Case atTGCC
    if atTGCC:
       if email:
          add_email = ' -@ '+email
       else:
          add_email=''
       if component not in metrics_components:
          cmd = 'cd '+submitdir+' ; export comparison='+comparison+\
                ' ; export component='+component+' ; ccc_msub'+add_email+' -r '+\
                component+'_'+comparison+'_C-ESM-EP ../job_C-ESM-EP.sh ; cd -'
    #
    # -- Case onCiclad
    if onCiclad:
       # -- Start the job_options variables: a string that will contain all the job options
       #    to be passed to qsub
       job_options = ''
       #
       # -- For all the components but for the parallel coordinates, we do this...
       if email:
          add_email = ' -m e -M '+email
          # -- add it to job_options
          job_options += add_email
       # 
       # -- Set the queue
       if not queue: queue = 'h12'
       # -- add it to job_options
       job_options += ' -q '+queue
       print '    -> queue = '+queue
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
          vmemory = str(int(memory)+2)
          # -- Set total memory instructions
          memory_instructions = ' -l mem='+memory+'gb -l vmem='+vmemory+'gb'
          # -- add it to job_options
          job_options += memory_instructions
          print '    -> Memory (mem) = '+memory+' ; Virtual Memory (vmem) = '+vmemory
       #
       # -- If the user specified do_parallel=True in parameter file, we ask for one node and 32 cores
       if do_parallel:
          parallel_instructions = ' -l nodes=1:ppn='+nprocs
          # -- add it to job_options
          job_options += parallel_instructions
          print '    -> Parallel execution: nprocs = '+nprocs
       # 
       # -- Build the job command line
       cmd = 'cd '+submitdir+' ; jobID=$(qsub'+job_options+' -v component='+component+',comparison='+comparison+',WD=${PWD} -N '+component+'_'+comparison+'_C-ESM-EP ../'+job_script+') ; qsub -W "depend=afternotok:$jobID" -v atlas_pathfilename='+atlas_pathfilename+',WD=${PWD},component='+component+',comparison='+comparison+' ../../share/fp_template/copy_html_error_page.sh ; cd -'
    #
    if atCNRM:
       jobname=component+'_'+comparison+'_C-ESM-EP'
       if component not in metrics_components: job_script = 'job_C-ESM-EP.sh'
       else: job_script = 'job_PMP_C-ESM-EP.sh'
       # 
       variables  =  'component='+component
       variables += ',comparison='+comparison
       variables += ',WD=$(pwd)'
       variables += ',CLIMAF_CACHE='+climaf_cache
       #
       mail = ''
       if email is not None : mail = ' --mail-type=END --mail-user=%s'%email
       
       # at CNRM, we use sqsub on PCs for launching on aneto; env vars are sent using arg '-e'
       cmd = '( \n\tcd '+submitdir+' ; \n\n'+\
             '\tsqsub \\\n\t\t-e \"'+variables+'\"'+\
             ' \\\n\t\t-b "--job-name='+jobname+mail+' " \\\n\t\t../'+job_script+ ' > jobname.tmp  2>&1; \n\n'+\
             \
             ' \tjobId=$(cat jobname.tmp | cut -d \" \" -f 4 jobname.tmp); rm jobname.tmp  ; \n'+\
             \
             '\techo -n Job submitted : $jobId\n\n'+\
             \
             ' \tsqsub -b \"-d afternotok:$jobID\" '+\
             '-e \"atlas_pathfilename='+atlas_pathfilename+','+variables+'\"'+\
             ' ../../share/fp_template/copy_html_error_page.sh >/dev/null 2>&1 \n)\n'

    #
    # -- If the user provides URL or url as an argument (instead of components), the script only returns the URL of the frontpage
    # -- Otherwise it submits the jobs
    # ----------------------------------------------------------------------------------------------------------------------------
    if argument.lower() not in ['url']:
       os.system(cmd)
       jobfile=comparison+"/"+component+"/job.in"
       with open(jobfile,"w") as job : job.write(cmd)
       print "-- See job in ",jobfile ; print



# -- 4/ Create the C-ESM-EP html front page for 'comparison' from the template 
# -----------------------------------------------------------------------------------------

# -- Loop on the components and edit the html file with pysed
for component in available_components:
    if component not in metrics_components:
       url = comparison_url+'/'+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       url = comparison_url+'/'+component+'/'+component+'_'+comparison+'.html'
    pysed(frontpage_html, 'target_'+component, url)

# -- Edit the comparison name
pysed(frontpage_html, 'target_comparison', comparison)

# -- Copy the edited html front page
if atTGCC:
   cmd1 = 'cp '+frontpage_html+' '+path_to_comparison_outdir_workdir_tgcc ; print cmd1 ; os.system(cmd1)
   cmd = 'dods_cp '+path_to_comparison_outdir_workdir_tgcc+frontpage_html+' '+path_to_comparison_on_web_server+' ; rm '+main_html

if onCiclad or atCNRM : cmd = 'mv -f '+frontpage_html+' '+path_to_comparison_on_web_server
os.system(cmd)

# -- Copy the top image
if not os.path.isfile(path_to_comparison_on_web_server+'/CESMEP_bandeau.png'):
   if atTGCC:
      os.system('cp share/fp_template/CESMEP_bandeau.png '+path_to_comparison_outdir_workdir_tgcc)
      cmd='dods_cp '+path_to_comparison_outdir_workdir_tgcc+'CESMEP_bandeau.png '+path_to_comparison_on_web_server
   if onCiclad or atCNRM : cmd='cp -f share/fp_template/CESMEP_bandeau.png '+path_to_comparison_on_web_server
   os.system(cmd)



# -- Final: Print the final message with the address of the C-ESM-EP front page
# -----------------------------------------------------------------------------------------
frontpage_address=comparison_url+frontpage_html


print ''
print '-- The CliMAF ESM Evaluation Platform atlas is available here: '
print '--'
print '--   '+frontpage_address
print '--'
print '--'
print '-- html file can be seen here: '
print '-- '+path_to_comparison_on_web_server+frontpage_html

