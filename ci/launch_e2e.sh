#!/bin/bash
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

echo "(launch_e2e.sh) ==> Executing run.sh ..."

REPOSITORY="${1}"
BRANCH_NAME="${2}"
PULL_REQUEST="${3}"
DISTRO="${4}"
DRIVER="${5}"
MASTERS="${6}"
WORKERS="${7}"
HYPERVISORS="${8}"
JOB_TYPE="${9}"
LAUNCH_FROM="${10}"

KUBEINIT_SPEC="${DISTRO}-${DRIVER}-${MASTERS}-${WORKERS}-${HYPERVISORS}-${LAUNCH_FROM}"

KUBEINIT_ANSIBLE_VERBOSITY="${GH_ANSIBLE_VERBOSITY:=v}"

KUBEINIT_MAIN_CI_REPOSITORY="https://github.com/kubeinit/kubeinit.git"

if [[ "$REPOSITORY" == "kubeinit/kubeinit" ]]; then
    REPOSITORY="${KUBEINIT_MAIN_CI_REPOSITORY}"
fi

if [ -f /etc/redhat-release ]; then
    OS_VERSION=$(cat /etc/redhat-release)
elif [ -f /etc/fedora-release ]; then
    OS_VERSION=$(cat /etc/fedora-release)
elif [ -f /etc/lsb-release ]; then
    source /etc/lsb-release
    OS_VERSION=${DISTRIB_DESCRIPTION}
elif [ -f /etc/debian_version ]; then
    OS_VERSION="Debian $(cat /etc/debian_version)"
else
    OS_VERSION="Unknown"
fi
OS_VERSION="${OS_VERSION} - $(uname -a)"

#
# For the multinode deployment we only support a 2 nodes cluster
#
if [[ "$HYPERVISORS" != "1" && "$HYPERVISORS" != "2" ]]; then
    echo "(launch_e2e.sh) ==> We only support 1 and 2 nodes clusters"
    exit 1
fi

echo "(launch_e2e.sh) ==> Hosts OS $OS_VERSION"
echo "(launch_e2e.sh) ==> The repository is $REPOSITORY"
echo "(launch_e2e.sh) ==> The branch is $BRANCH_NAME"
echo "(launch_e2e.sh) ==> The pull request is $PULL_REQUEST"
echo "(launch_e2e.sh) ==> The distro is $DISTRO"
echo "(launch_e2e.sh) ==> The driver is $DRIVER"
echo "(launch_e2e.sh) ==> The amount of master nodes is $MASTERS"
echo "(launch_e2e.sh) ==> The amount of worker nodes is $WORKERS"
echo "(launch_e2e.sh) ==> The amount of hypervisors is $HYPERVISORS"
echo "(launch_e2e.sh) ==> The job type is $JOB_TYPE"
echo "(launch_e2e.sh) ==> The ansible will be launched from $LAUNCH_FROM"
echo "(launch_e2e.sh) ==> The ansible verbosity is $KUBEINIT_ANSIBLE_VERBOSITY"

# Install the collection

echo "(launch_e2e.sh) ==> Installing KubeInit ..."
echo "(launch_e2e.sh) ==> Current path"
pwd
rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
echo "(launch_e2e.sh) ==> Current folder content"
ls
cd kubeinit
echo "(launch_e2e.sh) ==> Build the collection"
ansible-galaxy collection build -v --force --output-path releases/
echo "(launch_e2e.sh) ==> Install the collection"
ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat galaxy.yml | shyaml get-value version`.tar.gz
cd ..

#
# Begin ARA configuration
#

echo "(launch_e2e.sh) ==> Kill, stop, and remove the ARA pod"
podman pod kill ara-pod || true
podman pod stop ara-pod || true
podman pod rm ara-pod || true

podman pod create \
    --name ara-pod \
    --publish 26973:8000

#
# When the playbook is executed from a container
# the callback plugin is not able to write back the
# data to the api client, we need to make explicit
# that information as environment variables when
# running the deployment containers.
#

echo "(launch_e2e.sh) ==> Preparing API server container ..."
rm -rf ~/.ara/server || true
rm -rf ~/.ara/output_data || true
mkdir -p ~/.ara/server
mkdir -p ~/.ara/output_data

# The port redirection is at pod level
# we redirect the 26973:8000 as the api server
# listens in the 8000 port
podman run --name api-server \
            --pod ara-pod \
            --detach --tty \
            --volume ~/.ara/server:/opt/ara:z \
            --volume ~/.ara/output_data:/opt/output_data:z \
            quay.io/recordsansible/ara-api:latest

#
# Any change in the way the logs from Ansible are
# gathered needs to be tested in both scenarios, when
# we launch the playbook from the host and from a container
#

echo "(launch_e2e.sh) ==> Allow queries from anywhere and restart the api-server container ..."
until [ -f ~/.ara/server/settings.yaml ]; do
    sleep 5
done

# If we need to make changes to the ara api container
# we can update the settings.yaml file and restart the container
# sed -i "s/  - ::1/  - '*'/" ~/.ara/server/settings.yaml
# podman restart api-server

echo "(launch_e2e.sh) ==> Configuring ara callback ..."
export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"
# The action plugins variable is required to be able to record
export ANSIBLE_ACTION_PLUGINS="$(python3 -m ara.setup.action_plugins)"
export ANSIBLE_LOAD_CALLBACK_PLUGINS=true
export ARA_API_CLIENT="http"
export ARA_API_SERVER="http://127.0.0.1:26973"

podman exec -it api-server /bin/bash -c "ara-manage migrate"
#
# End ARA configuration
#

#
# Install the CLI/agent
#
python3 -m pip install -r ./agent/requirements.txt
KUBEINIT_REVISION="${revision:-ci}" python3 -m pip install --upgrade ./agent

export KUBEINIT_COMMON_DNS_PUBLIC='10.11.5.160'

#
# Create aux file with environment information
#

kubeinit -b > ./kubeinit/aux_info_file.txt
echo "" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> Hosts OS: ${OS_VERSION}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> Date: $(date +"%Y.%m.%d.%H.%M.%S")" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> Kubeinit agent/cli version: $(kubeinit -v) " >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The repository is: ${REPOSITORY}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The branch is: ${BRANCH_NAME}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The pull request is: ${PULL_REQUEST}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The distro is: ${DISTRO}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The driver is: ${DRIVER}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The amount of master nodes is: ${MASTERS}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The amount of worker nodes is: ${WORKERS}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The amount of hypervisors is: ${HYPERVISORS}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The job type is: ${JOB_TYPE}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The ansible deployment will be launched from: ${LAUNCH_FROM}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The ansible verbosity level is: ${KUBEINIT_ANSIBLE_VERBOSITY}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The job URL: ${CI_JOB_URL}" >> ./kubeinit/aux_info_file.txt
echo "(launch_e2e.sh) ==> The kubeinit spec string is: ${KUBEINIT_SPEC}" >> ./kubeinit/aux_info_file.txt

#
# This logic allows to record specific files or content before starting
# the deployment, we add this at the beginning of the deployment
# because if there is a runtime error then these tasks might not
# run at all. We also do this before choosing if the deployment is
# containerized or not.
#

echo "(launch_e2e.sh) ==> Running record tasks ..."
tee ./playbook_tmp.yml << endoffile
---
- name: Record useful files and variables to the deployment
  hosts: localhost
  tasks:
    # Relative to the kubeinit folder
    - name: Record deployment extra information
      ara_record:
        key: extra_information
        value: "{{ lookup('file', './aux_info_file.txt') }}"
        type: text

endoffile

# This will concatenate to the deployment playbook
# the initial ARA playbook to record some details
# related to the deployment
sed -i 's/---//g' ./kubeinit/playbook.yml
cat ./kubeinit/playbook.yml >> ./playbook_tmp.yml
mv ./playbook_tmp.yml ./kubeinit/playbook.yml

#
# The last step is to run the deployment
#
echo "(launch_e2e.sh) ==> Deploying the cluster ..."

#
# The deployment playbook can be launched from a container [c]
# or directly from the host [h]
#

FAILED="0"
KUBEINIT_SPEC=${KUBEINIT_SPEC//,/$'\n'}

# We enable having Windows compute nodes by default in the CI
# for the k8s-1-1-1 spec scenario
if [[ "$DISTRO" == "k8s" && "$MASTERS" == "1" && "$WORKERS" == "1" && "$HYPERVISORS" == "1" ]]; then
    # For enabling Windows deployments use the cluster_nodes_spec like
    # -e cluster_nodes_spec='[{"when_group":"compute_nodes","os":"windows"}]'
    CLUSTER_NODES='[{"when_group":"compute_nodes","os":"windows"}]'
fi

# This conditional will never be true, this is kept as an example about
# How to wire in extra roles and variables in a deployment
if [[ "$DISTRO" == "okd" && "$MASTERS" == "1" && "$WORKERS" == "1" && "$HYPERVISORS" == "1" && "$HYPERVISORS" == "falsecondition" ]]; then
    # For enabling additional extra nodes use the extra_nodes_spec like
    # -e extra_nodes_spec='[{"name":"nova-compute","when_distro":["okd"],"os":"centos"}]'
    EXTRA_NODES='[{"name":"nova-compute","when_distro":["okd"],"os":"centos"}]'
    EXTRA_ROLES='kubeinit_an_extra_role_goes_here'
    EXTRA_VARS='-e kubeinit_a_custom_variable_goes_here=true'
fi

if [[ "$LAUNCH_FROM" == "h" ]]; then
    {
        COUNTER="-1"
        for SPEC in $KUBEINIT_SPEC; do
            echo "(launch_e2e.sh) ==> Deploying ${SPEC}"
            COUNTER=$(($COUNTER + 1))
            ansible-playbook \
                --user root \
                -${KUBEINIT_ANSIBLE_VERBOSITY:=v} \
                -e kubeinit_spec=${SPEC} \
                -e kubeinit_libvirt_cloud_user_create=true \
                -e post_deployment_services_spec='['${POST_DEPLOYMENT_SERVICES:-}']' \
                -e extra_roles_spec='['${EXTRA_ROLES:-}']' \
                -e kubeinit_network_spec='{"network_name":"kimgtnet'$COUNTER'","network":"10.0.'$COUNTER'.0/24"}' \
                -e hypervisor_hosts_spec='[{"ansible_host":"nyctea"},{"ansible_host":"tyto"}]' \
                -e cluster_nodes_spec=${CLUSTER_NODES:-[]} \
                -e extra_nodes_spec=${EXTRA_NODES:-[]} \
                -e compute_node_ram_size=16777216 \
                -e extra_node_ram_size=25165824 \
                ${EXTRA_VARS:-} \
                ./kubeinit/playbook.yml
            # We can not have any other command after
            # 'ansible-playbook' otherwise the || wont work
        done
    } || {
        echo "(launch_e2e.sh) ==> The deployment failed, we still need to run the cleanup tasks"
        FAILED="1"
    }

    if [[ "$JOB_TYPE" == "pr" ]]; then
        #
        # This while true will provide the feature of adding the label 'waitfordebug'
        # to any PR in the main repository, if this label is found, then we will wait for
        # 10 minutes until the label is removed from the pull request, after the label is
        # removed the cleanup tasks will be executed.
        #
        while true; do
            waitfordebug=$(curl \
                            --silent \
                            --location \
                            --request GET "https://api.github.com/repos/kubeinit/kubeinit/issues/${PULL_REQUEST}/labels" | \
                            jq -c '.[] | select(.name | contains("waitfordebug")).name' | tr -d '"')
            if [ "$waitfordebug" == "waitfordebug" ]; then
                echo "Wait for debugging the environment for 3 minutes"
                sleep 180
            else
                break
            fi
        done
    fi

    COUNTER="-1"
    for SPEC in $KUBEINIT_SPEC; do
        echo "(launch_e2e.sh) ==> Cleaning ${SPEC}"
        COUNTER=$(($COUNTER + 1))
        ansible-playbook \
            --user root \
            -${KUBEINIT_ANSIBLE_VERBOSITY:=v} \
            -e kubeinit_spec=${SPEC} \
            -e post_deployment_services_spec='['${POST_DEPLOYMENT_SERVICES:-}']' \
            -e kubeinit_network_spec='{"network_name":"kimgtnet'$COUNTER'","network":"10.0.'$COUNTER'.0/24"}' \
            -e hypervisor_hosts_spec='[{"ansible_host":"nyctea"},{"ansible_host":"tyto"}]' \
            -e cluster_nodes_spec=${CLUSTER_NODES:-[]} \
            -e extra_nodes_spec=${EXTRA_NODES:-[]} \
            -e kubeinit_stop_after_task=task-cleanup-hypervisors \
            ./kubeinit/playbook.yml
    done
else
    echo "(launch_e2e.sh) ==> The parameter launch from do not match a valid value [c|h]"
    exit 1
fi
if [[ "$FAILED" == "1" ]]; then
    echo "(launch_e2e.sh) ==> The deployment command failed, this script must fail"
    exit 1
fi
