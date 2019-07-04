#!/bin/bash

if [[ $1 != '' ]]; then

  comparison=${1%/}

else

  comparison=*

fi


echo 'List of files for the cleanup = '
ls ${comparison}/*.log ${comparison}/last.out ${comparison}/*/*.log ${comparison}/*/last.out ${comparison}/*.e* ${comparison}/*.o* ${comparison}/*/*.e* ${comparison}/*/*.o* ${comparison}/*/job.in ${comparison}/job.in ${comparison}/climaf_mcdo_* ${comparison}/*/climaf_mcdo_* ${comparison}/ferret*.jnl* ${comparison}/*/ferret*.jnl*
echo 'Do you want to remove those files? (y/n - o/n - yes/no - oui/non) => '
echo -n " Your answer : "
read reponse
case ${reponse} in
y|o|yes|oui)
echo 'Erasing the files...'
#rm -f */*.log */last.out */*/*.log */*/last.out */*.e* */*.o* */*/*.e* */*/*.o* */*/job.in */job.in
#rm -rf */climaf_mcdo_* */*/climaf_mcdo_*
rm -rf ${comparison}/*.log ${comparison}/last.out ${comparison}/*/*.log ${comparison}/*/last.out ${comparison}/*.e* ${comparison}/*.o* ${comparison}/*/*.e* ${comparison}/*/*.o* ${comparison}/*/job.in ${comparison}/job.in ${comparison}/climaf_mcdo_* ${comparison}/*/climaf_mcdo_* ${comparison}/ferret*.jnl* ${comparison}/*/ferret*.jnl*
echo 'Done'
;;
n|no|non)
echo 'We stop here'
;;
*)
echo 'Please provide an answer from the list: y/n - o/n - yes/no - oui/non'
;;
esac


