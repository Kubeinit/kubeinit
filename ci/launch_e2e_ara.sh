#!/bin/bash
set -e

#############################################################################
#                                                                           #
# Copyright kubeinit contributors.                                          #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License"); you may   #
# not use this file except in compliance with the License. You may obtain   #
# a copy of the License at:                                                 #
#                                                                           #
# http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
# License for the specific language governing permissions and limitations   #
# under the License.                                                        #
#                                                                           #
#############################################################################

echo "(launch_e2e_ara.sh) ==> Executing launch_e2e_ara.sh"

PIPELINE_ID="$1"

echo "(launch_e2e_ara.sh) ==> The pipeline_id is $PIPELINE_ID"

#
# Any change in the way the logs from Ansible are
# gathered needs to be tested in both scenarios, when
# we launch the playbooks from the host and from a container
#
echo "(launch_e2e_ara.sh) ==> Running ara-manage to store the results from inside the api-server container"
podman exec -it api-server /bin/bash -c "ara-manage generate /opt/output_data/${PIPELINE_ID}"
mv ~/.ara/output_data/${PIPELINE_ID} .

touch ~/badge_status.svg
cp ~/badge_status.svg ./$PIPELINE_ID/
ls -ltah
pwd
chmod -R 755 ./$PIPELINE_ID

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ARA Records Ansible/KubeInit job report/g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ara.readthedocs.io/docs.kubeinit.org/g' {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#https://github.com/ansible-community/ara#https://github.com/kubeinit/kubeinit#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#https://ara.recordsansible.org#https://kubeinit.org#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#ARA Records Ansible and makes it easier to understand and troubleshoot. It is another recursive acronym.#KubeInit helps with the deployment of multiple Kubernetes distributions.#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#ara is a free and open source project under the GPLv3 license.#The CI results are rendered using <a href="https://placeholderfororiginalurl" target="_blank">ARA</a>#g' {} \;

find ./$PIPELINE_ID -type f -exec sed -i -e 's#../static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find ./$PIPELINE_ID -type f -exec sed -i -e 's#../static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;

find ./$PIPELINE_ID -type f -exec sed -i -e 's#static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find ./$PIPELINE_ID -type f -exec sed -i -e 's#static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#placeholderfororiginalurl#ara.recordsansible.org#g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's#>ara #>KubeInit #g' {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -E -e "/href=\".+\">Playbooks/ s/href=\".+\"/href=\"https:\/\/storage.googleapis.com\/kubeinit-ci\/jobs\/${PIPELINE_ID}\/index.html\"/g" {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -E -e "/href=\".+\">Hosts/ s/href=\".+\"/href=\"https:\/\/storage.googleapis.com\/kubeinit-ci\/jobs\/${PIPELINE_ID}\/hosts\/index.html\"/g" {} \;

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -E -e "/class=\"navbar-brand\" href=\".*\">/ s/href=\".*\"/href=\"https:\/\/storage.googleapis.com\/kubeinit-ci\/index.html\"/g" {} \;

echo "(launch_e2e_ara.sh) ==> Finishing the bash executor"
