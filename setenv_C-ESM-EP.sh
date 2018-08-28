#set +x

# -------------------------------------------------------- >
# --
# -- Script to run a CliMAF atlas on Ciclad:
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

# --> On Curie
if [[ -d "/ccc" && ! -d "/data" ]] ; then
  unset PYTHONPATH
  module switch python/2.7.8
  # CDO fix
  module unload nco/4.4.8
  module unload netcdf/4.3.3.1_hdf5_parallel
  module unload cdo/1.6.7_netcdf-4.3.2_hdf5
  module load netcdf/4.4.0_hdf5
  module load cdo/1.9.2
  module load ncview ncl_ncarg nco
  # CDO fix
  source /ccc/work/cont003/dsm/p86jser/miniconda/etc/profile.d/conda.sh
  working_conda=/ccc/work/cont003/dsm/p86jser/miniconda/envs/cesmep_env
  conda activate ${working_conda}
  LD_LIBRARY_PATH=${working_conda}/lib:${LD_LIBRARY_PATH}
  export HDF5_DISABLE_VERSION_CHECK=1
  export UVCDAT_ANONYMOUS_LOG=False
  export CLIMAF=$(ccc_home -u igcmg --cccwork)/CliMAF/climaf_1.0.3_CESMEP
  my_append -bp PYTHONPATH ${CLIMAF}
  # # -- CDFTools
  export CLIMAF_CACHE=${SCRATCHDIR}/cache_atlas_explorer

  export myroot=${WORKDIR}

  my_append -bp PATH  $(ccc_home -u p86ipsl)/bin   # Path vers dods_cp

fi

# --> On Ciclad
if [[ -d "/data" ]] ; then
  unset PYTHONPATH
  module unload netcdf4
  module load netcdf4/4.3.3.1-gfortran
  module load cdo
  module load ncl/6.3.0
  source /prodigfs/ipslfs/dods/jservon/miniconda/etc/profile.d/conda.sh
  working_conda=/prodigfs/ipslfs/dods/jservon/miniconda/envs/cesmep_env
  conda activate ${working_conda}
  LD_LIBRARY_PATH=${working_conda}/lib:$LD_LIBRARY_PATH
  export HDF5_DISABLE_VERSION_CHECK=1
  export UVCDAT_ANONYMOUS_LOG=False
  export CLIMAF=/home/jservon/Evaluation/CliMAF/climaf_installs/climaf_1.0.3_CESMEP
  my_append -bp PYTHONPATH ${CLIMAF}
  my_append -bp PATH ${CLIMAF}
  export CLIMAF_CACHE=/prodigfs/ipslfs/dods/${USER}/atlas_explorer
  # -- CDFTools
  my_append -bp PATH /home/lvignon/bin
  my_append -bp PATH ${CLIMAF}/bin
  #export PATH=/prodigfs/ipslfs/dods/jservon/miniconda/envs/cesmep_env/bin:/home/igcmg/atlas:/home/igcmg/fast:/opt/scilab-5.4.1/bin:/usr/lib64/qt-3.3/bin:/opt/pgi-2013/linux86-64/2013/bin:/opt/matlab-2013b:/opt/matlab-2013b/bin:/opt/intel/composer_xe_2011_sp1.9.293/bin/intel64:/opt/g95-stable-0.92/bin:/opt/ferret-6.7.2/fast:/opt/ferret-6.7.2/bin:/opt/cdfTools-3.0:/opt/canopy-1.3.0/Canopy_64bit/User/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/idl8/idl/bin:/opt/intel/composer_xe_2011_sp1.9.293/mpirt/bin/intel64:/opt/ncl-6.1.2/bin:/home/lvignon/bin:/home/jservon/bin:/opt/idl8/idl/bin:/opt/intel/composer_xe_2011_sp1.9.293/mpirt/bin/intel64:/opt/ncl-6.1.2/bin:/home/lvignon/bin:/home/jservon/bin
  echo "PATH ${PATH}"
fi
