#!/bin/bash

# Helper script for preparing C-ESM-EP runs to be launched by libIGCM during a simulation

# It is called by libIGCM at the stage of simulation preparation (ins_job), and
# installs a (lite) C-ESM-EP directory in SUBMIT directory.
# It then creates there :
#    - a relevant datasets_setups.py file (by copying a fixed file)
#    - a settings file imported by that datasets_setup.py file
#    - libIGCM_post.sh : a script that will be called by libIGCM during simulation
#    - a relevant entry for 'account' and for 'mail' in file settings.py

# The created script activates a set of components which matches the type of experiment

#set -x
set -e

# LibIGCM provided parameters
target=$1            # Directory where C-ESM-EP  should be installed
comparison=$2        # Which C-ESM-EP 'comparison' will be run
jobname=$3           # Used as a prefix for comparison's name
R_SAVE=$4            # Directory holding simulation outputs
ProjectId=$5         # Which project ressource allocation should be charged
MailAdress=$6        # Mail adress as in libIGCM
DateBegin=$7         # Start date for the simulation
ConfigCesmep=$8      # Value of config.card Post section variable Cesmep
CesmepPeriod=$9      # Duration of atlas time slices
CesmepSlices=${10}   # Number of atlas time slices
Components=${11}     # List of activated components

if [[ ! -d "/ccc" ||  -d "/data" ]] ; then
    # Computing centers other than TGCC
    echo "echo No C-ESM-EP available on this center ($(uname -n))" 
    exit 1
fi

# We are at TGCC

# This script can be called from anywhere
dir=$(cd $(dirname $0); pwd)

# First install a light copy of C-ESM-EP and cd to there
$dir/install_lite.sh $target $comparison 
cd $target/cesmep_lite
mv $comparison ${jobname}_${comparison}
comparison=${jobname}_${comparison}

# Derive a set of parameters from output's path
root=$(echo $R_SAVE | cut -d / -f 1-5)
Login=$(echo $R_SAVE | cut -d / -f 6)
TagName=$(echo $R_SAVE | cut -d / -f 8)
SpaceName=$(echo $R_SAVE | cut -d / -f 9)
ExpType=$(echo $R_SAVE | cut -d / -f 10)
ExperimentName=$(echo $R_SAVE | cut -d / -f 11)

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
	root           = '$root'
	Login          = '${Login}'
	TagName        = '${TagName}'
	SpaceName      = '${SpaceName}'
	ExpType        = '${ExpType}'
	ExperimentName = '${ExperimentName}'
	OUT            = '$OUT'
	frequency      = '$frequency'
	DateBegin      = '${DateBegin//-/}'
	CesmepSlices   = $CesmepSlices
	CesmepPeriod   = $CesmepPeriod
	EOF

# Install a dedicated datasets_setup file
cp $dir/libIGCM_datasets.py $comparison/datasets_setup.py

# Compute CESMEP components list based on list of component
# directories and on simulation components list
comps=","
for comp in $(cd $comparison ; ls ) ; do
    ! [ -d $comparison/$comp ] && continue
    add=false
    case comp in
	MainTimeSeries,AtlasExplorer)
	    [[ $Components = *,ATM,* || $Components = *,OCE,* ]] && add=true && break ;;
	Atmosphere_Surface,Atmosphere_StdPressLev,Atmosphere_zonmean,NH_Polar_Atmosphere_StdPressLev,NH_Polar_Atmosphere_Surface,SH_Polar_Atmosphere_StdPressLev,SH_Polar_Atmosphere_Surface)
	    [[ $Components = *,ATM,* ]] && add=true && break ;;
	ORCHIDEE)
	    [[ $Components = *,SRF,* || $Components = *,OOL,* ]] && add=true && break ;;
	NEMO_main,NEMO_zonmean,NEMO_depthlevels,ENSO)
	     [[ $Components = *,OCE,* ]] && add=true && break ;;
	*)
	    # If there is a param file, assume this actually is a
	    # customized comparison directory that must be activated
	    find $comparison/$comp -name "params*py" >/dev/null 2>&1  && add=true ;;
    esac
    if [ $add = true ] ; then comps=$comps$comp","; fi
done
# Discard leading and trailing comma in components list
comps=${comps%,} ; comps=${comps#,}

# Write down a few parameters in a file used by libIGCM_post.sh
cache=$CCCSCRATCHDIR/cesmep_climaf_caches/${ExperimentName}_${TagName}_${ExpType}_${SpaceName}_${OUT}
echo "$dir $comparison ${DateBegin//-/} $CesmepPeriod $CesmepSlices $cache $comps " > libIGCM_post.param

# Set account/project to charge, and mail to use, in relevant file
sed -i \
    -e "s/account *=.*/account = \"$ProjectId\"/" \
    -e "s/mail *=.*/mail = \"${MailAdress}\"/" \
    settings.py



