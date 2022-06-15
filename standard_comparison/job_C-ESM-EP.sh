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

# -> Separer le cas batch et le cas interactif : identifier les deux

# -- Specify the atlas script
# -------------------------------------------------------- >
atlas_file='main_C-ESM-EP.py'
env_script='setenv_C-ESM-EP.sh'

# -- Cas interactif depuis le repertoire de la comparaison
if [[ $1 != '' ]]; then

  component=${1%/}
  comparison=$(basename $PWD)
  #comparison=$(basename $(dirname $0) | sed 's=/==g')
  env=../${env_script}
  main=../${atlas_file}
  #datasets_setup_file=datasets_setup.py
  # -- Name of the parameter file
  #param_file=${component}/params_${component}.py

else

  # -- comparison, component et WD sont les variables passees avec qsub -v
  echo '$comparison=' $comparison
  echo '$component=' $component
  echo '$WD=' $WD
  echo '$cesmep_frontpage=' $cesmep_frontpage
  echo '$CLIMAF_CACHE=' $CLIMAF_CACHE
  env=../../${env_script}
  main=../../${atlas_file}
  #datasets_setup_file=../datasets_setup.py
  if [[ -n ${WD} ]]; then
     cd $WD
  fi
  component=${component%/}
  # -- Name of the parameter file
  #param_file=params_${component}.py

fi


# -- Setup the environment...
# -------------------------------------------------------- >
source ${env}

# -- Provide a season
# -------------------------------------------------------- >
#season='ANM'

# -- Set CliMAF cache in some special cases (default is to inherit it)
# ------------------------------------------------------------------- >

if [[ -d "/data/scratch/globc" ]] ; then
    export CLIMAF_CACHE=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/climafcache_${component}
    echo ">>> CC= "$CLIMAF_CACHE
else
    export CLIMAF_CACHE
    export TMPDIR=${CLIMAF_CACHE}
fi


# -- Run the atlas...
# -------------------------------------------------------- >
echo "Running ${atlas_file} for season ${season} with parameter file ${param_file}"
echo "Using CliMAF cache = ${CLIMAF_CACHE}"
#echo python ${main} -p ${param_file} --season ${season} --datasets_setup ${datasets_setup_file} --comparison ${comparison}
#python ${main} -p ${param_file} --season ${season} --datasets_setup ${datasets_setup_file} --comparison ${comparison}
python ${main} --comparison ${comparison} --component ${component} --cesmep_frontpage $cesmep_frontpage


