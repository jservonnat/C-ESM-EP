#!/bin/bash
cd $WD

cp ../../share/fp_template/error_template.html ${atlas_pathfilename} 
sed -i "s/target_component/${component}/g" ${atlas_pathfilename}
sed -i "s/target_comparison/${comparison}/g" ${atlas_pathfilename}

