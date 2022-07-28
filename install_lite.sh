#!/bin/bash

# Proceed with a light install of C-ESM-EP, that saves on i-nodes, and on disk usage, by
# refering (through symbolic links) to the code in current dir
#   - First argument is the target directory
#   - Second (optionnal) argument is the single comparison to install (defaults to standard_comparison)

#   - The corresponding comparison sub-directory is copied (and not the other ones)
#   - Sub-directories 'Documentation', 'tests', '.git' and file README.md  are not installed
#   - Sub-directory 'share' is symbolically linked (this saves a lot of i-nodes)
#   - other files are symbolically linked, and may be turned to regular files if changes are
#       needed (but a few files, that should be changed, are copied rather than linked)

#set -x

o=$(cd $(dirname $0) ; pwd)  # Dir of current code
[ -h $o/share ] && echo "Cannot work from a lite install" && exit 1

target=$1 
mkdir -p $target
target=$(cd $target ; pwd)

# Copy the comparison subdir
comparison=${2:-standard_comparison}
[ ! -d $o/$comparison ] && echo "No access to $o/$comparison" && exit 1
(cd $o ; tar -cf - --exclude=*.out --exclude=*~ --exclude=climaf.log --exclude=job.in  $comparison) | \
    (cd $target; tar -xf -)

# Link some files at C-ESM-EP root level 
for file in $(ls $o/*py $o/*.sh) README.md ; do
    ln -sf $file $target
done

# Next files are prone to be edited, so better make a copy than a link
for fic in run_C-ESM-EP.py setenv_C-ESM-EP.sh settings.py \
	   custom_obs_dict.py custom_plot_params.py locations.py; do
    rm -f $target/$fic
    cp -f $o/$fic $target
done

# Linking next dir saves a lot of i-nodes
ln -sf $o/share $target

cat <<EOF > $target/README.lite
This is a light install of C-ESM-EP. You may customize it by 
     - replacing symbolic links by the link target file
     - editing files
For further doc, refer to the origin directory in $o

EOF
