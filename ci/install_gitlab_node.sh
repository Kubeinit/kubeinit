#!/bin/bash
set -o pipefail
set -e

if [[ -z "${GITLAB_CI_TOKEN}" ]]; then
    echo "The GitLab token to register the node is not defined."
    echo "Please run:"
    echo "export GITLAB_CI_TOKEN=<the_token_goes_here>"
    echo "Exiting..."
    exit 1
fi

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
    sudo yum install git lvm2 lvm2-devel -y
    sudo yum install python3-libvirt python3-lxml libvirt -y
    sudo yum install python3 python3-pip -y
    sudo yum install nano git podman -y

    # ARA required packages
    sudo yum install gcc python3-devel libffi-devel openssl-devel redhat-rpm-config -y
    sudo yum install sqlite -y

    # Install GitLab runner binary
    curl -LJO https://gitlab-runner-downloads.s3.amazonaws.com/latest/rpm/gitlab-runner_amd64.rpm

    if ! rpm -qa | grep gitlab-runner; then
        sudo rpm -ivh --replacepkgs gitlab-runner_amd64.rpm
    fi
fi

sudo pip3 install PyGithub
sudo pip3 install ansible
sudo pip3 install netaddr
sudo pip3 install pybadges
sudo pip3 install jinja2
sudo pip3 install google-cloud-storage

sudo python3 -m pip install --upgrade "ara[server]"==1.5.1

echo "127.0.0.1 nyctea" >> /etc/hosts
cd
mkdir -p ~/.ssh
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
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
--name kubeinit-ci-bot-server-1 \
--docker-pull-policy always \
--tag-list kubeinit-ci-bot

sudo gitlab-runner start

sudo sed -i 's/enforcing/disabled/g' /etc/selinux/config /etc/selinux/config
sudo reboot
