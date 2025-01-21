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

# LibIGCM provided parameters
target=$1            # Directory where C-ESM-EP  should be installed (it will be created)
comparison=$2        # Which C-ESM-EP 'comparison' will be run. e.g. run_comparison
label=$3             # Used as a prefix for comparison's name
R_SAVE=$4            # Directory holding simulation outputs
ProjectId=${5:-None} # Which project ressource allocation should be charged (at TGCC and IDRIS)
MailAdress=$6        # Mail adress as in libIGCM
DateBegin=$7         # Start date for the simulation
ConfigCesmep=$8      # Value derived from config.card's Post section variable Cesmep (SE, TS or anything else)
CesmepPeriod=$9      # Period for atlas time slices (in years)
CesmepSlices=${10}   # Number of atlas time slices
Components=${11}     # List of activated physical components (e.g. ,ATM,OCE, ). Use "," at begin, end and as separator
Center=${12:-TGCC}   # Which computing center are we running on (TGCC, IDRIS, spirit*)
CesmepSlicesDuration=${13:-$CesmepPeriod}   # Duration of an atlas time slice (in years)
CesmepReferences=${14:-NONE} # Paths for the references simulation outputs, with period suffix. A comma separated list
CesmepInputFrequency="${15:-monthly}" # Which is the frequency of simulation outputs to use (daily/monthly/yearly)
CesmepPublish=${16:-True}
CesmepAtlasPath=${17:-NONE} # Path for the atlas (relative to $WORKDIR/C-ESM-EP/)
CesmepAtlasTitle=${18:-NONE} # Title for the atlas 


# This script can be called from anywhere
dir=$(cd $(dirname $0); pwd)

crack_path ()
# Derive a set of parameters from a simulation output's path, possibly with period suffix, as e.g.
# /ccc/store/cont003/gencmip6/lurtont/IGCM_OUT/IPSLCM6/PROD/historical/CM61-LR-hist-01/*/Analyse/TS_MO/1980-2005
{
    path=$1
    if [ $Center = TGCC ] ; then 
	root=$(echo $path | cut -d / -f 1-5)
	rest=$(echo $path | cut -d / -f 6-)
    elif [[ $Center == spirit* ]] ; then 
	root=/$(echo $path | cut -d / -f 2)
	rest=$(echo $path | cut -d / -f 3-)
    elif [ $Center = IDRIS ] ; then 
	#ex: /lustre/fsstor/projects/rech/psl/upe47jz/IGCM_OUT/OL2/DEVT/secsto/MyPostExp2
	root=$(echo $path | cut -d / -f 1-6)
	rest=$(echo $path | cut -d / -f 7-)
    else
	echo "Unkown Center $Center"
	exit 1
    fi
    login=$(echo $rest | cut -d / -f 1)
    tagname=$(echo $rest | cut -d / -f 3)
    [[ $Center == spirit* ]] && tagname="IGCM_OUT"/$tagname
    spacename=$(echo $rest | cut -d / -f 4)
    exptype=$(echo $rest | cut -d / -f 5)
    experimentname=$(echo $rest | cut -d / -f 6)
    
    # Next fields are expected only for reference simulations
    DIR=$(echo $rest | cut -d / -f 7)  # e.g. ATM
    out=$(echo $rest | cut -d / -f 8)  # e.g. Analyse, Output

    # Next field is either a period, with implies frequency
    # is monthly, or a subdir (e.g. TS_MO, TS_DA, MO, DA, ..)
    next=$(echo $rest | cut -d / -f 9)
    if [[ $next =~ [0-9]{4}[-_][0-9]{4} ]] ; then
	period=$next
	freq=monthly
    else
	period=$(echo $rest | cut -d / -f 10)
	freq=${next:(-2):2} # Last two letters
	freq=${freq:-None}
	[ $freq = MO ] && freq=monthly
	[ $freq = DA ] && freq=daily
	[ $freq = YE ] && freq=yearly
	[ "$next" = "*" ] && freq="*"
    fi
    echo "$root $login $tagname $spacename $exptype $experimentname $out $period $freq"
}

# First install a light copy of C-ESM-EP and cd to there
$dir/install_lite.sh $target $comparison with_libIGCM
if [ $? -eq 9 ]; then
    # The target install already exist and the user wants to keep it
    exit 0
fi
set -e
cd $target/cesmep_lite
mv $comparison ${label}_${comparison}
comparison=${label}_${comparison}

read Root Login TagName SpaceName ExpType ExperimentName foo <<< $(crack_path $R_SAVE)

# Derive more parameters
if [ $ConfigCesmep = SE -o $ConfigCesmep = TS ]; then
    OUT=Analyse
elif [ $ConfigCesmep = Pack -o $ConfigCesmep = AtEnd ]; then
    OUT=Output
else
    echo "Internal ERROR - ConfigCesmep value unknown : $ConfigCesmep"
    exit 6
fi

if [ $ConfigCesmep = SE ]; then
    CesmepInputFrequency=seasonal  # xxx peut sauter après maj de libIGCM
fi

# Create comparison's parameters file and set part which is fixed along run
cat <<-EOF > $comparison/libIGCM_fixed_settings.py
	root           = '$Root'
	# Next is the login for C-ESM-EP jobs (which may differ from the simulation's job
	Login          = '${Login}'
	TagName        = '${TagName}'
	SpaceName      = '${SpaceName}'
	ExpType        = '${ExpType}'
	ExperimentName = '${ExperimentName}'
	OUT            = '$OUT'
	frequency      = '$CesmepInputFrequency'
	DateBegin      = '${DateBegin//-/}'
	CesmepSlices   = $CesmepSlices
	CesmepSlicesDuration = $CesmepSlicesDuration
	CesmepPeriod   = $CesmepPeriod
	AtlasPath      = '$CesmepAtlasPath'
	AtlasTitle     = '$CesmepAtlasTitle'
	#
	# Next lines will allow to build the simulation output data path. This 
	# is needed when creating a fake simulation for computing an atlas, and e.g.
	# the user or the project used when running ins_job for C-ESM-EP (which 
	# shows above) is not the same as when running the simulation (which shows 
	# in the data path)
	# Each such parameter should be specified
	
	# DataPathRoot =       # e.g. '/ccc/store/cont003/gen0826'
	# DataPathLogin =      # user login showing in the data path 
	# DataPathJobName =    # needed only if you changed w.r.t.the initial config.card
	EOF
if [ $DataPathRoot ] ; then
    sed -i -e "s/# DataPathRoot.*/DataPathRoot = \"$DataPathRoot\"" $comparison/libIGCM_fixed_settings.py
fi
if [ $DataPathLogin ] ; then
    sed -i -e "s/# DataPathLogin.*/DataPathLogin = \"$DataPathLogin\"/" $comparison/libIGCM_fixed_settings.py
fi

# Install a dedicated datasets_setup file
cp $dir/libIGCM_datasets.py $comparison/datasets_setup.py

# Create python module libIGCM_references.py defining a list of reference simulations
rm -f $comparison/libIGCM_references.py
if [ $CesmepReferences != NONE ]; then
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
	read RefRoot RefLogin RefTagName RefSpaceName RefExpType RefExperiment RefOut RefPeriod RefFreq <<< $(crack_path $reference)
	cat <<-EOJ >> $comparison/libIGCM_references.py
		  dict(project='IGCM_OUT',
		    root        = "$RefRoot",
		    login       = "$RefLogin",
		    model       = "$RefTagName",
		    status      = "$RefSpaceName",
		    experiment  = "$RefExpType",
		    simulation  = "$RefExperiment",
		    frequency   = "$RefFreq",
		    OUT         = "$RefOut",
		    ts_period   = 'full',
		    clim_period = "$RefPeriod",
		    custom_name = "${RefExperiment}_${RefPeriod}"
		    ),
		EOJ
	done
    cat <<-EOK >> $comparison/libIGCM_references.py
	]
	EOK
fi

# Compute CESMEP components list based on list of component
# directories and on simulation physical components list ($Components)
comps=","
for comp in $(cd $comparison ; ls ) ; do
    ! [ -d $comparison/$comp ] && continue
    # Work only on directories
    add=false
    case $comp in
	#AtlasExplorer)
	#    [[ $Components = *,ATM,* || $Components = *,OCE,* ]] && add=true ;;
	MainTimeSeries )
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
    echo "ERROR : the list of simulation physical components: "
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

# Write down a few parameters in file libIGCM_post.param, used by libIGCM_post.sh
echo "$dir $comparison ${DateBegin//-/} $CesmepPeriod $CesmepSlices $CesmepSlicesDuration $cache $comps " > libIGCM_post.param

# Set account/project to charge, and mail to use, and flag 'publish',
# in relevant file
[ $Center = IDRIS ] && ProjectId=$ProjectId"@cpu"
sed -i \
    -e "s/account *=.*/account = \"$ProjectId\"/" \
    -e "s/mail *=.*/mail = \"${MailAdress}\"/" \
    settings.py
if [ $CesmepPublish = FALSE -o $CesmepPublish = False ]; then
    sed -i -e "s/publish *=.*/publish = False/" settings.py
fi

# Create a link to simulation outputs (for easing debug)
ln -sf $R_SAVE simulation_outputs
