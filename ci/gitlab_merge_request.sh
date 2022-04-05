#!/bin/bash
set -o pipefail
set -ex

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

cluster_type=$1

mr_iid=$CI_MERGE_REQUEST_IID
project_id=$CI_MERGE_REQUEST_PROJECT_ID
IFS=',' read -ra labels <<< $CI_MERGE_REQUEST_LABELS
commit_sha=$CI_COMMIT_SHA

KUBEINIT_RUNNER_HOST=$(cat ~/.gitlab-runner/runner-host)
KUBEINIT_RUNNER_USER=$(cat ~/.gitlab-runner/runner-user)

KUBEINIT_ANSIBLE_VERBOSITY="v"
for label in ${labels[@]}; do
    echo $label
    if [[ "$label" =~ verbosity=v+ ]]; then
        echo "$label is a valid ansible verbosity"
        IFS='=' read -ra params <<< $label
        KUBEINIT_ANSIBLE_VERBOSITY=${params[1]}
        break
    else
        echo "$label is an invalid ansible verbosity"
    fi
done

KUBEINIT_SPEC_LABEL=""
for label in ${labels[@]}; do
    echo $label
    if [[ "$label" =~ [a-z0-9.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[ch] ]]; then
        echo "$label is a valid ci job label"
        IFS='-' read -ra params <<< $label
        DISTRO=${params[0]}
        DRIVER=${params[1]}
        CONTROLLERS=${params[2]}
        COMPUTES=${params[3]}
        HYPERVISORS=${params[4]}
        RUN_MODE=${params[5]}
        KUBEINIT_SPEC_LABEL=$label
        break
    else
        echo "$label is an invalid ci job label"
    fi
done

new_labels=()
for label in ${labels[@]}; do
    if [[ "$label" != "$KUBEINIT_SPEC_LABEL" ]]; then
        new_labels+=($label)
    fi
done

if [[ "${labels[@]}" != "${new_labels[@]}" ]]; then
    gitlab project-merge-request update --project-id $project_id --iid $mr_iid --labels $(echo ${new_labels[@]} | tr ' ' ',')
fi

pwd

# Install the collection
cd kubeinit
rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
ansible-galaxy collection build -v --force --output-path releases/
ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat galaxy.yml | shyaml get-value version`.tar.gz
cd ..

export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"
export ANSIBLE_ACTION_PLUGINS="$(python3 -m ara.setup.action_plugins)"
export ANSIBLE_LOAD_CALLBACK_PLUGINS=true
export ARA_API_CLIENT="http"
export ARA_API_SERVER="http://127.0.0.1:8000"

#
# Install the CLI/agent
#
python3 -m pip install -r ./agent/requirements.txt
KUBEINIT_REVISION="${revision:-ci}" python3 -m pip install --upgrade ./agent

#
# Check if this is a multicluster deployment
# this means that the distro has a period in
# the name like okd.rke, k8s.rke, or k8s.eks
#
KUBEINIT_SPEC=$KUBEINIT_SPEC_LABEL
if [[ ${DISTRO} == *.* ]] ; then
    FIRST_DISTRO="$(cut -d'.' -f1 <<<"${DISTRO}")"
    SECOND_DISTRO="$(cut -d'.' -f2 <<<"${DISTRO}")"

    FIRST_KUBEINIT_SPEC="${KUBEINIT_SPEC/${DISTRO}/${FIRST_DISTRO}}"
    SECOND_KUBEINIT_SPEC="${KUBEINIT_SPEC/${DISTRO}/${SECOND_DISTRO}}"
    KUBEINIT_SPEC="${FIRST_KUBEINIT_SPEC},${SECOND_KUBEINIT_SPEC}"

    # We will enable only submariner in the
    # case of having a multicluster deployment
    # for okd.rke
    if [[ "$DISTRO" == "okd.rke" ]]; then
        POST_DEPLOYMENT_SERVICES='submariner'
    fi
fi

FAILED="0"
KUBEINIT_SPEC=${KUBEINIT_SPEC//,/ }
ARA_PLAYBOOK_NAME=ci-job-$CI_JOB_ID
ARA_PLAYBOOK_LABEL=ci_job_$CI_JOB_ID

export > ../export_$ARA_PLAYBOOK_LABEL

if [[ "$RUN_MODE" == "h" ]]; then
    {
        COUNTER="0"
        for SPEC in $KUBEINIT_SPEC; do
            echo "(launch_e2e.sh) ==> Deploying ${SPEC}"
            ansible-playbook \
                --user root \
                -${KUBEINIT_ANSIBLE_VERBOSITY:=v} \
                -e ara_playbook_name=${ARA_PLAYBOOK_NAME}-deployment \
                -e ara_playbook_labels=${ARA_PLAYBOOK_LABEL},${KUBEINIT_SPEC_LABEL},deployment \
                -e kubeinit_spec=${SPEC} \
                -e post_deployment_services_spec='['${POST_DEPLOYMENT_SERVICES:-}']' \
                -e kubeinit_network_spec='[network_name=kimgtnet'$COUNTER',network=10.0.'$COUNTER'.0/24]' \
                -e hypervisor_hosts_spec='[[ansible_host=nyctea],[ansible_host=tyto]]' \
                ./kubeinit/playbook.yml
            COUNTER="1"
        done
    } || {
        echo "(launch_e2e.sh) ==> The deployment failed, we still need to run the cleanup tasks"
        FAILED="1"
    }
    COUNTER="0"
    for SPEC in $KUBEINIT_SPEC; do
        echo "(launch_e2e.sh) ==> Cleaning ${SPEC}"
        ansible-playbook \
            --user root \
            -${KUBEINIT_ANSIBLE_VERBOSITY:=v} \
            -e ara_playbook_name=${ARA_PLAYBOOK_NAME}-cleanup \
            -e ara_playbook_labels=${ARA_PLAYBOOK_LABEL},${KUBEINIT_SPEC_LABEL},cleanup \
            -e kubeinit_spec=${SPEC} \
            -e post_deployment_services_spec='['${POST_DEPLOYMENT_SERVICES:-}']' \
            -e kubeinit_network_spec='[network_name=kimgtnet'$COUNTER',network=10.0.'$COUNTER'.0/24]' \
            -e hypervisor_hosts_spec='[[ansible_host=nyctea],[ansible_host=tyto]]' \
            -e kubeinit_stop_after_task=task-cleanup-hypervisors \
            ./kubeinit/playbook.yml
        COUNTER="1"
    done
else
    echo "(launch_e2e.sh) ==> The parameter launch from do not match a valid value [c|h]"
    exit 1
fi

MR_RESULTS_DIR=/opt/output_data/$mr_iid
RESULTS_DIR=$MR_RESULTS_DIR/$CI_JOB_ID

cat << EOF > ./ci/generate-ara-output.sh
#!/bin/bash

set -x

mkdir -p $MR_RESULTS_DIR
chown 999:999 $MR_RESULTS_DIR

for id in \$(bash -c "comm -23 <(ara playbook list -f value -c id | sort) <(ara playbook list -f value -c id --label $ARA_PLAYBOOK_LABEL | sort)"); do
  ara playbook delete \$id
done
ara-manage generate $RESULTS_DIR

find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's/ARA Records Ansible/KubeInit job report/g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's/ara.readthedocs.io/docs.kubeinit.org/g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#https://github.com/ansible-community/ara#https://github.com/kubeinit/kubeinit#g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#https://ara.recordsansible.org#https://kubeinit.org#g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#ARA Records Ansible and makes it easier to understand and troubleshoot. It is another recursive acronym.#KubeInit helps with the deployment of multiple Kubernetes distributions.#g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#ara is a free and open source project under the GPLv3 license.#The CI results are rendered using <a href="https://placeholderfororiginalurl" target="_blank">ARA</a>#g' {} \;
find $RESULTS_DIR -type f -exec sed -i -e 's#../static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find $RESULTS_DIR -type f -exec sed -i -e 's#../static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;
find $RESULTS_DIR -type f -exec sed -i -e 's#static/images/logo.svg#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg#g' {} \;
find $RESULTS_DIR -type f -exec sed -i -e 's#static/images/favicon.ico#https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/favicon.ico#g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#placeholderfororiginalurl#ara.recordsansible.org#g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -e 's#>ara #>KubeInit #g' {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -E -e "/href=\".+\">Playbooks/ s/href=\".+\"/href=\"https:\/\/storage.googleapis.com\/kubeinit-ci\/jobs\/${CI_JOB_ID}\/index.html\"/g" {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -E -e "/href=\".+\">Hosts/ s/href=\".+\"/href=\"https:\/\/storage.googleapis.com\/kubeinit-ci\/jobs\/${CI_JOB_ID}\/hosts\/index.html\"/g" {} \;
find $RESULTS_DIR -type f -name '*.html' -exec sed -i -E -e "/class=\"navbar-brand\" href=\".*\">/ s/href=\".*\"/href=\"http:\/\/${KUBEINIT_RUNNER_HOST}:8080\/ara-output-data\/${mr_iid}\/${CI_JOB_ID}\/index.html\"/g" {} \;

chown -R 999:999 $RESULTS_DIR
EOF
chmod +x ./ci/generate-ara-output.sh

ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=accept-new $KUBEINIT_RUNNER_USER@$KUBEINIT_RUNNER_HOST podman exec kubeinit-ara-api $(pwd)/ci/generate-ara-output.sh

gitlab project-merge-request-note create --project-id $project_id --mr-iid $mr_iid --body "Results for merge request job [#$CI_JOB_ID]($CI_JOB_URL) [$KUBEINIT_SPEC_LABEL](http://${KUBEINIT_RUNNER_HOST}:8080/ara-output-data/${mr_iid}/${CI_JOB_ID})."

if [[ "$FAILED" == "1" ]]; then
    echo "(launch_e2e.sh) ==> The deployment command failed, this script must fail"
    exit 1
fi
exit 0
