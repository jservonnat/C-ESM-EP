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
    export LC_ALL=C.UTF-8  # Needed by pcocc (actually by Click in python 3.6)
    export LANG=C.UTF-8    # Needed by pcocc (actually by Click in python 3.6)
    my_append -ep PATH /ccc/cont003/home/igcmg/igcmg/Tools/irene 
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
	echo -e"\n\nBefore you firt run of C-ESM-EP at IDRIS, you must "
	echo -e "declare the singularity container that satisfies C-ESM-EP "
	echo -e "prerequisites, by issuing (only once) these commands :"
	echo -e "\n\t module load singularity"
	echo -e "\t idrcontmgr cp /gpfswork/rech/psl/commun/Tools/cesmep_environment/<file>\n"
	echo -e "\n where <file> is the newest '.sif' file in that Tools directory"
	exit 1
    fi
fi

# --> On Spirit
if [[ -d "/data" && -d "/thredds/ipsl" && ! -d "/scratch/globc"  ]] ; then 
    if [[ $(uname -n) == spirit* ]] ; then
	emodule=/net/nfs/tools/Users/SU/modulefiles/jservon/climaf/env20230611_climafV3.0_IPSL9
	echo Loading module $emodule for CliMAF and C-ESM-EP
	set +x
	module purge
	module load $emodule
    else
	echo "C-ESM-EP is not maintained on system $(uname -n)"
	exit 1
    fi
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

my_append -bp PATH ${root}

# Set CliMAF cache
export CLIMAF_CACHE=$(python3 -c 'from locations import climaf_cache; print(climaf_cache)')

echo
echo "Environment settings for C-ESM-EP"
echo "---------------------------------"
echo CLIMAF_CACHE        = $CLIMAF_CACHE
echo CESMEP_CLIMAF_CACHE = $CESMEP_CLIMAF_CACHE
#echo PATH                = $PATH
echo PYTHONPATH          = $PYTHONPATH
echo 
