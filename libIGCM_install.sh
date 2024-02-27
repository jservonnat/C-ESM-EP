#!/bin/bash

# Helper script for preparing C-ESM-EP runs on IPSL-CM outputs,
# to be launched by libIGCM during a simulation

# It is called by libIGCM at the stage of simulation preparation (ins_job), and
# installs a (lite) C-ESM-EP directory in SUBMIT directory.
# It then creates there :
#    - a relevant datasets_setups.py file (by copying a fixed file)
#    - a settings file (libIGCM_settings.py) imported by that datasets_setup.py file
#    - libIGCM_post.sh : a script that will be called by libIGCM during simulation
#    - a relevant entry for 'account' and for 'mail' in file settings.py

# The created script activates a set of components which matches the type of experiment

#set -x

# LibIGCM provided parameters
target=$1            # Directory where C-ESM-EP  should be installed
comparison=$2        # Which C-ESM-EP 'comparison' will be run
jobname=$3           # Used as a prefix for comparison's name
R_SAVE=$4            # Directory holding simulation outputs 
ProjectId=${5:-None} # Which project ressource allocation should be charged
MailAdress=$6        # Mail adress as in libIGCM
DateBegin=$7         # Start date for the simulation
ConfigCesmep=$8      # Value of config.card Post section variable Cesmep
CesmepPeriod=$9      # Period for atlas time slices
CesmepSlices=${10}   # Number of atlas time slices
Components=${11}     # List of activated components
Center=${12:-TGCC}   # Which computing center are we running on
CesmepSlicesDuration=${13:-$CesmepPeriod}   # Duration of an atlas time slice
CesmepReferences=${14:-NONE} # Paths for the references simulation (with period suffix). A comma separated list

# This script can be called from anywhere
dir=$(cd $(dirname $0); pwd)

crack_path ()
# Derive a set of parameters from a simulation output's path, with period suffix as e.g.
# /ccc/store/cont003/gen0826/lurtont/IGCM_OUT/IPSLCM6/*/historical/CM61-LR-hist-01/*/Analyse/1980-2005
{
    path=$1
    if [ $Center = TGCC ] ; then 
	root=$(echo $path | cut -d / -f 1-5)
	rest=$(echo $path | cut -d / -f 6-)
    elif [[ $Center == spirit* ]] ; then 
	root=/$(echo $path | cut -d / -f 2)
	rest=$(echo $path | cut -d / -f 3-)
    elif [ $Center = IDRIS ] ; then 
	root=$(echo $path | cut -d / -f 1-4)
	rest=$(echo $path | cut -d / -f 5-)
    else
	echo "Unkown Center $Center"
	exit 1
    fi
    login=$(echo $rest | cut -d / -f 1)
    tagname=$(echo $rest | cut -d / -f 3)
    [[ $Center == spirit* ]] && tagname="IGCM_OUT"/$tagName
    spacename=$(echo $rest | cut -d / -f 4)
    exptype=$(echo $rest | cut -d / -f 5)
    experimentname=$(echo $rest | cut -d / -f 6)
    out=$(echo $rest | cut -d / -f 8)
    period=$(echo $rest | cut -d / -f 9)

    echo "$root $login $tagname $spacename $exptype $experimentname $out $period"
}

# First install a light copy of C-ESM-EP and cd to there
$dir/install_lite.sh $target $comparison with_libIGCM
if [ $? -eq 9 ]; then
    # The target install already exist and the user wants to keep it
    exit 0
fi
set -e
cd $target/cesmep_lite
mv $comparison ${jobname}_${comparison}
comparison=${jobname}_${comparison}

read Root Login TagName SpaceName ExpType ExperimentName foo <<< $(crack_path $R_SAVE)

# Derive more parameters
OUT='Analyse'
frequency='monthly'
if [ $ConfigCesmep = SE ]; then
    frequency='seasonal'
elif [ $ConfigCesmep != TS ]; then
    OUT='Output'
fi

# Create comparison's parameters file and set first part
cat <<-EOF > $comparison/libIGCM_fixed_settings.py
	root           = '$Root'
	Login          = '${Login}'
	TagName        = '${TagName}'
	SpaceName      = '${SpaceName}'
	ExpType        = '${ExpType}'
	ExperimentName = '${ExperimentName}'
	OUT            = '$OUT'
	frequency      = '$frequency'
	DateBegin      = '${DateBegin//-/}'
	CesmepSlices   = $CesmepSlices
	CesmepSlicesDuration = $CesmepSlicesDuration
	CesmepPeriod   = $CesmepPeriod
	EOF

# Install a dedicated datasets_setup file
cp $dir/libIGCM_datasets.py $comparison/datasets_setup.py

# Create a python module defining a list of reference simulations
rm -f $comparison/libIGCM_references.py
if [ $CesmepReferences != NONE ]; then
    echo "CesmepReferences=$CesmepReferences"
    cat <<-EOH > $comparison/libIGCM_references.py
	reference = [\\
	EOH
    for reference in ${CesmepReferences//,/ }; do	
	if [ $reference = default ] ; then
	    echo "  'default'," >>  $comparison/libIGCM_references.py
	    continue
	fi
	
	#e.g. /ccc/store/cont003/gencmip6/lurtont/IGCM_OUT/IPSLCM6/PROD/historical/CM61-LR-hist-01/*/Analyse/1980_1989
	# Test that the path has some data
	path=$(dirname $reference)
	if [ $(ls $path 2>/dev/null | wc -l) -eq 0 ] ; then
	    echo "ERROR : Reference path doesn't exist or has no data : $path"
	    exit 5
	fi

	# Create reference attributes dict
	read RefRoot RefLogin RefTagName RefSpaceName RefExpType RefExperiment RefOut RefPeriod <<< \
	     $(crack_path $reference)
	cat <<-EOJ >> $comparison/libIGCM_references.py
		  dict(project='IGCM_OUT',
		    root        = "$RefRoot",
		    login       = "$RefLogin",
		    model       = "$RefTagName",
		    status      = "$RefSpaceName",
		    experiment  = "$RefExpType",
		    simulation  = "$RefExperiment",
		    frequency   = 'monthly',
		    OUT         = "$RefOut",
		    ts_period   = 'full',
		    clim_period = "$RefPeriod",
		    custom_name = "$RefExperiment/$RefPeriod"
		    ),
		EOJ
	done
    cat <<-EOK >> $comparison/libIGCM_references.py
	]
	EOK
fi

# Compute CESMEP components list based on list of component
# directories and on simulation components list ($Components)
comps=","
for comp in $(cd $comparison ; ls ) ; do
    ! [ -d $comparison/$comp ] && continue
    # Work only on directories
    add=false
    case $comp in
	MainTimeSeries | AtlasExplorer)
	    [[ $Components = *,ATM,* || $Components = *,OCE,* ]] && add=true ;;

	Atmosphere_Surface | Atmosphere_StdPressLev | Atmosphere_zonmean |\
	NH_Polar_Atmosphere_StdPressLev | NH_Polar_Atmosphere_Surface | \
	SH_Polar_Atmosphere_StdPressLev | SH_Polar_Atmosphere_Surface)
	    [[ $Components = *,ATM,* ]] && add=true ;;

	ORCHIDEE )
	    [[ $Components = *,SRF,* || $Components = *,OOL,* ]] && add=true ;;

	NEMO_main | NEMO_zonmean | NEMO_depthlevels | ENSO)
	     [[ $Components = *,OCE,* ]] && add=true ;;
    esac
    if [ $add = true ] ; then
	comps=$comps$comp",";
    else
	if [ $comp != __pycache__ ] ; then 
	   # Remove component directory 
	   rm -fr $comparison/$comp ;
	fi
    fi
done
# Discard leading and trailing comma in components list
comps=${comps%,} ; comps=${comps#,}

if [ -z $comps ] ; then
    echo "ERROR : the list of simulation components: "
    echo -e "\t $Components"
    echo "cannot trigger any C-ESM-EP component for comparison $(pwd)/$comparison" 
    exit 1
fi

# Compute location for C-ESM-EP CliMAF cache, 
case $Center in
    TGCC) cacheroot=$CCCSCRATCHDIR ;;
    IDRIS) cacheroot=$SCRATCH ;;
    spirit*) cacheroot=/scratchu/$USER ;;
esac    
cache=$cacheroot/cesmep_climaf_caches/${ExperimentName}_${TagName}_${ExpType}_${SpaceName}_${OUT}

# Write down a few parameters in a file used by libIGCM_post.sh
echo "$dir $comparison ${DateBegin//-/} $CesmepPeriod $CesmepSlices $CesmepSlicesDuration $cache $comps " > libIGCM_post.param

# Set account/project to charge, and mail to use, in relevant file
[ $Center = IDRIS ] && ProjectId=$ProjectId"@cpu"
sed -i \
    -e "s/account *=.*/account = \"$ProjectId\"/" \
    -e "s/mail *=.*/mail = \"${MailAdress}\"/" \
    settings.py

# Create a link to simulation outputs (for easing debug)
ln -sf $R_SAVE simulation_outputs
