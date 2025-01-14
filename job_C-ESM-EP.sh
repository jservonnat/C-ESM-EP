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

if [ ${atTGCC:-0} -eq 1 ] ; then
    
    export irene_tools=/ccc/cont003/home/igcmg/igcmg/Tools/irene
    export PCOCC_CONFIG_PATH=/ccc/work/cont003/igcmg/igcmg/climaf_python_docker_archives/.config/pcocc
    CESMEP_CONTAINER=${CESMEP_CONTAINER:-"ipsl:cesmep_container"}
    env="--env re(CCC.*DIR) --env re(CLIMAF.*) --env PYTHONPATH "
    env+="--env TMPDIR=${CLIMAF_CACHE} --env LOGNAME --env SLURM_JOBID "
    pcocc-rs run $env $CESMEP_CONTAINER  <<-EOF

	set -x
	umask 0022
	export PATH=\$PATH:$irene_tools  # For thredds_cp
	$run_main
	EOF

elif [ -n "$singularity_container" ] ; then
    
    # We are probably at IDRIS, and will use singularity
    module load singularity
    # File systems bindings
    binds=$HOME,$SCRATCH
    binds+=,/lustre/fswork/projects/rech/psl
    binds+=,/lustre/fswork/projects/rech/psl:/gpfswork/rech/psl
    binds+=,/gpfslocalsys
    #
    env="TMPDIR=${CLIMAF_CACHE},CLIMAF_CACHE=${CLIMAF_CACHE}"
    env+=",LOGNAME=$LOGNAME,PYTHONPATH=$PYTHONPATH"
    env+=",SLURM_JOBID=$SLURM_JOBID"
    #
    set -x
    srun singularity shell --bind $binds --env $env \
        $SINGULARITY_ALLOWED_DIR/$singularity_container <<-EOG
	set -x
	export PATH=/gpfslocalsup/bin:\$PATH
	$run_main
	EOG
    
else
    
    export TMPDIR=${CLIMAF_CACHE}
    export PYTHONPATH
    $run_main
    
fi

