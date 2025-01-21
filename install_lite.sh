#!/bin/bash

# Proceed with a light install of C-ESM-EP, that saves on i-nodes, and
# on disk usage, by refering (through symbolic links, PATH and
# PYTHONPATH) to the C-ESM-EP code in a reference dir

#   - First argument: the directory that will host the light C-ESM-EP 
#         (in a subdir called cesmep_lite)
#   - Second argument is the single comparison to install

#   - The C-ESM-EP code is assumed to be located in *this* script's directory
#   - The comparison directory can be a subdir of this script dir or located
#       somewhere else; it is copied
#   - Sub-directories 'Documentation', 'tests', '.git' and file README.md
#       are not installed
#   - a few files are also symbolically linked,
#   - installed file setenv_C-ESM-EP.sh is modified so that PATH and PYTHONPATH 
#     includes the dir of current code, and PYTHONPATH includes share/cesmep_modules

#set -x

cesmep_dir=$(cd $(dirname $0) ; pwd)  # Dir of current code
[ -h $cesmep_dir/share ] && echo "Cannot work from a lite install" && exit 1

target=${1?"Provide target directory as first argument"} 
comparison=${2?"Provide comparison name as second argument"}
with_libIGCM=${3:-no}  # If arg #3 is set, also link scripts used by libIGCM

target=$(cd $target ; pwd)
[ ! -d $target ] && \
    echo "$0 : Must provide an existing directory as first argument" && exit 1
target=$target/cesmep_lite
if [ -d $target ] ; then
    echo -e "\033[1;32mThere's already a C-ESM-EP lite install at $target."
    echo -n -e " Do you want to supersede it (y/N) ? : \033[m"
    read reponse
    case ${reponse} in
	oui|OUI|o|y|yes|YES)
	    echo "OK"
	    ;;
	non|NON|n|no|NO|*)
	    echo "No C-ESM-EP install !"
	    exit 9
	    ;;
    esac
    chmod -R 777 $target
    rm -fR $target
fi
mkdir -p $target

# Copy the comparison subdir
if [ -d $cesmep_dir/$comparison ] ; then
    comparison_dir=$cesmep_dir
elif [ -d $comparison ] ; then
    comparison=$(realname $comparison)
    comparison_dir=$(dirname $comparison)
    comparison=$(basename $comparison)
else
    echo "No access to C-ESM-EP comparison $comparison"
    exit 1
fi
(cd $comparison_dir ; tar -chf - --exclude=*.out --exclude=*~ --exclude=climaf.log \
     --exclude=job.in  --exclude=cesmep_atlas_style_css $comparison) | \
    (cd $target; tar -xf - )

# Link a few files at C-ESM-EP root level 
links="share job_C-ESM-EP.sh job_PMP_C-ESM-EP.sh locations.py custom_obs_dict.py"
[ $with_libIGCM != no ] && links+=" libIGCM_clean.sh libIGCM_post.sh"
for file in $links; do
     ln -sf $cesmep_dir/$file $target
done

# Copy some python files (cannot link because of side effect in PYTHONPATH)
copies="run_C-ESM-EP.py main_C-ESM-EP.py"
for file in $copies; do
     cp -f $cesmep_dir/$file $target
done

# Copy also files that will or could be changed
cp -f $cesmep_dir/settings.py $target

# Set root directory in setenv_C-ESM-EP.sh
sed -e "s!#root=.*# *HERE!root=$cesmep_dir!g" $cesmep_dir/setenv_C-ESM-EP.sh \
    > $target/setenv_C-ESM-EP.sh
