#!/bin/bash
#set +x
#set -e

# -------------------------------------------------------- >
# --
# -- Script to run a CliMAF atlas :
# --   - sets up the environment
# --
# --     Author: Jerome Servonnat
# --     Contact: jerome.servonnat__at__lsce.ipsl.fr
# --
# -------------------------------------------------------- >
if [ -z $BASH_ARGV ] ; then
    echo "This script must be sourced. Type "
    echo "  . $0"
    exit
fi
date
directory_of_this_script=$(cd $(dirname $BASH_ARGV); pwd)

# Here, script install_lite.sh may set (or have set) a value for
# 'root', to a directory hosting the full C-ESM-EP code. This allow to
# have light installs. Otherwise, 'root' is set to the directory
# of current script, which is fine if it hosts a full code set

#root=                             #HERE
root=${root:-$directory_of_this_script}

# -- Source useful functions (my_append..)
source $root/utils.sh

# -- Setup the environment...
# -------------------------------------------------------- >

# --> At TGCC - Irene
if [[ -d "/ccc" && ! -d "/data" ]] ; then
    export atTGCC=1
    export irene_tools=/ccc/cont003/home/igcmg/igcmg/Tools/irene
    my_append -ep PATH $irene_tools
    export CLIMAF=/ccc/cont003/home/igcmg/igcmg/Tools/climaf
    my_append -bp PYTHONPATH $CLIMAF
    # How to find environment container, and which container to use
    export PCOCC_CONFIG_PATH=/ccc/work/cont003/igcmg/igcmg/climaf_python_docker_archives/.config/pcocc
    export CESMEP_CONTAINER=${CESMEP_CONTAINER:-"ipsl:cesmep_container"}
fi

# --> At IDRIS - Jean-Zay
if [[ -d "/gpfsdswork" ]]; then
    echo "loading module singularity"
    set +x
    module load singularity
    if [ -z $singularity_container ]
    then
	# identify one container among those managed by idrcontmgr
	export singularity_container=$(idrcontmgr ls | /usr/bin/grep sif | tail -n -1)
    fi
    if [ -z $singularity_container ] 
    then
	echo -e"\n\nBefore your first run of C-ESM-EP at IDRIS, you must "
	echo -e "declare the singularity container that satisfies C-ESM-EP "
	echo -e "prerequisites, by issuing (only once) these commands :"
	echo -e "\n\t module load singularity"
	echo -e "\t idrcontmgr cp /gpfswork/rech/psl/commun/Tools/cesmep_environment/<file>\n"
	echo -e "\n where <file> is the newest '.sif' file in that Tools directory"
	exit 1
    fi
    my_append -bp PYTHONPATH /gpfswork/rech/psl/commun/Tools/climaf
fi

# --> On Spirit
if [[ -d "/data" && -d "/thredds/ipsl" && ! -d "/scratch/globc"  ]] ; then 
    if [[ $(uname -n) == spirit* ]] ; then
	emodule=${CESMEP_CLIMAF_MODULE:-env20240920_climafV3.1_IPSL15}
	if [ ${emodule:0:1} != "/" ]; then
	    prefix=/net/nfs/tools/Users/SU/modulefiles/jservon/climaf
	    emodule=$prefix/$emodule
	fi
	echo Loading module $emodule for CliMAF and C-ESM-EP
	set +x
	module purge
	module load $emodule || exit
	# If one wants to use an alternate CLiMAF version
	#export PYTHONPATH=~/climaf_installs/climaf_running:$PYTHONPATH
    else
	echo "C-ESM-EP is not maintained on system $(uname -n)"
	exit 1
    fi
fi

# Obelix at LSCE
if [[ -d "/home/orchideeshare/"  ]] ; then
    
    # We are using a conda environment
    export ENV=/home/orchideeshare/igcmg/Tools/miniforge3/envs/20250128
    export PATH=$ENV/bin:$ENVS/../../bin:$PATH
    export LD_LIBRARY_PATH=$ENV/lib:$LD_LIBRARY_PATH
    export NCARG_ROOT=$ENV
    export PROJ_DATA=$ENV/proj
    export PYPROJ_GLOBAL_CONTEXT=ON
    export HDF5_DISABLE_VERSION_CHECK=1

    # One could design a module 'cesmep' reproducing the sequence above
    # Next 3 lines would then be useful
    #
    #. /usr/share/Modules/init/ksh # Acces to module command
    #module purge
    #module load cesmep

    # Next sequence, which uses conda.sh and conda activate, also works
    #
    # Initialize the current bash shell 
    #export MAMBA_ROOT_PREFIX=/home/orchideeshare/igcmg/Tools/miniforge3
    #source $MAMBA_ROOT_PREFIX/etc/profile.d/conda.sh
    # Activate the relevant environment
    #echo -n "Activating the conda environment may take up to 15s on obelix..."
    #conda activate 20250128
    #echo

    # Set which CliMAF is used
    export CLIMAF=/home/orchideeshare/igcmg/Tools/cesmep/climaf_code
    # One may change the CliMAF version used:
    export CLIMAF=~/climaf
    
    export PYTHONPATH=$CLIMAF:$PYTHONPATH
fi

# --> At CNRM
if [[ -d "/cnrm" ]] ; then   
    unset PYTHONPATH

    # CliMAF
    export CLIMAF=/cnrm/est/COMMON/climaf/current
    my_append -bp PYTHONPATH /cnrm/est/COMMON/climaf/add_packages/lib/python3.10/site-packages/
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PATH ${CLIMAF}/bin
fi


# --> At Cerfacs on Scylla
if [[ -d "/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP" ]] ; then
        echo "We work at Cerfacs on Scylla"
    unset PYTHONPATH

    # CDAT
    source /data/softs/python2/venvs/cesmep1.0/bin/activate
    export HDF5_DISABLE_VERSION_CHECK=1
    export UVCDAT_ANONYMOUS_LOG=False

    # CliMAF
    export CLIMAF=/data/scratch/globc/dcom/CMIP6_TOOLS/climaf
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PATH ${CLIMAF}/bin
    export CLIMAF_CACHE=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/climafcache_${component}
fi


# --> At Cerfacs on kraken
if [[ -d "/scratch/globc/coquart/C-ESM-EP" ]] ; then
        echo "We work at Cerfacs on Kraken"
    unset PYTHONPATH
    module load tools/cdo/1.9.5
    module load tools/nco/4.7.6

    # CDAT
    module load python/anaconda2.7
    source activate CESMEP
    CONDA=/softs/anaconda2
    my_append -bp LD_LIBRARY_PATH ${CONDA}/lib
    my_append -bp PYTHONPATH ${CONDA}/lib/python2.7/site-packages
    my_append -bp PATH $CONDA/bin
    export HDF5_DISABLE_VERSION_CHECK=1
    export UVCDAT_ANONYMOUS_LOG=False

    # CliMAF
    export CLIMAF=/scratch/globc/coquart/climaf
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PATH ${CLIMAF}/bin
fi

# Complement PYTHONPATH and PATH
my_append -bp PYTHONPATH ${root}/share/cesmep_modules
my_append -bp PYTHONPATH ${root}
my_append -bp PYTHONPATH ${directory_of_this_script}
#
my_append -bp PATH ${root}

# Set CliMAF cache
export CLIMAF_CACHE=$(python3 -c 'from locations import climaf_cache; print(climaf_cache)')

echo
echo "Environment settings for C-ESM-EP"
echo "---------------------------------"
echo CLIMAF_CACHE        = $CLIMAF_CACHE
echo CESMEP_CLIMAF_CACHE = $CESMEP_CLIMAF_CACHE
echo PYTHONPATH          = $PYTHONPATH
[ ! -z $CESMEP_CONTAINER ] && echo CESMEP_CONTAINER     = $CESMEP_CONTAINER
echo 
