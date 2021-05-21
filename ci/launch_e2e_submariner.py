#!/bin/python3

"""Main CI job script for submariner tests."""

import os
import subprocess
import time
from datetime import datetime

from github import Github

from kubeinit_ci_utils import remove_label, upload_logs_to_github, upload_logs_to_google_cloud

#
# We only execute the submariner job for a specific PR
#


def main():
    """Run the main method."""
    gh = Github(os.environ['GH_SUBMARINER_TOKEN'])
    gh_token = os.environ['GH_SUBMARINER_TOKEN']
    gc_token_path = os.environ['CG_STORAGE_KEY']

    vars_file_path = os.getenv('VARS_FILE', "")
    pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

    repo = gh.get_repo("submariner-io/submariner-operator")
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

            if ("check-okd-rke" in labels):
                distro = "okd.rke"
                driver = "libvirt"
                master = "1"
                worker = "2"
                execute = True
                scenario = "submariner"
                remove_label("check-okd-rke", pr, repo)

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
                    subprocess.check_call("./ci/run_submariner.sh %s %s %s %s %s %s %s %s" % (str(branch.name),
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
                upload_error = upload_logs_to_github(str(job_name) + "-" + str(output), gh_token)
                try:
                    upload_logs_to_google_cloud(str(job_name) + "-" + str(output), gc_token_path)
                except Exception as e:
                    print('An exception hapened uploading to Google cloud')
                    print(e)
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
                    dest_url = 'https://kubeinit-bot.github.io/kubeinit-ci-results/' + str(job_name) + "-" + str(output) + '/index.html'

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
