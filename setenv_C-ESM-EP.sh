#set +x

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
    cesmep_modules=${PWD}/../share/cesmep_modules
elif [[ -d "${PWD}/../../share/cesmep_modules" ]] ; then
    cesmep_modules=${PWD}/../../share/cesmep_modules
fi

# Set CliMAF cache
here=$(cd $(dirname $BASH_ARGV); pwd) #In order to know the dir of present file
cache=$(cd $here ; python -c 'from __future__ import print_function; from locations import climaf_cache; print(climaf_cache)')
export CLIMAF_CACHE=$cache
# export above will be re-done for some cases, further below, e.g. after a "module load climaf"

# --> At TGCC - Irene
if [[ -d "/ccc" && ! -d "/data" ]] ; then
  unset PYTHONPATH
  #module switch python/2.7.15
  # CDO fix
  module unload nco/4.4.8
  module unload netcdf/4.3.3.1_hdf5_parallel
  module unload cdo/1.6.7_netcdf-4.3.2_hdf5
  module unload netcdf-fortran
  #module load netcdf-fortran/4.5.3
  module load netcdf-c/4.6.0
  #module load module load netcdf/4.4.0_hdf5
  module unload cdo
  module load cdo/1.9.5
  module load ncview ncl_ncarg nco
  # CDO fix
  source /ccc/work/cont003/drf/p86jser/miniconda/etc/profile.d/conda.sh
  working_conda=/ccc/work/cont003/drf/p86jser/miniconda/envs/cesmep_env
  conda activate ${working_conda}
  LD_LIBRARY_PATH=${working_conda}/lib:${LD_LIBRARY_PATH}
  export HDF5_DISABLE_VERSION_CHECK=1
  export UVCDAT_ANONYMOUS_LOG=False
  export CLIMAF=$(ccc_home -u igcmg --cccwork)/CliMAF/climaf_V1.2.13_post
  my_append -bp PYTHONPATH ${CLIMAF}
  my_append -bp PATH ${CLIMAF}
  # # -- CDFTools
  # ??
  export myroot=${WORKDIR}

  my_append -bp PATH  $(ccc_home -u p86ipsl)/bin   # Path vers dods_cp

fi

# --> On Ciclad
if [[ -d "/data" && -d "/thredds/ipsl" && ! -d "/scratch/globc"  ]] ; then 
    if [[ $(uname -n) == spirit* ]] ; then
	# --> On Spirit
	#module purge
	echo Loading module cesmep
	set +x
	module load /home/ssenesi/environnements/modules/cesmep
    else
	unset PYTHONPATH
	module load climaf
	module switch climaf/2.0.0-python3.6_test # This sets CLIMAF
	# Must set again CLIMAF_CACHE
	export CLIMAF_CACHE=$cache
	working_conda=/net/nfs/tools/Users/SU/jservon/miniconda3_envs/analyse_3.6_test
	LD_LIBRARY_PATH=${working_conda}/lib:$LD_LIBRARY_PATH
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
    echo ">>> CC= "$CLIMAF_CACHE
    echo ">>> PP= "$PYTHONPATH

    # -- CDFTools
    #my_append -bp PATH /data/home/globc/moine/CDFTOOLS_3.0_forCliMAF/bin
    #echo "PATH ${PATH}"
fi

echo '$CLIMAF_CACHE=' $CLIMAF_CACHE
