#!/bin/bash



echo 'List of files for the cleanup = '
ls */climaf.log */last.out */*/climaf.log */*/last.out */*.e* */*.o* */*/*.e* */*/*.o* */*/job.in */job.in
echo 'Do you want to remove those files? (y/n - o/n - yes/no - oui/non) => '
echo -n " Your answer : "
read reponse
case ${reponse} in
y|o|yes|oui)
echo 'Erasing the files...'
rm -f */climaf.log */last.out */*/climaf.log */*/last.out */*.e* */*.o* */*/*.e* */*/*.o* */*/job.in */job.in
echo 'Done'
;;
n|no|non)
echo 'We stop here'
;;
*)
echo 'Please provide an answer from the list: y/n - o/n - yes/no - oui/non'
;;
esac


