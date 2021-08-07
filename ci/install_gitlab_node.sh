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

GITLAB_CI_HOST_NAME=$(hostname)

if [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
    # Fedora or CentOS or RHEL
    touch /etc/redhat-release
    touch /etc/fedora-release
    sudo yum update -y

    if grep -q Fedora "/etc/fedora-release";
    then
        sudo yum groupinstall "Virtualization" -y
    else
        sudo yum groupinstall "Virtualization Host" -y
    fi

    # Common requirements
    sudo yum install git lvm2 -y
    sudo yum install python3-libvirt python3-lxml libvirt -y
    sudo yum install python3 python3-pip -y
    sudo yum install nano git podman -y

    # ARA required packages
    sudo yum install gcc python3-devel libffi-devel openssl-devel redhat-rpm-config -y
    sudo yum install sqlite -y
    # We might try in the future to move to MySQL insteadof sqlite
    # sudo yum install mysql-server mysql-common mysql-devel mysql-libs python3-PyMySQL -y
    # pip3 install mysqlclient
    # Make sure that NOBODY can access the server without a password
    # mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'password'; FLUSH PRIVILEGES;"
    # Any subsequent tries to run queries this way will get access denied because lack of usr/pwd param
    # sudo systemctl start mysqld
    # sudo systemctl status mysqld

    # mysql -u root -ppassword -e "DROP DATABASE ara;"
    # mysql -u root -ppassword -e "CREATE DATABASE ara;"

    # Install GitLab runner binary
    curl -LJO https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_amd64.rpm

    if ! rpm -qa | grep gitlab-runner; then
        sudo rpm -ivh --replacepkgs gitlab-runner_amd64.rpm
    fi
fi

# Make sure ansible is removed
if command -v ansible; then
    apath=$(python3 -m pip show ansible | grep Location | awk '{ print $2 }')
    python3 -m pip uninstall ansible -y
    sudo rm -rf "$apath/ansible*"
fi

# Install dependencies
python3 -m pip install \
    --upgrade \
    pip \
    wheel \
    shyaml \
    cryptography==3.3.2 \
    ansible==3.4.0 \
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
# sudo python3 -m pip install --upgrade "ara[server]"==1.5.6
# we run the server (api-server) in a pod so we dont need to install it anymore
sudo python3 -m pip install --upgrade ara

echo "nyctea" > /etc/hostname
iface_ip=$(ip route get "8.8.8.8" | grep -Po '(?<=(src )).*(?= uid| proto)')
echo "${iface_ip} nyctea" >> /etc/hosts
cd
mkdir -p ~/.ssh
# In the case the key already exists we wont overwrite it
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa <<< n || true
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
ssh -oStrictHostKeyChecking=no root@nyctea uptime

mv /var/lib/libvirt /home/
sudo mkdir -p /home/libvirt/
sudo ln -sf /home/libvirt/ /var/lib/libvirt

echo "gitlab-runner:gitlab-runner" | sudo chpasswd
echo "gitlab-runner ALL=(root) NOPASSWD:ALL" \
    | sudo tee /etc/sudoers.d/gitlab-runner
sudo chmod 0440 /etc/sudoers.d/gitlab-runner

# We run the uninstall as is running under the gitlab-runner user
sudo gitlab-runner uninstall
sudo gitlab-runner install --user root

sudo gitlab-runner register --non-interactive \
                            --url https://gitlab.com/ \
                            --registration-token ${GITLAB_CI_TOKEN} \
                            --executor shell \
                            --output-limit 10000 \
                            --name ${GITLAB_CI_HOST_NAME} \
                            --docker-pull-policy always \
                            --tag-list kubeinit-ci-${GITLAB_CI_CLUSTER_TYPE}

sudo gitlab-runner start

sudo sed -i 's/enforcing/disabled/g' /etc/selinux/config /etc/selinux/config
sudo reboot
