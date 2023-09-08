#!/usr/bin/env bash

# Testing that an execution of a reference comparison's clone do plot
# all graphics and provides the reference results

# Another script must launch the test comparison, upstream; the
# present script checks the results and must be executed once batch
# jobs launched by the first one are completed

# ENVIRONMENT VARIABLES
##########################

# CLIMAF and CLIMAF_CACHE should be set

# Should we activate tracing :
setx=${setx:-0}
[ $setx = 1 ] && set -x

# Should we stop checking results as soon as a component or some plots
# are missing in the test comaprison
strict=${strict:-1} 

# CESMEP indicates the location for C-ESM-EP code under testing
CESMEP=${CESMEP?Please indicate location for C-ESM-EP code in \$CESMEP}

# ARGUMENTS
##################
# Name of the comparison that produced the reference results
ref_name=${1:-reference_comparison}
# Location for reference results. Can be a relative path
ref_outputs=${2:-$CESMEP/tests/reference_results}
# Name of the comparison that tried to reproduce reference results
testcomp=${3:-test_comparison}
##################

ref_outputs=$(cd $ref_outputs ; pwd)
cd $CESMEP

# Get outputs directory for test comparison
test_outputs=$(python run_C-ESM-EP.py $testcomp url | tail -n 1 | cut -c 4-)
test_outputs=$(dirname $test_outputs)

echo "#####################################################################################"
echo "This is the analysis of a C-ESM-EP run for a comparison named $testcomp that "
echo "is a clone of comparison $ref_name"
echo "The C-ESM-EP instance used is $CESMEP"
echo "The results are at $test_outputs "
echo "They are compared with the reference results at $ref_outputs"
echo "#####################################################################################"
echo -e "\n\n\n\n"

# List components dirs in reference outputs (as dirs containing png files)
echo $ref_outputs
refs=$(ls $ref_outputs/*/*.png)
if [ -z "$refs" ] ; then
    echo "Issue accessing reference outputs in $ref_outputs" 
    exit 1
fi
dirs=$(echo $refs | xargs -n 1 dirname | sort -u)

# Count missing component dirs in test_results, and check for missing
# plots in existing components dir
nok=0
issue_components=""
 issues=""
missing_components=""
for dir in $dirs; do
    component=$(basename $dir)
    other_dir=$test_outputs/$component
    if [ ! -d $other_dir ]; then
	#echo "Missing component directory $other_dir "
	missing_components+=" $other_dir"
	nok=$(( nok + 1 ))
    else
	# Analyze component job outputs for plot failure messages
	cissues=$(grep -h "!! Plotting failed" $CESMEP/$testcomp/$component/*.out)
	[ "$cissues" ] && grep -h "!! Plotting failed" $CESMEP/$testcomp/$component/*.out
	dissues=$(grep -h "No data found"      $CESMEP/$testcomp/$component/*.out)
	[ "$dissues" ] && grep -h "No data found"      $CESMEP/$testcomp/$component/*.out
	if [ "$cissues" -o "$dissues" ] ; then
	    issue_components+=" $component"
	    nok=$(( nok + 1 ))
	fi
    fi
done

# Exit if there are issues and   $strict == 1
if [ $nok -ne 0 ] && [ $strict -eq 1 ]  ; then
    echo -e "\n\n\n#########################################################"
    [ "$missing_components" ] && echo -e "Issue : missing components $missing_components (see above)"
    [ "$issue_components" ] && echo -e "Issue for some plots or data in component(s) $issue_components (see above)"
    echo -e "Stoping checks."
    echo -e "#########################################################\n\n\n"
    exit $nok
fi


# Test differences in graphics output, based on html index, using a
# CliMAF test utility

# A CliMAF version if needed
[ -z $CLIMAF ] && module load ${climaf_module:?Please set variable climaf_module or load a CLiMAF module}

export PYTHONPATH=$CLIMAF:$CLIMAF/tests:$PYTHONPATH

htmls=$(ls $ref_outputs/*/*.html | tr "\n" " ")
echo $htmls
if [ -z "$htmls" ] ; then
    echo "Issue accessing reference outputs index files in $ref_outputs"
    exit 1
fi
cat <<-EOF >tmp.py
	import sys, os
	from tests.tools_for_tests import compare_html_files
	print("Comparing outputs for components :")#, end='')
	NOK=0
	for file_ref in "$htmls".split() :
	   component = file_ref.split("/")[-2]
	   print(component)#, end='')
	   fic = file_ref.split("/")[-1].replace("$ref_name","$testcomp")
	   #print(fic)#, end='')
	   file_test="$test_outputs"+"/"+component+"/"+fic
	   #print(file_test)
	   dn=os.path.dirname(file_ref)
	   bn=os.path.basename(file_ref)
	   NOK+=compare_html_files(file_test, bn, dn, display_error=False,\
	            replace="$ref_name", by="$testcomp", allow_url_change=True,\
	            generate_diffs_html=True)
	print()
	exit(NOK)
	EOF
python tmp.py
status=$?
if [ $status -eq 0 ] ; then 
    echo 
    echo -e "\n\n\n#########################################################"
    echo "Comparison successful. "
    echo -e "#########################################################\n\n\n"
    if [ $setx != 1 ] ; then
	# House-keeping in case of check success
	rm tmp.py
	rm -fR $CESMEP/$testcomp $test_outputs
	[ ! -z $CESMEP_CLIMAF_CACHE ] && rm -fR $CESMEP_CLIMAF_CACHE
    fi
else
    echo -e "Check was not successful, and no house-keeping occurred"
    echo -e "Don't forget to later clean CESMEP_CLIMAF_CACHE at :\n\t$CESMEP_CLIMAF_CACHE"
    echo -e "and test comparison dir at: \n\t$CESMEP/$testcomp "
    echo -e "and its outputs at: \n\t$test_outputs"
fi
exit $status
