#!/bin/python3

"""Main CI job script."""

import os
import subprocess
import sys
from datetime import datetime

from kubeinit_ci_utils import upload_logs

from pybadges import badge


def main(distros):
    """Run the main method."""
    gh_token = os.environ['GH_TOKEN']

    vars_file_path = os.getenv('VARS_FILE', "")
    pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

    output = "go"
    # Something linke:
    # url = "https://gitlab.com/kubeinit/kubeinit-ci/pipelines/"
    url = os.getenv('CI_PIPELINE_URL', "")
    print("The job results will be published in runtime at: " + url)

    cdk_configs = ["cdk-libvirt-3-master-1-worker-default",
                   "cdk-libvirt-1-master-1-worker-default",
                   "cdk-libvirt-1-master-0-worker-default"]

    okd_configs = ["okd-libvirt-3-master-1-worker-default",
                   "okd-libvirt-1-master-1-worker-default",
                   "okd-libvirt-1-master-0-worker-default"]

    rke_configs = ["rke-libvirt-3-master-1-worker-default",
                   "rke-libvirt-1-master-1-worker-default",
                   "rke-libvirt-1-master-0-worker-default"]

    k8s_configs = ["k8s-libvirt-3-master-1-worker-default",
                   "k8s-libvirt-1-master-1-worker-default",
                   "ks8-libvirt-1-master-0-worker-default"]

    eks_configs = ["eks-libvirt-3-master-1-worker-default",
                   "eks-libvirt-1-master-1-worker-default",
                   "eks-libvirt-1-master-0-worker-default"]

    list_of_distros = distros.split(',')

    configs = []

    for dist in list_of_distros:
        if dist == 'okd':
            configs = configs + okd_configs
        if dist == 'eks':
            configs = configs + eks_configs
        if dist == 'rke':
            configs = configs + rke_configs
        if dist == 'cdk':
            configs = configs + cdk_configs
        if dist == 'k8s':
            configs = configs + k8s_configs

    for config in configs:
        print("-*-*-*-*-")
        print(config)
        execute = False
        scenario = "default"
        # We assign the executed label to avoid executing this agains the same PR over and over
        # We mark the PR as e2e-executed

        #
        # Charmed Distribution of Kubernetes
        #
        if ("cdk-libvirt-3-master-1-worker-default" == config):
            distro = "cdk"
            driver = "libvirt"
            master = "3"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("cdk-libvirt-3-master-0-worker-default" == config):
            distro = "cdk"
            driver = "libvirt"
            master = "3"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("cdk-libvirt-1-master-1-worker-default" == config):
            distro = "cdk"
            driver = "libvirt"
            master = "1"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("cdk-libvirt-1-master-0-worker-default" == config):
            distro = "cdk"
            driver = "libvirt"
            master = "1"
            worker = "0"
            execute = True
            scenario = "periodic"

        #
        # Rancher Kubernetes Engine
        #
        elif ("rke-libvirt-3-master-1-worker-default" == config):
            distro = "rke"
            driver = "libvirt"
            master = "3"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("rke-libvirt-3-master-0-worker-default" == config):
            distro = "rke"
            driver = "libvirt"
            master = "3"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("rke-libvirt-1-master-1-worker-default" == config):
            distro = "rke"
            driver = "libvirt"
            master = "1"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("rke-libvirt-1-master-0-worker-default" == config):
            distro = "rke"
            driver = "libvirt"
            master = "1"
            worker = "0"
            execute = True
            scenario = "periodic"

        #
        # Origin Kubernetes Distribution
        #
        elif ("okd-libvirt-3-master-0-worker-default" == config):
            distro = "okd"
            driver = "libvirt"
            master = "3"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("okd-libvirt-3-master-1-worker-default" == config):
            distro = "okd"
            driver = "libvirt"
            master = "3"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("okd-libvirt-1-master-0-worker-default" == config):
            distro = "okd"
            driver = "libvirt"
            master = "1"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("okd-libvirt-1-master-1-worker-default" == config):
            distro = "okd"
            driver = "libvirt"
            master = "1"
            worker = "1"
            execute = True
            scenario = "periodic"

        #
        # Kubernetes
        #
        elif ("k8s-libvirt-3-master-1-worker-default" == config):
            distro = "k8s"
            driver = "libvirt"
            master = "3"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("k8s-libvirt-3-master-0-worker-default" == config):
            distro = "k8s"
            driver = "libvirt"
            master = "3"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("k8s-libvirt-1-master-1-worker-default" == config):
            distro = "k8s"
            driver = "libvirt"
            master = "1"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("k8s-libvirt-1-master-0-worker-default" == config):
            distro = "k8s"
            driver = "libvirt"
            master = "1"
            worker = "0"
            execute = True
            scenario = "periodic"

        #
        # EKS
        #
        elif ("eks-libvirt-3-master-1-worker-default" == config):
            distro = "eks"
            driver = "libvirt"
            master = "3"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("eks-libvirt-3-master-0-worker-default" == config):
            distro = "eks"
            driver = "libvirt"
            master = "3"
            worker = "0"
            execute = True
            scenario = "periodic"
        elif ("eks-libvirt-1-master-1-worker-default" == config):
            distro = "eks"
            driver = "libvirt"
            master = "1"
            worker = "1"
            execute = True
            scenario = "periodic"
        elif ("eks-libvirt-1-master-0-worker-default" == config):
            distro = "eks"
            driver = "libvirt"
            master = "1"
            worker = "0"
            execute = True
            scenario = "periodic"

        if execute:
            now = datetime.now()
            now.strftime("%m.%d.%Y.%H.%M.%S")
            job_name = "periodic" + "-" + distro + "-" + driver + "-" + master + "-" + worker + "-" + scenario + "-" + "weekly"
            print("Let's run the e2e job, distro %s driver %s " % (distro, driver))

            print("The pipeline ID is: " + str(pipeline_id))
            print("The clouds.yml path is: " + str(vars_file_path))
            # We trigger the e2e job
            badge_code = badge(left_text=str(distro) + "-" + str(master) + "-" + str(worker), right_text='OK', right_color='green')
            try:
                print("We call the downstream job configuring its parameters")
                subprocess.check_call("./ci/run_periodic.sh %s %s %s %s %s %s %s %s" % (str("--"),
                                                                                        str("--"),
                                                                                        str(vars_file_path),
                                                                                        str(distro),
                                                                                        str(driver),
                                                                                        str(master),
                                                                                        str(worker),
                                                                                        str(scenario)),
                                      shell=True)
            except Exception as e:
                print('An exception hapened executing Ansible')
                print(e)
                badge_code = badge(left_text=str(distro) + "-" + str(master) + "-" + str(worker), right_text='NOK', right_color='red')

            with open("/root/badge_status.svg", "w+") as text_file:
                text_file.write(badge_code)

            try:
                print("Render ara data")
                subprocess.check_call("./ci/ara.sh %s" % (str(job_name) + "-" + str(output)), shell=True)
            except Exception as e:
                print('An exception hapened rendering ara data')
                print(e)

            print("starting the uploader job")
            # No matter if the job passed or failed we always use go as the suffix

            upload_error = upload_logs(str(job_name) + "-" + str(output), gh_token)
            print("finishing the uploader job")

            if upload_error == 1:
                print("An error ocurred when uploading logs")
                dest_url = url + str(pipeline_id)
            else:
                print("All logs were uploaded succesfully")
                dest_url = 'https://kubeinit-bot.github.io/kubeinit-ci-results/' + str(job_name) + "-" + str(output) + '/index.html'
            print(dest_url)


if __name__ == "__main__":

    if (len(sys.argv) != 2):
        print("This can only take one argument like:")
        print("launch_e2e_periodic.py okd")
        print("launch_e2e_periodic.py okd,rke")
        print("launch_e2e_periodic.py cdk,rke")
        print("Mix any of the supported distros in a comma separated string")
        sys.exit()

    print("---")
    print("Main argument: " + sys.argv[0])
    print("---")
    print("Distros argument: " + sys.argv[1])
    print("---")
    main(sys.argv[1])
