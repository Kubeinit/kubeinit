#!/bin/bash
set -e

echo "Executing ara.sh"

PIPELINE_ID="$1"

echo "The pipelne_id is $PIPELINE_ID"

echo "Running ara-manage to store the results"
ara-manage generate ./$PIPELINE_ID
touch ~/badge_status.svg
cp ~/badge_status.svg ./$PIPELINE_ID/
ls -ltah
pwd
chmod -R 755 ./$PIPELINE_ID

curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg
curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico
mv logo_white.svg ./$PIPELINE_ID/static/images/logo.svg
mv favicon.ico ./$PIPELINE_ID/static/images/favicon.ico

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ARA Records Ansible/KubeInit job report/g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ara.readthedocs.io/docs.kubeinit.com/g' {} \;

echo "Finishing the bash executor"
