#!/bin/python
import os, sys
import getpass
import re

WD=os.getcwd()

username=getpass.getuser()
if username=='fabric':
   username2 = str.split(os.getcwd(),'/')[4]
else:
   username2 = username

# -- 0/ Identify where we are...
# -----------------------------------------------------------------------------------------
atTGCC   = False
onCiclad = False


# -- 1/ Get the arguments / Name of the comparison (comparison)
# --    and components to be run (components)
# -----------------------------------------------------------------------------------------
args = sys.argv

metrics_components = ['ParallelCoordinates_Atmosphere']
allcomponents=['ParallelCoordinates_Atmosphere','Atmosphere_Surface','Atmosphere_StdPressLev','Atmosphere_zonmean','NEMO_main','NEMO_zonmean','Atlantic_Atmosphere_Surface','Focus_Atlantic_AMOC_Surface','PISCES','ENSO','Monsoons','ORCHIDEE','TurbulentAirSeaFluxes', 'AtlasExplorer','Essentials_CM6011_CM6012']

if len(args)==1:
   print 'Provide the name of a comparison setup as argument of the script'
else:
   comparison=str.replace(args[1],'/','')
   argument='None'
   if len(args)==3:
      argument=args[2]
      if argument in ['OA']:
         if argument=='OA': components = ['Atmosphere_Surface','Atmosphere_zonmean','NEMO_main','NEMO_zonmean','Atlantic_Atmosphere_Surface','ENSO','PISCES']
      elif  argument.lower() in ['url']:
         components=allcomponents
      else:
         components=str.split(argument,',')
   else:
      components=allcomponents


# -- 2/ Set the paths (one per requested component)
# -----------------------------------------------------------------------------------------
if os.path.exists ('/ccc') and not os.path.exists ('/data')  :
    atTGCC   = True
    base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/work/'
    pathwebspace='/ccc/work/cont003/dods/public/'
if 'ciclad' in os.uname()[1].strip().lower():
    onCiclad = True
    base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/IPSLFS/'
    pathwebspace='/prodigfs/ipslfs/dods/'

suffix = username+'/C-ESM-EP/'+comparison+'_'+username2+'/'
root_url = base_url + suffix
webspace = pathwebspace + suffix


if not os.path.isdir(webspace):
   os.makedirs(webspace)


# -- 2/ Submit the jobs (one per requested component) 
# -----------------------------------------------------------------------------------------

# -- Loop on the components
for component in components:
    print 'component = ',component
    # -- Define where the directory where the job is submitted
    submitdir = WD+'/'+comparison+'/'+component
    #
    # -- Build the command line that will submit the job
    # ---------------------------------------------------
    # -- Case atTGCC
    if atTGCC:
       cmd=''
       if component not in metrics_components:
          cmd = 'cd '+submitdir+' ; export comparison='+comparison+' ; export component='+component+' ; ccc_msub -r '+component+'_'+comparison+'_C-ESM-EP ../job_C-ESM-EP.sh ; cd -'
    # -- Case onCiclad
    if onCiclad:
       # -- For all the components but for the parallel coordinates, we do this...
       if component not in metrics_components:
          if 'NEMO' in component or 'Turbulent' in component:
             queue = 'days3 -l mem=30gb -l vmem=32gb'
          else:
             queue = 'h12'
          cmd = 'cd '+submitdir+' ; qsub -q '+queue+' -v component='+component+',comparison='+comparison+',WD=${PWD} -N '+component+'_'+comparison+'_C-ESM-EP ../job_C-ESM-EP.sh ; cd -'
       else:
          # -- ... and for the parallel coordinates, we do that.
          cmd = 'cd '+submitdir+' ; qsub -q h12 -v component='+component+',comparison='+comparison+',WD=${PWD} -N '+component+'_'+comparison+'_C-ESM-EP ../job_PMP_C-ESM-EP.sh ; cd -'
    #
    # -- If the user provides URL or url as an argument (instead of components), the script only returns the URL of the frontpage
    # -- Otherwise it submits the jobs
    # ----------------------------------------------------------------------------------------------------------------------------
    if argument.lower() not in ['url']:
       print cmd
       os.system(cmd)



# -- 3/ Create the C-ESM-EP html front page for 'comparison' from the template 
# -----------------------------------------------------------------------------------------
season='ANM'

# -- Copy the template and rename it with the comparison name
main_html='C-ESM-EP_'+comparison+'.html'
cmd = 'cp share/fp_template/C-ESM-EP_template.html '+main_html
os.system(cmd)

# -- Def pysed
def pysed(file, old_pattern, new_pattern):
    with open(file, "r") as sources:
         lines = sources.readlines()
    with open(file, "w") as sources:
         for line in lines:
             sources.write(re.sub(old_pattern, new_pattern, line))
    return ''


# -- Loop on the components and edit the html file with pysed
for component in allcomponents:
    if component not in metrics_components:
       url = root_url+component+'_'+season+'/atlas_'+component+'_'+comparison+'_'+season+'.html'
    else:
       url = root_url+component+'/'+component+'_'+comparison+'.html'
    pysed(main_html, 'target_'+component, url)

# -- Edit the comparison name
pysed(main_html, 'target_comparison', comparison)


# -- Copy the edited html front page
if atTGCC:
   if '/dsm/' in os.getcwd(): wspace='dsm'
   if '/gencmip6/' in os.getcwd(): wspace='gencmip6'
   outworkdir = '/ccc/work/cont003/'+wspace+'/'+username+'/C-ESM-EP/out/'+comparison+'_'+username+'/'
   if not os.path.isdir(outworkdir): os.makedirs(outworkdir)
   cmd1 = 'cp '+main_html+' '+outworkdir ; print cmd1 ; os.system(cmd1)
   cmd = 'dods_cp '+outworkdir+main_html+' '+webspace+' ; rm '+main_html
if onCiclad: cmd = 'mv '+main_html+' '+webspace
os.system(cmd)


# -- Copy the top image
if not os.path.isfile(webspace+'/CESMEP_bandeau.png'):
   if atTGCC:
      os.system('cp share/fp_template/CESMEP_bandeau.png '+outworkdir)
      cmd='dods_cp '+outworkdir+'CESMEP_bandeau.png '+webspace
   if onCiclad: cmd='cp share/fp_template/CESMEP_bandeau.png '+webspace
   os.system(cmd)

# -- Print the final message with the address of the C-ESM-EP front page
address=root_url+main_html


print ''
print '-- The CliMAF ESM Evaluation Platform will be available here: '
print '--'
print '--   '+address
print '--'
print '--'
print '-- html file can be seen here: '
print '-- '+webspace+main_html

