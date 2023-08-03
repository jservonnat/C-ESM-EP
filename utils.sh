#!/bin/bash

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
