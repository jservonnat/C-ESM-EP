#!/bin/bash
######################
## CURIE   TGCC/CEA ##
######################
#MSUB -r C-ESM-EP_job
#MSUB -eo
#MSUB -n 1              # Reservation du processus
#MSUB -T 36000          # Limite de temps elapsed du job
#MSUB -q standard
##MSUB -Q normal
#MSUB -A devcmip6
set +x
# -------------------------------------------------------- >
# --
# -- Script to run a CliMAF atlas on Ciclad:
# --   - sets up the environment
# --   - specify the parameter file and the season
# --   - automatically sets up the CliMAF cache
# --   - and run the atlas
# --
# --
# --     Author: Jerome Servonnat
# --     Contact: jerome.servonnat__at__lsce.ipsl.fr
# --
# --
# -------------------------------------------------------- >
date


# -- On doit pouvoir le soumettre en batch, ou le soumettre en interactif dans le repertoire de la composante
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
  datasets_setup_file=datasets_setup.py
  # -- Name of the parameter file
  param_file=${component}/params_${component}.py

else

  # -- comparison, component et WD sont les variables passees avec qsub -v
  echo '$comparison'
  echo $comparison
  echo '$component'
  echo $component
  echo '$WD'
  echo $WD
  env=../../${env_script}
  main=../../${atlas_file}
  datasets_setup_file=../datasets_setup.py
  if [[ -n ${WD} ]]; then
     cd $WD
  fi
  component=${component%/}
  # -- Name of the parameter file
  param_file=params_${component}.py

fi


# -- Setup the environment...
# -------------------------------------------------------- >
source ${env}

# -- Provide a season
# -------------------------------------------------------- >
season='ANM'

# -- Set CliMAF cache (automatically)
# -------------------------------------------------------- >
if [[ -d "/ccc" && ! -d "/data" ]]; then
export CLIMAF_CACHE=${SCRATCHDIR}/climafcache_${component}_${season}
fi

if [[ -d "/data" ]]; then
export CLIMAF_CACHE=/prodigfs/ipslfs/dods/${USER}/climafcache_${component}_${season}
fi

# -- Run the atlas...
# -------------------------------------------------------- >
echo "Running ${atlas_file} for season ${season} with parameter file ${param_file}"
echo "Using CliMAF cache = ${CLIMAF_CACHE}"
python ${main} -p ${param_file} --season ${season} --datasets_setup ${datasets_setup_file} --comparison ${comparison}


