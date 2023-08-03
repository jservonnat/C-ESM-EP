#!/bin/bash
######################
## CURIE   TGCC/CEA ##
######################
if [[ -d "/cnrm" ]] ; then
echo "at CNRM"
#SBATCH --partition P8HOST
# Nom du job
#SBATCH --job-name CESMEP
# Temps limite du job
#SBATCH --time=03:00:00
#SBATCH --nodes=1
else
echo "Everywhere else"
#MSUB -r C-ESM-EP_job
#MSUB -eo
#MSUB -n 1              # Reservation du processus
#MSUB -T 36000          # Limite de temps elapsed du job
#MSUB -q standard
##MSUB -Q normal
#MSUB -A devcmip6
fi
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
# -> Separer le cas batch et le cas interactif : identifier les deux

# -- Specify the atlas script
# -------------------------------------------------------- >
atlas_file='PMP_C-ESM-EP.py'
env_script='setenv_C-ESM-EP.sh'


# -- Cas interactif depuis le repertoire de la comparaison
if [[ $1 != '' ]]; then

  ln -s ../cesmep_atlas_style_css
  component=${1%/}
  comparison=$(basename $PWD)
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

# -- Run the atlas...
# ------------------------------------------------------- >
echo "Running Parallel Coordinates metrics for comparison ${comparison}"
echo "Using CliMAF cache = ${CLIMAF_CACHE}"
export PATH=/prodigfs/ipslfs/dods/jservon/anaconda2-5.1.0/bin:/opt/ncl-6.3.0/bin:/opt/netcdf43/gfortran/bin:/home/igcmg/atlas:/home/igcmg/fast:/opt/ferret-6.9/bin:/opt/ferret-6.9/fast:/opt/nco-4.5.2/bin:/usr/lib64/openmpi/1.4.5-ifort/bin:/opt/intel/15.0.6.233/composer_xe_2015.6.233/bin/intel64:/opt/intel/15.0.6.233/composer_xe_2015.6.233/debugger/gdb/intel64_mic/bin:/opt/scilab-5.4.1/bin:/usr/lib64/qt-3.3/bin:/opt/pgi-2013/linux86-64/2013/bin:/opt/matlab-2013b:/opt/matlab-2013b/bin:/opt/intel/composer_xe_2011_sp1.9.293/bin/intel64:/opt/g95-stable-0.92/bin:/opt/ferret-6.7.2/fast:/opt/ferret-6.7.2/bin:/opt/cdfTools-3.0:/opt/canopy-1.3.0/Canopy_64bit/User/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/idl8/idl/bin:/opt/intel/composer_xe_2011_sp1.9.293/mpirt/bin/intel64:/opt/ncl-6.1.2/bin:/home/lvignon/bin:/home/jservon/bin
source activate /data/jservon/PMP_nightly_backup_22062017/PMP_nightly
export LD_LIBRARY_PATH=/data/jservon/PMP_nightly_backup_22062017/PMP_nightly/lib:/prodigfs/ipslfs/dods/jservon/anaconda2-5.1.0/lib:${LD_LIBRARY_PATH}


python3 ${main} --datasets_setup ${datasets_setup_file} --comparison ${comparison} --params ${param_file}


