#!/bin/bash
set -e

echo "(ara.sh) ==> Executing ara.sh"

PIPELINE_ID="$1"

echo "(ara.sh) ==> The pipelne_id is $PIPELINE_ID"

echo "(ara.sh) ==> Running ara-manage to store the results"
ara-manage generate ./$PIPELINE_ID
touch ~/badge_status.svg
cp ~/badge_status.svg ./$PIPELINE_ID/
ls -ltah
pwd
chmod -R 755 ./$PIPELINE_ID

# curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg
# curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico
# mv logo_white.svg ./$PIPELINE_ID/static/images/logo.svg
# mv favicon.ico ./$PIPELINE_ID/static/images/favicon.ico

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ARA Records Ansible/KubeInit job report/g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ara.readthedocs.io/docs.kubeinit.com/g' {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#https://github.com/ansible-community/ara#https://github.com/kubeinit/kubeinit#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#https://ara.recordsansible.org#https://kubeinit.org#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#ARA Records Ansible and makes it easier to understand and troubleshoot. It is another recursive acronym.#KubeInit helps with the deployment of multiple Kubernetes distributions.#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#ara is a free and open source project under the GPLv3 license.#The CI results are rendered using <a href="https://ara.recordsansible.org" target="_blank">ARA</a>#g' {} \;

find ./$PIPELINE_ID -type f -exec sed -i -e 's#../static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find ./$PIPELINE_ID -type f -exec sed -i -e 's#../static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;

find ./$PIPELINE_ID -type f -exec sed -i -e 's#static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find ./$PIPELINE_ID -type f -exec sed -i -e 's#static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#ara#KubeInit#g' {} \;

echo "(ara.sh) ==> Finishing the bash executor"
