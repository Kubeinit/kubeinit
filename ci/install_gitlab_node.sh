#!/bin/bash
set -o pipefail
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

if [[ -z "${GITLAB_CI_TOKEN}" ]]; then
    echo "The GitLab token to register the node is not defined."
    echo "Please run:"
    echo "export GITLAB_CI_TOKEN=<the_token_goes_here>"
    echo "Exiting..."
    exit 1
fi
if [[ -z "${GITLAB_CI_CLUSTER_TYPE}" ]]; then
    echo "The type of environment is required to register the nodes."
    echo "Please run:"
    echo "export GITLAB_CI_CLUSTER_TYPE=<[multinode|singlenode]>"
    echo "Exiting..."
    exit 1
fi
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    echo "Exiting..."
    exit 1
fi

if [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
    # Install jq
    yum install -y jq

    # Install selinux python bindings
    yum install -y libselinux-python3

    # Disable selinux in the next reboot
    sudo sed -i 's/enforcing/disabled/g' /etc/selinux/config /etc/selinux/config

    if [ -f "/etc/fedora-release" ]; then
        if grep -q 35 "/etc/fedora-release"; then
            update-crypto-policies --set DEFAULT:FEDORA32
        fi
    fi

fi

if [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then
    apt-get install -y jq
fi

# Check disk free space
if [ -d "/home/libvirt" ]; then
    file_space="/home/libvirt"
elif [ -d "/var/lib/libvirt" ]; then
    file_space="/var/lib/libvirt"
else
    file_space="/var/lib/"
fi
dspace=$(df -BG ${file_space} | \
    jq -R -s '
        split("\n") |
        .[] |
        if test("^/") then
            gsub(" +"; " ") | split(" ") | {mount: .[0], spacetotal: .[1], spaceused: .[2], spaceavail: .[3]}
        else
            empty
        end
    ' | jq .spaceavail | tr -d '"')

dspaceint=$(echo $dspace | sed 's/G//')
dspacereq="250"
if [ "$dspaceint" -gt "$dspacereq" ]; then
    echo "There is enough disk space"
else
    echo "There is not enough disk space, at least $dspacereq"
    echo "Check the space in $file_space"
    df -h
    echo "If /home has all the space..."
    echo "Try: mv /var/lib/libvirt /home/"
    echo "     mkdir -p /home/libvirt/"
    echo "     ln -sf /home/libvirt/ /var/lib/libvirt"
    echo "Exiting..."
    exit 1
fi

GITLAB_CI_HOST_NAME=$(hostname)

#
# SSH access
#

mkdir -p ~/.ssh
touch ~/.ssh/config
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa <<< n || true
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
INGRESS_IP=$(ip route get "8.8.8.8" | grep -Po '(?<=(src )).*(?= uid)')
echo "${INGRESS_IP}    nyctea" >> /etc/hosts
echo "nyctea" > /etc/hostname

#
# Make sure there is no IPv6
#
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

#
# FIXME:TODO: Include the prepare podman playbook instead of
# installing packages directly
#

if [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
    yum install -y nano git podman curl python3 python3-pip
    # ARA required packages
    yum install -y gcc python3-devel libffi-devel openssl-devel redhat-rpm-config
    yum install -y sqlite

    # Install GitLab runner binary
    curl -LJO https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_amd64.rpm

    if ! rpm -qa | grep gitlab-runner; then
        rpm -ivh --replacepkgs gitlab-runner_amd64.rpm
    fi
fi

if [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then
    apt-get install -y nano git podman curl python3 python3-pip

    # ARA dependencies
    apt-get install -y build-essential python3-dev
    apt-get install -y sqlite3

    # Install GitLab runner binary
    curl -LJO "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner_amd64.deb"
    dpkg -i gitlab-runner_amd64.deb

fi

# Configure git with the bot account
git config --global init.defaultBranch main
git config --global user.email "bot@kubeinit.org"
git config --global user.name "kubeinit-bot"

# Make sure ansible is removed
if command -v ansible; then
    apath=$(python3 -m pip show ansible | grep Location | awk '{ print $2 }')
    python3 -m pip uninstall ansible -y
    python3 -m pip uninstall ansible-base -y
    rm -rf "$apath/ansible*"
fi

python3 -m pip install --ignore-installed PyYAML

# Install dependencies
python3 -m pip install \
    --upgrade \
    pip \
    wheel \
    shyaml \
    cryptography \
    ansible \
    netaddr \
    requests \
    PyGithub \
    pybadges \
    jinja2 \
    urllib3 \
    google-cloud-storage

# Install and configure ara
# There are problems with multithread ara, we keep the last
# single thread version
# python3 -m pip install --upgrade "ara[server]"==1.5.6
# we run the server (api-server) in a pod so we dont need to install it anymore
python3 -m pip install --upgrade ara

gitlab-runner uninstall
gitlab-runner install --user root

gitlab-runner register \
    --non-interactive \
    --url https://gitlab.com/ \
    --registration-token ${GITLAB_CI_TOKEN} \
    --executor shell \
    --output-limit 10000 \
    --name ${GITLAB_CI_HOST_NAME} \
    --docker-pull-policy always \
    --tag-list kubeinit-ci-${GITLAB_CI_CLUSTER_TYPE}

gitlab-runner start

ssh -oStrictHostKeyChecking=no root@nyctea uptime

CONTAINER_RUNTIME=$(podman system info --format=json | jq .host.ociRuntime.name)

echo "-----------------------------------------------------------------"
echo "| Make sure the container runtime is CRUN                       |"
echo "| currently is: ${CONTAINER_RUNTIME}                                            |"
echo "-----------------------------------------------------------------"

if [[ "$CONTAINER_RUNTIME" == "runc" ]]; then
    echo "****** ERROR:FATAL: Container runtime must be crun ******"
    echo "****** ERROR:FATAL: Container runtime must be crun ******"
fi

echo "-----------------------------------------------------------------"
echo "| Make sure the inventory hosts are reached not using 127.0.0.1 |"
echo "| instead by the node FQDN or the external IP address of the    |"
echo "| machines                                                      |"
echo "-----------------------------------------------------------------"

echo "-----------------------------------------------------------"
echo "| Make sure IPv6 is disabled in all the other hypervisors |"
echo "| also disable selinux everywhere                         |"
echo "| if this is a cluster deployed in multiple hosts         |"
echo "-----------------------------------------------------------"

echo "Reboot this machine now!!!!!"
echo "reboot"
