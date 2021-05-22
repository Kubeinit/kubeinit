#!/bin/python3

"""Main CI job script."""

import os
import subprocess
import time
from datetime import datetime

from github import Github

from kubeinit_ci_utils import remove_label, render_index, upload_logs_to_google_cloud

#
# We only execute the e2e jobs for those PR having
# `whitelist_domain` as part of the committer's email
#


def main():
    """Run the main method."""
    gh = Github(os.environ['GH_TOKEN'])
    # gh_token = os.environ['GH_TOKEN']
    gc_token_path = os.environ['GC_STORAGE_KEY']

    vars_file_path = os.getenv('VARS_FILE', "")
    pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

    repo = gh.get_repo("kubeinit/kubeinit")
    branches = repo.get_branches()

    output = 0
    # Something linke:
    # url = "https://gitlab.com/kubeinit/kubeinit-ci/pipelines/"
    url = os.getenv('CI_PIPELINE_URL', "")
    print("The job results will be published in runtime at: " + url)

    for branch in branches:
        for pr in repo.get_pulls(state='open', sort='created', base=branch.name):
            labels = [item.name for item in pr.labels]

            sha = pr.head.sha
            committer_email = repo.get_commit(sha=sha).commit.committer.email
            print(committer_email)

            execute = False
            scenario = "default"
            # We assign the executed label to avoid executing this agains the same PR over and over
            # We mark the PR as e2e-executed

            #
            # OVN multi HV deployment
            #
            if ("k8s.ovn-libvirt-3-master-2-worker-default" in labels):
                distro = "k8s.ovn"
                driver = "libvirt"
                master = "3"
                worker = "2"
                execute = True
                scenario = "default"
                remove_label("k8s.ovn-libvirt-3-master-2-worker-default", pr, repo)
            #
            # Charmed Distribution of Kubernetes
            #
            if ("cdk-libvirt-3-master-1-worker-default" in labels):
                distro = "cdk"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("cdk-libvirt-3-master-1-worker-default", pr, repo)
            elif ("cdk-libvirt-3-master-0-worker-default" in labels):
                distro = "cdk"
                driver = "libvirt"
                master = "3"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("cdk-libvirt-3-master-0-worker-default", pr, repo)
            elif ("cdk-libvirt-1-master-1-worker-default" in labels):
                distro = "cdk"
                driver = "libvirt"
                master = "1"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("cdk-libvirt-1-master-1-worker-default", pr, repo)
            elif ("cdk-libvirt-1-master-0-worker-default" in labels):
                distro = "cdk"
                driver = "libvirt"
                master = "1"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("cdk-libvirt-1-master-0-worker-default", pr, repo)

            #
            # Rancher Kubernetes Engine
            #
            elif ("rke-libvirt-3-master-1-worker-default" in labels):
                distro = "rke"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("rke-libvirt-3-master-1-worker-default", pr, repo)
            elif ("rke-libvirt-3-master-0-worker-default" in labels):
                distro = "rke"
                driver = "libvirt"
                master = "3"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("rke-libvirt-3-master-0-worker-default", pr, repo)
            elif ("rke-libvirt-1-master-1-worker-default" in labels):
                distro = "rke"
                driver = "libvirt"
                master = "1"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("rke-libvirt-1-master-1-worker-default", pr, repo)
            elif ("rke-libvirt-1-master-0-worker-default" in labels):
                distro = "rke"
                driver = "libvirt"
                master = "1"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("rke-libvirt-1-master-0-worker-default", pr, repo)

            #
            # Origin Kubernetes Distribution
            #
            elif ("okd-libvirt-3-master-0-worker-default" in labels):
                distro = "okd"
                driver = "libvirt"
                master = "3"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("okd-libvirt-3-master-0-worker-default", pr, repo)
            elif ("okd-libvirt-3-master-1-worker-default" in labels):
                distro = "okd"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("okd-libvirt-3-master-1-worker-default", pr, repo)
            elif ("okd-libvirt-1-master-0-worker-default" in labels):
                distro = "okd"
                driver = "libvirt"
                master = "1"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("okd-libvirt-1-master-0-worker-default", pr, repo)
            elif ("okd-libvirt-1-master-1-worker-default" in labels):
                distro = "okd"
                driver = "libvirt"
                master = "1"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("okd-libvirt-1-master-1-worker-default", pr, repo)

            #
            # Kubernetes
            #
            elif ("k8s-libvirt-3-master-1-worker-default" in labels):
                distro = "k8s"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("k8s-libvirt-3-master-1-worker-default", pr, repo)
            elif ("k8s-libvirt-3-master-0-worker-default" in labels):
                distro = "k8s"
                driver = "libvirt"
                master = "3"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("k8s-libvirt-3-master-0-worker-default", pr, repo)
            elif ("k8s-libvirt-1-master-1-worker-default" in labels):
                distro = "k8s"
                driver = "libvirt"
                master = "1"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("k8s-libvirt-1-master-1-worker-default", pr, repo)
            elif ("k8s-libvirt-1-master-0-worker-default" in labels):
                distro = "k8s"
                driver = "libvirt"
                master = "1"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("k8s-libvirt-1-master-0-worker-default", pr, repo)

            #
            # EKS
            #
            elif ("eks-libvirt-3-master-1-worker-default" in labels):
                distro = "eks"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("eks-libvirt-3-master-1-worker-default", pr, repo)
            elif ("eks-libvirt-3-master-0-worker-default" in labels):
                distro = "eks"
                driver = "libvirt"
                master = "3"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("eks-libvirt-3-master-0-worker-default", pr, repo)
            elif ("eks-libvirt-1-master-1-worker-default" in labels):
                distro = "eks"
                driver = "libvirt"
                master = "1"
                worker = "1"
                execute = True
                scenario = "default"
                remove_label("eks-libvirt-1-master-1-worker-default", pr, repo)
            elif ("eks-libvirt-1-master-0-worker-default" in labels):
                distro = "eks"
                driver = "libvirt"
                master = "1"
                worker = "0"
                execute = True
                scenario = "default"
                remove_label("eks-libvirt-1-master-0-worker-default", pr, repo)

            #
            # Misc jobs
            #
            elif ("okd.rke-libvirt-3-master-1-worker-submariner" in labels):
                distro = "okd.rke"
                driver = "libvirt"
                master = "3"
                worker = "1"
                execute = True
                scenario = "submariner"
                remove_label("okd.rke-libvirt-3-master-1-worker-submariner", pr, repo)
            elif ("okd.rke-libvirt-1-master-2-worker-submariner" in labels):
                distro = "okd.rke"
                driver = "libvirt"
                master = "1"
                worker = "2"
                execute = True
                scenario = "submariner"
                remove_label("okd.rke-libvirt-1-master-2-worker-submariner", pr, repo)

            if execute:
                now = datetime.now()
                now.strftime("%m.%d.%Y.%H.%M.%S")
                job_name = pipeline_id + "-" + distro + "-" + driver + "-" + master + "-" + worker + "-" + scenario + "-" + now.strftime("%Y.%m.%d.%H.%M.%S")
                print("Let's run the e2e job, distro %s driver %s " % (distro, driver))
                print("-------------")
                print("-------------")
                print("Running the e2e job for: " + str(pr.number) + " " + pr.title)
                print("-------------")
                print("-------------")
                print("-------------")

                # We update the status to show that we are executing the e2e test
                print("Current status")
                print(repo.get_commit(sha=sha).get_statuses())
                repo.get_commit(sha=sha).create_status(state="pending",
                                                       target_url=url + str(pipeline_id),
                                                       description="Running...",
                                                       context="%s-%s-%s-master-%s-worker-%s" % (distro,
                                                                                                 driver,
                                                                                                 master,
                                                                                                 worker,
                                                                                                 scenario))
                print("The pipeline ID is: " + str(pipeline_id))
                print("The clouds.yml path is: " + str(vars_file_path))
                # We trigger the e2e job
                start_time = time.time()
                try:
                    print("We call the downstream job configuring its parameters")
                    subprocess.check_call("./ci/run_kubeinit.sh %s %s %s %s %s %s %s %s" % (str(branch.name),
                                                                                            str(pr.number),
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
                    output = 1

                try:
                    print("Render ara data")
                    subprocess.check_call("./ci/ara.sh %s" % (str(job_name) + "-" + str(output)), shell=True)
                except Exception as e:
                    print('An exception hapened rendering ara data')
                    print(e)
                    output = 1

                print("starting the uploader job")
                # No matter if the job passed or failed we always use go as the suffix
                # upload_error = upload_logs_to_github(str(job_name) + "-" + str(output), gh_token)
                upload_error = upload_logs_to_google_cloud(str(job_name) + "-" + str(output), gc_token_path)
                render_index(gc_token_path)
                print("finishing the uploader job")

                if output == 0:
                    state = "success"
                else:
                    state = "failure"

                desc = ("Ended with %s in %s minutes" % (state, round((time.time() - start_time) / 60, 2)))

                print(desc)
                print(state)

                if upload_error == 1:
                    dest_url = url + str(pipeline_id)
                else:
                    dest_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/pr/' + str(job_name) + "-" + str(output) + '/index.html'

                print("The destination URL is: " + dest_url)
                # We update the status with the job result
                repo.get_commit(sha=sha).create_status(state=state,
                                                       target_url=dest_url,
                                                       description=desc,
                                                       context="%s-%s-%s-master-%s-worker-%s" % (distro,
                                                                                                 driver,
                                                                                                 master,
                                                                                                 worker,
                                                                                                 scenario))
            else:
                print("No need to do anything")
            if execute:
                exit()


if __name__ == "__main__":
    main()
