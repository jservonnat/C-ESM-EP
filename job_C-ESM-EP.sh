#!/bin/bash
#set -x
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

# -> # -- On doit pouvoir le soumettre en batch, ou le soumettre en interactif
#         dans le repertoire de la composante

# -- Specify the atlas script
# -------------------------------------------------------- >
atlas_file='main_C-ESM-EP.py'
env_script='setenv_C-ESM-EP.sh'

# -- Cas interactif depuis le repertoire de la comparaison
if [[ $1 != '' ]]; then

  component=${1%/}
  comparison=$(basename $PWD)
  cesmep_frontpage=${2:-null}
  comparison_dir=$(pwd)

else

  # -- Cas batch depuis le répertoire de la composante 
  # -- comparison, component, WD ... sont passees dans l'environnement
  component=${component%/}
  echo '$comparison=' $comparison
  echo '$component=' $component
  echo '$cesmep_frontpage=' $cesmep_frontpage
  comparison_dir=$(cd ..;pwd)
  echo '$WD=' $WD
  if [[ -n ${WD} ]]; then
     cd $WD
  fi
fi

env=$comparison_dir/../setenv_C-ESM-EP.sh
atlas_script=$comparison_dir/../main_C-ESM-EP.py

# -- Setup the environment...
# -------------------------------------------------------- >
source ${env}
# Need to import from comparison directory :
my_append -bp PYTHONPATH $comparison_dir


# -- Set CliMAF cache in some special cases (default is to inherit it)
# ------------------------------------------------------------------- >

if [[ -d "/data/scratch/globc" ]] ; then
    CLIMAF_CACHE=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/climafcache_${component}
fi
export CLIMAF_CACHE
echo ">>> CC= "$CLIMAF_CACHE


# -- Run the atlas...
# -------------------------------------------------------- >
echo "Running ${atlas_file} for season ${season} with parameter file ${param_file} in $(pwd)"
#echo "Using CliMAF cache = ${CLIMAF_CACHE}"

run_main="python ${atlas_script} --comparison ${comparison} --component ${component} --cesmep_frontpage $cesmep_frontpage"

if [ -n "$docker_container" ] ; then
    
    # this implies we are at TGCC) -> using pcocc for running a container 
    irene_tools=/ccc/cont003/home/igcmg/igcmg/Tools/irene

    # Syntax using pcocc, which is for now buggy 
    #env="-e re(CCC.*DIR) -e re(CLIMAF.*) -e PYTHONPATH "
    #env+="-e TMPDIR=${CLIMAF_CACHE} -e LOGNAME "
    #pcocc run -s $env -I $docker_container --cwd $(pwd) <<-EOF

    # Syntax using pcocc-rs
    env="--env re(CCC.*DIR) --env re(CLIMAF.*) --env PYTHONPATH "
    env+="--env TMPDIR=${CLIMAF_CACHE} --env LOGNAME "
    pcocc-rs run $env $docker_container  <<-EOF

	set -x
	umask 0022
	export PATH=\$PATH:$irene_tools  # For thredds_cp
	export PYTHONPATH=/src/climaf:$PYTHONPATH
	$run_main
	EOF

elif [ -n "$singularity_container" ] ; then
    
    # We are probably at IDRIS, and will use singularity
    module load singularity
    # File systems bindings
    binds=$HOME:$HOME,$SCRATCH:$SCRATCH
    # Must bind /gpfswork/rech and /gpfsstore/rech to access data in psl/common
    # and of other projects
    binds+=,/gpfsstore/rech:/gpfsstore/rech,/gpfswork/rech:/gpfswork/rech
    # Must bind /gpfsdswork/projects to mimic a system symbolic link for $WORK
    binds+=,/gpfswork:/gpfsdswork/projects
    # Same for $SCRATCH
    binds+=,/gpfsscratch:/gpfsssd/scratch
    # Must bind /gpfslocalsup/bin for accessing mfthredds and thredds_cp commands
    binds+=,/gpfslocalsup/bin:/gpfslocalsup/bin
    # Must bind /gpfsdsmnt/ipsl/dods/pub for executing thredds_cp
    binds+=,/gpfsdsmnt/ipsl/dods/pub:/gpfsdsmnt/ipsl/dods/pub
    #
    env="TMPDIR=${CLIMAF_CACHE},CLIMAF_CACHE=${CLIMAF_CACHE}"
    env+=",LOGNAME=$LOGNAME"
    #
    set -x
    srun singularity shell --bind $binds --env $env \
        $SINGULARITY_ALLOWED_DIR/$singularity_container <<-EOG
	set -x
	export PATH=/gpfslocalsup/bin:\$PATH
	# CliMAF location may be tuned below. Container default is /src/climaf
	export CLIMAF=/src/climaf
	export PYTHONPATH=\$CLIMAF:$PYTHONPATH
	$run_main
	EOG
    
else
    
    export TMPDIR=${CLIMAF_CACHE}
    $run_main
    
fi

