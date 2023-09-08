#!/usr/bin/env bash
# Execute a test comparison as a clone of a reference comparison, and
# checks that the outputs produced match the reference outputs

# Checking outputs is done using colocated script compare_results.sh,
# which is executed in a job, launched after termination of the jobs of
# the reference comparison

# Result is available as the exit status of that job, and both through the
# subject of a mail send by the batch subsytem and in the job output

if [ -z "$*" -o "$1" = -h ]; then 
    echo "Usage : $0 reference_comparison reference_results_dir email"
    exit 1
fi

CESMEP=${CESMEP?Please set CESMEP to the C-ESM-EP code location}
# Script for comparing outputs is colocated with current script
compare_script=$CESMEP/tests/compare_results.sh
here=$(pwd)

# ENVIRONMENT VARIABLES USED
##########################################
# Should we activate tracing :
setx=${setx:-0}
[ $setx = 1 ] && set -x

# Should we actually launch the check job (on top of launching the comparison)
do_check=${do_check:-1}

# Verify that some CliMAF install is configured for use
[ -z $CLIMAF ] && module load ${climaf_module:?Please set variable climaf_module or load such a module}

# SCRIPT ARGUMENTS
##########################################
# Name of the comparison to reproduce
reference=${1:-reference_comparison}
# 2nd arg is location of its reference results
#   If empty -> use "reference_results"
ref_results=${2:-reference_results}
#   If relative path -> take it in C_ESM-EP code subdir 'tests' 
if [ ${ref_results:0:1} != "/" ]; then
    ref_results=$CESMEP/tests/$ref_results
fi
ref_results=$(realpath $ref_results)

# Mail adress for reporting results
email=${3:-none@ipsl.fr}
##########################################

machine=$(uname -n) 
if [[ $machine == spirit* ]] ; then
    batch=sbatch
else
    echo "Machine $machine not yet handled"
    exit 1
fi

# Launch test comparison, a clone of the reference comparison
##############################################################

testcomp=test_comparison  # Name of the test comparison

# May need to use a dedicated cache for forcing re-compute
# e.g. in case CLIMAF_CACHE is shared with reference run
if [ ! -z $CESMEP_CLIMAF_CACHE ] ; then 
    mkdir -p ${CESMEP_CLIMAF_CACHE}
    rm -fR $CESMEP_CLIMAF_CACHE/*
fi
out=$here/launch_${testcomp}.out
out=$(realpath $out)

cd $CESMEP;
rm -fr $testcomp; cp -a $reference $testcomp ;

cd $testcomp ;
rm -fr */slurm-*.out  */*_${reference}_C-ESM-EP.e* */copy_html_error_page.sh.e*

cd $CESMEP
mv -f settings.py settings.py.kip
echo -e "email=$email\none_mail_per_component = False\n" > settings.py
python run_C-ESM-EP.py $testcomp > $out 2>&1
if [ $? -ne 0 ] ; then 
    echo "Issue at the stage of launching $testcomp. See $out"
    exit 1
else
    echo "Comparison $testcomp was launched. See launch output in:"
    echo "   $out"
fi
mv -f settings.py.kip settings.py


if [ $do_check -eq 1 ] ; then 
    # Launch a job comparing results, that executes after completion of
    # the test comparison jobs (even if some component job failed)
    ###########################################################
    cd $here
    jobs=$(cat $CESMEP/$testcomp/launched_jobs | tr "\n" ",") ; jobs=${jobs%,} ; 
    jobname="Check_C-ESM-EP_$reference"
    if [ $batch = sbatch ] ; then
	out="%x-%j.out"
	sbatch --dependency=afterany:$jobs --job-name=$jobname --error=$out --output=$out \
	       --mail-type=END,FAIL --mail-user=$email \
	       --export=ALL,strict=1,CESMEP=$CESMEP,setx,CLIMAF,CLIMAF_CACHE,CESMEP \
	       $compare_script $reference $ref_results $testcomp > jobID.tmp
	if [ $? -ne 0 ] ; then
	    echo "Issue launching comparison job :"
	    cat jobID.tmp; rm jobID.tmp
	    exit 1
	fi
	jobID=$(tail -n 1 jobID.tmp | cut -d " " -f 4) ; rm jobID.tmp
	output="$(pwd)/${jobname}-${jobID}.out"
    else 
	echo "only Slurm is yet handled for handling results comparison- sorry !"
	exit 1
    fi

    # Print useful information re. results
    ######################################################
    
    echo "Check of C-ESM-EP run for comparison '$reference' was launched as comparison '$testcomp' in"
    echo "     $CESMEP/$testcomp"
    echo "Its outputs will be compared with reference results in "
    echo "     $ref_results"
    echo "Test success will appear as exit status of job '$jobname' (jobid = $jobID), both through:"
    echo "   - a mail to $email "
    echo "   - and in file $output"

fi


