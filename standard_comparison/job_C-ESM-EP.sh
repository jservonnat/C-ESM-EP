#!/bin/bash
set -x
# -------------------------------------------------------- >
# --
# -- Script to run a CliMAF atlas on Ciclad, TGCC, CNRM, Spirit....
# --   - sets up the environment, except batch system specific ones which are
#          assumed to be set on the submit command 
# --   - specify the parameter file and the season
# --   - sets the CliMAF cache for special cases
# --   - and run the atlas
# --
# --
# --     Author: Jerome Servonnat
# --     Contact: jerome.servonnat__at__lsce.ipsl.fr
# --
# --
# -------------------------------------------------------- >
date

# -> # -- On doit pouvoir le soumettre en batch, ou le soumettre en interactif dans le repertoire de la composante

# -- Specify the atlas script
# -------------------------------------------------------- >
atlas_file='main_C-ESM-EP.py'
env_script='setenv_C-ESM-EP.sh'

# -- Cas interactif depuis le repertoire de la comparaison
if [[ $1 != '' ]]; then

  component=${1%/}
  comparison=$(basename $PWD)
  #comparison=$(basename $(dirname $0) | sed 's=/==g')
  env=$(cd ../; pwd)/${env_script}
  main=$(cd ../; pwd)/${atlas_file}
  #datasets_setup_file=datasets_setup.py
  # -- Name of the parameter file
  #param_file=${component}/params_${component}.py

else

  # -- comparison, component, WD ... sont les variables passees avec qsub -v
  component=${component%/}
  echo '$comparison=' $comparison
  echo '$component=' $component
  echo '$WD=' $WD
  echo '$cesmep_frontpage=' $cesmep_frontpage
  if [[ -n ${WD} ]]; then
     cd $WD
  fi
  env=$(cd ../..; pwd)/${env_script}
  main=$(cd ../..; pwd)/${atlas_file}
fi


# -- Setup the environment...
# -------------------------------------------------------- >
echo 'CESMEP_CLIMAF_CACHE=' $CESMEP_CLIMAF_CACHE
source ${env}
echo 'CLIMAF_CACHE=' $CLIMAF_CACHE
# Need to import from comparison directory :
my_append -bp PYTHONPATH $(cd ..; pwd)


# -- Set CliMAF cache in some special cases (default is to inherit it)
# ------------------------------------------------------------------- >

if [[ -d "/data/scratch/globc" ]] ; then
    CLIMAF_CACHE=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/climafcache_${component}
fi
export CLIMAF_CACHE
echo ">>> CC= "$CLIMAF_CACHE


# -- Run the atlas...
# -------------------------------------------------------- >
echo "Running ${atlas_file} for season ${season} with parameter file ${param_file}"
#echo "Using CliMAF cache = ${CLIMAF_CACHE}"
run_main="python ${main} --comparison ${comparison} --component ${component} --cesmep_frontpage $cesmep_frontpage"

if [ -n "$docker_container" ] ; then
    
    # this implies we are at TGCC) -> using pcocc for running a container 
    env="-e re(CCC.*DIR) -e re(CLIMAF.*) -e PYTHONPATH "
    env+="-e TMPDIR=${CLIMAF_CACHE} -e LOGNAME "
    pcocc run -s $env -I $docker_container --cwd $(pwd) <<-EOF
	set -x
	umask 0022
	PATH=\$PATH:/ccc/cont003/home/igcmg/igcmg/Tools/irene 	# For thredds_cp
	$run_main
	EOF

elif [ -n "$singularity_container" ] ; then
    
    # We are probably at IDRIS, and will use singularity
    module load singularity
    # File systems bindings
    binds=$SCRATCH:$SCRATCH
    # Must bind /gpfswork/rech and /gpfsstore/rech to access data in psl/commun
    # and of other projects
    binds+=,/gpfsstore/rech:/gpfsstore/rech,/gpfswork/rech:/gpfswork/rech
    # Must bind /gpfsdswork/projects to mimic a system symbolic link for $WORK
    binds+=,/gpfswork:/gpfsdswork/projects
    # Must bind /gpfslocalsup/bin for accessing mfthredds and thredds_cp commands
    binds+=,/gpfslocalsup/bin:/gpfslocalsup/bin
    # Must bind /gpfsdsmnt/ipsl/dods/pub for executing thredds_cp
    binds+=,/gpfsdsmnt/ipsl/dods/pub:/gpfsdsmnt/ipsl/dods/pub
    #
    env="CLIMAF=$WORK/climaf,PYTHONPATH=$WORK/climaf:$PYTHONPATH"
    #env="PYTHONPATH=$PYTHONPATH"
    env+=",TMPDIR=${CLIMAF_CACHE},CLIMAF_CACHE=${CLIMAF_CACHE}"
    env+=",LOGNAME=$LOGNAME"
    #
    set -x
    srun --mpi=pmix_v2 singularity shell --bind $binds --env $env \
        $SINGULARITY_ALLOWED_DIR/$singularity_container <<-EOG
	set -x
	export PATH=/gpfslocalsup/bin:\$PATH
	$runmain
	EOG
    
else
    
    export TMPDIR=${CLIMAF_CACHE}
    $run_main
    
fi

