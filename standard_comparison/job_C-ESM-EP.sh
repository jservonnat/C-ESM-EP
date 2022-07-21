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
  env=$(cd ../..; pwd)/${env_script}
  main=$(cd ../..; pwd)/${atlas_file}
  #datasets_setup_file=../datasets_setup.py
  # -- Name of the parameter file
  #param_file=params_${component}.py
  if [[ -n ${WD} ]]; then
     cd $WD
  fi

fi


# -- Setup the environment...
# -------------------------------------------------------- >
echo '$CESMEP_CLIMAF_CACHE=' $CESMEP_CLIMAF_CACHE
source ${env}
echo '$CLIMAF_CACHE=' $CLIMAF_CACHE

# -- Provide a season
# -------------------------------------------------------- >
#season='ANM'

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
if [ ${with_pcocc:-0} -eq 0 ] ; then

    export TMPDIR=${CLIMAF_CACHE}
    python ${main} --comparison ${comparison} --component ${component} --cesmep_frontpage $cesmep_frontpage

else

    # This implies we are at TGCC -> using pcocc for running a container (named climaf)
    # It needs that the user ran once:
    #    pcocc image import docker-archive:/ccc/work/cont003/gen0826/senesis/docker_archives/climaf.tar climaf
    # We assume that $env_name has been set (by setenv_C-ESM-EP.sh) to the name of the conda
    # environment provided by the climaf container
    
    env="-e re(CCC.*DIR) -e re(CLIMAF.*) -e PYTHONPATH -e TMPDIR=${CLIMAF_CACHE} -e LOGNAME "
    pcocc run -s $env -I climaf --cwd $(pwd) <<-EOF

	# Initialize conda environment for CliMAF and CESMEP
	. /opt/mamba/etc/profile.d/conda.sh
	conda activate $env_name

	set -x
	umask 0022

	# CliMAF version used is usually the one included in the Docker container
	export PYTHONPATH=/src/climaf:\$PYTHONPATH 

	# Need one IGCMG tool (thredds_cp)
	PATH=\$PATH:/ccc/cont003/home/igcmg/igcmg/Tools/irene

	# Run C-ESM-EP main script
	python ${main} --comparison ${comparison} --component ${component} --cesmep_frontpage $cesmep_frontpage

	EOF
fi

