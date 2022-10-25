#set +x
set -e

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

# -- Useful functions
function my_append { 
    function my_append_usage {
	echo "Function my_append (in .bash_login)"
	echo "Append/prepend a string to a variable"
	echo "Use to set PATH variables"
	echo "Usage : my_append [bexdpvh] -[-s sep] VAR DIR"
	echo "        my_append -ep PATH /usr/bin"
	echo "        my_append -bv FER_GO ${HOME}/GRAF/FERRET/GO"
	echo "        -v : variable type, separator=[space] (default)"
	echo "        -p : path type, separator=:"
	echo "        -s sep : choose altenate separator"
	echo "        -b : prepend at begining"
	echo "        -e : append at end (default)"
	echo "        -x : check that directory is executable"
	echo "        -d : check that directory exists"
}
    local l_sep=" " l_order="end" l_check_dir="no" l_check_exe="no"
    local name OPTIND OPTARG OPTNAME l_return=0
    while getopts bexds:pvh OPTNAME ; do
 	case ${OPTNAME} in
	    ( h ) my_append_usage   ;;
            ( b ) l_order="beg"     ;;
            ( e ) l_order="end"     ;;
	    ( x ) l_check_exe="yes" ;;
	    ( d ) l_check_dir="yes" ;;
            ( s ) l_sep=${OPTARG}   ;;
	    ( p ) l_sep=":"         ;;
	    ( v ) l_sep=" "         ;;
	esac
    done
    shift $(( ${OPTIND} - 1 ))

    [[ ${#} -lt 2 || -z ${2} ]]  && return
    [[ ${l_check_dir} = "yes" ]] && [[ ! -d ${2} ]] && return
    [[ ${l_check_exe} = "yes" ]] && [[ ! -x ${2} ]] && return
	    
    if [[ $(printenv ${1}) = "" ]] ; then
	eval "export ${1}=${2}"
    else
        if ! eval test -z "\"\${$1##*${l_sep}$2${l_sep}*}\"" -o -z "\"\${$1%%*${l_sep}$2}\"" -o -z "\"\${$1##$2${l_sep}*}\"" -o -z "\"\${$1##$2}\""  ; then
	    [[ ${l_order} = "end" ]] && eval "$1=\"\$$1${l_sep}$2\""
	    [[ ${l_order} = "beg" ]] && eval "$1=\"$2${l_sep}\$$1\""
        fi
    fi
}

# -- Setup the environment...
# -------------------------------------------------------- >

if [[ -d "${PWD}/share/cesmep_modules" ]] ; then
    cesmep_modules=${PWD}/share/cesmep_modules
elif [[ -d "${PWD}/../share/cesmep_modules" ]] ; then
    cesmep_modules=$(cd ${PWD}/../share/cesmep_modules; pwd)
elif [[ -d "${PWD}/../../share/cesmep_modules" ]] ; then
    cesmep_modules=$(cd ${PWD}/../../share/cesmep_modules; pwd)
fi

# --> At TGCC - Irene
if [[ -d "/ccc" && ! -d "/data" ]] ; then
    # container to use for setting the environment
    prerequisites_container=cesmep_container    
    if ! pcocc image show $prerequisites_container > /dev/null 2>&1 ; then
	echo -e"\n\nBefore you firt run of C-ESM-EP at TGCC, you must tell pcocc which is the Docker "
	echo "container that satisfies C-ESM-EP prerequisites, by issuing (only once) a command like"
	echo -e "\n\t pcocc image import docker-archive:\$container_archive $prerequisites_container\n"
	echo -e "where \$container_archive could possibly be :"
	echo -e "\t~igcmg/Tools/climaf/climaf_spirit_a.tar"
	echo -e "(if it seems wrong, ask your C-ESM-EP guru for the up-to-date location)"
	exit 1
    fi
    CLIMAF=/src/climaf  # This is Climaf location in container
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PYTHONPATH ${cesmep_modules}
fi

# --> On Ciclad or Spirit
if [[ -d "/data" && -d "/thredds/ipsl" && ! -d "/scratch/globc"  ]] ; then 
    if [[ $(uname -n) == spirit* ]] ; then
	# --> On Spirit
	emodule=/net/nfs/tools/Users/SU/modulefiles/jservon/climaf/spirit_0
	echo Loading module $emodule for CliMAF and C-ESM-EP
	set +x
	module purge
	module load $emodule
    else
	unset PYTHONPATH
	module load climaf
	module switch climaf/2.0.0-python3.6_test # This sets CLIMAF
	working_conda=/net/nfs/tools/Users/SU/jservon/miniconda3_envs/analyse_3.6_test
	LD_LIBRARY_PATH=${working_conda}/lib:$LD_LIBRARY_PATH
	CLIMAF=/home/ssenesi/climaf_installs/climaf_running
	my_append -bp PATH ${CLIMAF}
	my_append -bp PATH ${CLIMAF}/bin
	my_append -bp PYTHONPATH ${CLIMAF}
	# -- CDFTools
	my_append -bp PATH /home/lvignon/bin
	# Others
	export HDF5_DISABLE_VERSION_CHECK=1
	export UVCDAT_ANONYMOUS_LOG=False
    fi
    #
    set +x
    my_append -bp PYTHONPATH ${cesmep_modules}
    echo "PATH ${PATH}"
fi

# --> At CNRM
if [[ -d "/cnrm" ]] ; then
   
    unset PYTHONPATH

    # CDAT
    CONDA=/cnrm/est/COMMON/conda2/
    source $CONDA/etc/profile.d/conda.sh
    working_conda=$CONDA/envs/cdat_env
    conda activate ${working_conda}
    my_append -bp LD_LIBRARY_PATH ${working_conda}/lib
    my_append -bp PYTHONPATH ${working_conda}/lib/python2.7/site-packages
    my_append -bp PATH $CONDA/bin
    export HDF5_DISABLE_VERSION_CHECK=1
    export UVCDAT_ANONYMOUS_LOG=False

    # CliMAF
    export CLIMAF=/cnrm/est/COMMON/climaf/current
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PYTHONPATH ${cesmep_modules}
    my_append -bp PATH ${CLIMAF}/bin

    # -- CDFTools
    my_append -bp PATH /cnrm/est/COMMON/CDFTOOLS_3.0/bin
    echo "PATH ${PATH}"
    echo "PYTHONPATH ${PYTHONPATH}"
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
    export cesmep_modules=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/share/cesmep_modules
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PYTHONPATH ${cesmep_modules}
    my_append -bp PATH ${CLIMAF}/bin
    export CLIMAF_CACHE=/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/climafcache_${component}
    echo ">>> CC= "$CLIMAF_CACHE
    echo ">>> PP= "$PYTHONPATH

    # -- CDFTools
    #my_append -bp PATH /data/home/globc/moine/CDFTOOLS_3.0_forCliMAF/bin
    #echo "PATH ${PATH}"
fi


# --> At Cerfacs on kraken
if [[ -d "/scratch/globc/coquart/C-ESM-EP" ]] ; then
        echo "We work at Cerfacs on Kraken"

    unset PYTHONPATH

    # CDO
    module load tools/cdo/1.9.5

    # NCO
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
    export cesmep_modules=/scratch/globc/coquart/C-ESM-EP/share/cesmep_modules
    my_append -bp PYTHONPATH ${CLIMAF}
    my_append -bp PYTHONPATH ${cesmep_modules}
    my_append -bp PATH ${CLIMAF}/bin
    echo ">>> PP= "$PYTHONPATH

    # -- CDFTools
    #my_append -bp PATH /data/home/globc/moine/CDFTOOLS_3.0_forCliMAF/bin
    #echo "PATH ${PATH}"
fi

# Set CliMAF cache
here=$(cd $(dirname $BASH_ARGV); pwd) #In order to know the dir of present file
cache=$(cd $here ; python3 -c 'from locations import climaf_cache; print(climaf_cache)')
if [[ ! "$CLIMAF_CACHE" = /data/scratch/globc/* ]] ; then  # special case for Cerfacs
    export CLIMAF_CACHE=$cache
fi

echo CLIMAF_CACHE = $CLIMAF_CACHE
echo CESMEP_CLIMAF_CACHE = $CESMEP_CLIMAF_CACHE

