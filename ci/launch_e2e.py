#!/bin/python3

"""
Copyright kubeinit contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

#############################################
# Any change done in this file needs to be  #
# force pushed first to the GitLab instance #
# so the changes are refreshed when the job #
# starts to run                             #
#############################################

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime

from github import Github

from kubeinit_ci_utils import (get_periodic_jobs_labels,
                               remove_label,
                               render_index,
                               upload_logs_to_google_cloud)

from pybadges import badge


GH_LABELS = []


def main(cluster_type, job_type):
    """Run the main method."""
    #
    # This method can deploy multiple
    # cluster_type configurations like:
    # multinode or singlenode
    # And multiple job_types like:
    # pr, periodic or submariner
    #

    if cluster_type == 'singlenode':
        c_type = '1'
    else:
        c_type = '[2-9]'

    now = datetime.now()

    #
    # KubeInit's pull request check
    #
    if job_type == 'pr':
        #
        # We will check for labels in opened PRs in the main
        # kubeinit project
        #
        print("'launch_e2e.py' ==> Pull request job")
        gh = Github(os.environ['GH_TOKEN'])
        pipeline_id = os.getenv('CI_PIPELINE_ID', 0)
        repo = gh.get_repo("kubeinit/kubeinit")
        branches = repo.get_branches()
        output = 0
        url = os.getenv('CI_PIPELINE_URL', "")
        print("'launch_e2e.py' ==> The job results will be published in runtime at: " + url)
        for branch in branches:
            for pr in repo.get_pulls(state='open',
                                     sort='created',
                                     base=branch.name):
                labels = [item.name for item in pr.labels]

                #
                # Adjust dinamically the verbosity based on a GH label.
                #
                ansible_label = 'verbosity'
                ansible_label_found = next((s for s in labels if ansible_label in s), None)
                if ansible_label_found:
                    global GH_LABELS
                    GH_LABELS.append('GH_ANSIBLE_VERBOSITY=' + ansible_label_found.split("=")[1])

                sha = pr.head.sha
                execute = False
                print("'launch_e2e.py' ==> The current labels in PR: " + str(pr.number) + " are:")
                print(labels)
                for label in labels:
                    # DISTRO-DRIVER-CONTROLLERS-COMPUTES-HYPERVISORS-[VIRTUAL_SERVICES|CONTAINERIZED_SERVICES]-[LAUNCH_FROM_CONTAINER|LAUNCH_FROM_HOST]
                    if re.match(r"[a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-" + c_type + "-[c|h]", label):
                        print("'launch_e2e.py' ==> Matching a PR label")
                        params = label.split("-")
                        distro = params[0]
                        driver = params[1]
                        masters = params[2]
                        workers = params[3]
                        hypervisors = params[4]
                        launch_from = params[5]
                        execute = True
                        remove_label(label, pr, repo)
                        break
                if execute:
                    repo.get_commit(sha=sha).create_status(state="pending",
                                                           target_url=url + str(pipeline_id),
                                                           description="Running...",
                                                           context="%s-%s-%s-%s-%s-%s" % (distro,
                                                                                          driver,
                                                                                          masters,
                                                                                          workers,
                                                                                          hypervisors,
                                                                                          launch_from))
                    repository = 'kubeinit/kubeinit'
                    branch_name = branch.name
                    pr_number = pr.number
                    start_time = time.time()
                    timestamp = now.strftime("%Y.%m.%d.%H.%M.%S")
                    job_name = (distro + "-" +
                                driver + "-" +
                                masters + "-" +
                                workers + "-" +
                                hypervisors + "-" +
                                launch_from + "-" +
                                job_type + "-" +
                                pipeline_id + "-" +
                                timestamp
                                )

                    output = run_e2e_job(distro,
                                         driver,
                                         masters,
                                         workers,
                                         hypervisors,
                                         job_type,
                                         pipeline_id,
                                         repository,
                                         branch_name,
                                         pr_number,
                                         launch_from,
                                         job_name)
                    if output == 0:
                        state = "success"
                    else:
                        state = "failure"

                    dur_mins = str(round((time.time() - start_time) / 60, 2))
                    desc = ("Ended with %s in %s minutes" % (state, dur_mins))

                    dest_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/' + str(job_name) + "-" + str(output) + '/index.html'
                    print("'launch_e2e.py' ==> The destination URL is: " + dest_url)
                    # We update the status with the job result
                    repo.get_commit(sha=sha).create_status(state=state,
                                                           target_url=dest_url,
                                                           description=desc,
                                                           context="%s-%s-%s-%s-%s-%s" % (distro,
                                                                                          driver,
                                                                                          masters,
                                                                                          workers,
                                                                                          hypervisors,
                                                                                          launch_from))
                    pr.create_issue_comment(body="%s-%s-%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                 driver,
                                                                                 masters,
                                                                                 workers,
                                                                                 hypervisors,
                                                                                 launch_from,
                                                                                 state,
                                                                                 str(start_time),
                                                                                 dur_mins))

                    if output == 0:
                        exit()
                    else:
                        exit(1)
                else:
                    print("'launch_e2e.py' ==> No need to do anything")
                    print("'launch_e2e.py' ==> Trying another PR...")
                    # We can not have exit() here, in that case we will be
                    # checking only the first PR, if the first PR do not have
                    # the labels, then we need to check the next one until we find a
                    # PR with the labels.

    #
    # KubeInit's periodic job check
    #
    if (re.match(r"periodic(=[a-z|0-9|,|\.]+)?", job_type) or
            re.match(r"periodic=([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+", job_type) or
            job_type == 'periodic=random'):

        #
        # We will run the periodic jobs depending on the
        # hardware we called this script from [multinode-singlenode]
        #
        gh = Github(os.environ['GH_TOKEN'])
        pipeline_id = os.getenv('CI_PIPELINE_ID', 0)
        repo = gh.get_repo("kubeinit/kubeinit")

        output = "go"
        # Something linke:
        # url = "https://gitlab.com/kubeinit/kubeinit-ci/pipelines/"
        url = os.getenv('CI_PIPELINE_URL', "")
        print("'launch_e2e.py' ==> The job results will be published in runtime at: " + url)

        if '=' in job_type:
            labels = get_periodic_jobs_labels(job_type.split("=")[1])
        else:
            labels = get_periodic_jobs_labels('all')
        job_type = job_type.split("=")[0]
        print("'launch_e2e.py' ==> All the labels to check are")
        print(labels)

        for label in labels:
            execute = False
            print("'launch_e2e.py' ==> The label to be processed is: " + label)

            # DISTRO-DRIVER-CONTROLLERS-COMPUTES-HYPERVISORS-[VIRTUAL_SERVICES|CONTAINERIZED_SERVICES]-[LAUNCH_FROM_CONTAINER|LAUNCH_FROM_HOST]
            if re.match(r"[a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-" + c_type + "-[c|h]", label):
                print("'launch_e2e.py' ==> Matching a PR label")
                params = label.split("-")
                distro = params[0]
                driver = params[1]
                masters = params[2]
                workers = params[3]
                hypervisors = params[4]
                launch_from = params[5]
                execute = True

            if execute:
                repository = 'kubeinit/kubeinit'
                branch_name = 'main'
                pr_number = 'latest'
                timestamp = 'weekly'
                start_time = time.time()
                job_name = (distro + "-" +
                            driver + "-" +
                            masters + "-" +
                            workers + "-" +
                            hypervisors + "-" +
                            launch_from + "-" +
                            job_type + "-" +
                            pipeline_id + "-" +
                            timestamp
                            )

                # print(distro)
                # raise Exception("'launch_e2e.py' ==> STOP!")

                output = run_e2e_job(distro,
                                     driver,
                                     masters,
                                     workers,
                                     hypervisors,
                                     job_type,
                                     pipeline_id,
                                     repository,
                                     branch_name,
                                     pr_number,
                                     launch_from,
                                     job_name)

                if output == 0:
                    state = "success"
                else:
                    state = "failure"
                dur_mins = str(round((time.time() - start_time) / 60, 2))
                issue = repo.get_issue(number=595)
                issue.create_comment(body="%s-%s-%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                          driver,
                                                                          masters,
                                                                          workers,
                                                                          hypervisors,
                                                                          launch_from,
                                                                          state,
                                                                          str(start_time),
                                                                          dur_mins))

    #
    # KubeInit's submariner PR check
    #
    if job_type == 'submariner':
        gh = Github(os.environ['GH_SUBMARINER_TOKEN'])

        pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

        repo = gh.get_repo("submariner-io/submariner-operator")
        branches = repo.get_branches()

        output = 0

        url = os.getenv('CI_PIPELINE_URL', "")
        print("'launch_e2e.py' ==> The job results will be published in runtime at: " + url)

        for branch in branches:
            for pr in repo.get_pulls(state='open',
                                     sort='created',
                                     base=branch.name):
                labels = [item.name for item in pr.labels]
                sha = pr.head.sha
                execute = False
                if ("check-okd-rke" in labels):
                    distro = "okd.rke"
                    driver = "libvirt"
                    masters = "1"
                    workers = "2"
                    hypervisors = "1"
                    launch_from = "h"
                    execute = True
                    remove_label("check-okd-rke", pr, repo)

                if execute:
                    repo.get_commit(sha=sha).create_status(state="pending",
                                                           target_url=url + str(pipeline_id),
                                                           description="Running...",
                                                           context="%s-%s-%s-%s-%s-%s" % (distro,
                                                                                          driver,
                                                                                          masters,
                                                                                          workers,
                                                                                          hypervisors,
                                                                                          launch_from))
                    repository = repo.name
                    print("'launch_e2e.py' ==> The repository name is: " + repository)
                    branch_name = branch.name
                    pr_number = pr.number
                    start_time = time.time()
                    timestamp = now.strftime("%Y.%m.%d.%H.%M.%S")
                    job_name = (distro + "-" +
                                driver + "-" +
                                masters + "-" +
                                workers + "-" +
                                hypervisors + "-" +
                                launch_from + "-" +
                                job_type + "-" +
                                pipeline_id + "-" +
                                timestamp
                                )
                    output = run_e2e_job(distro,
                                         driver,
                                         masters,
                                         workers,
                                         hypervisors,
                                         job_type,
                                         pipeline_id,
                                         repository,
                                         branch_name,
                                         pr_number,
                                         launch_from,
                                         job_name)
                    if output == 0:
                        print("'launch_e2e.py' ==> The current job succeeded")
                        state = "success"
                    else:
                        print("'launch_e2e.py' ==> The current job failed")
                        state = "failure"

                    dur_mins = str(round((time.time() - start_time) / 60, 2))
                    desc = ("Ended with %s in %s minutes" % (state, dur_mins))

                    dest_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/' + str(job_name) + "-" + str(output) + '/index.html'
                    print("'launch_e2e.py' ==> Desc message: " + desc)

                    print("'launch_e2e.py' ==> The destination URL is: " + dest_url)
                    # We update the status with the job result
                    repo.get_commit(sha=sha).create_status(state=state,
                                                           target_url=dest_url,
                                                           description=desc,
                                                           context="%s-%s-%s-%s-%s-%s" % (distro,
                                                                                          driver,
                                                                                          masters,
                                                                                          workers,
                                                                                          hypervisors,
                                                                                          launch_from))
                    pr.create_issue_comment(body="%s-%s-%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                 driver,
                                                                                 masters,
                                                                                 workers,
                                                                                 hypervisors,
                                                                                 launch_from,
                                                                                 state,
                                                                                 str(start_time),
                                                                                 dur_mins))
                    if output == 0:
                        exit()
                    else:
                        exit(1)
                else:
                    print("'launch_e2e.py' ==> No need to do anything")
                    exit()


def run_e2e_job(distro, driver, masters, workers,
                hypervisors, job_type,
                pipeline_id, repository,
                branch_name, pr_number, launch_from, job_name):
    """Run the e2e job."""
    output = 0
    badge_text = "%s-%s-%s-%s-%s-%s" % (distro,
                                        driver,
                                        masters,
                                        workers,
                                        hypervisors,
                                        launch_from)
    badge_code = badge(left_text=badge_text,
                       right_text='passing',
                       right_color='green')
    try:
        print("'launch_e2e.py' ==> We call the downstream job configuring its parameters")

        # The first parameter of the command are the variables values we might append to
        # the deployment command
        deployment_command = "%s ./ci/launch_e2e.sh %s %s %s %s %s %s %s %s %s %s" % (str(' '.join(GH_LABELS)),
                                                                                      str(repository),
                                                                                      str(branch_name),
                                                                                      str(pr_number),
                                                                                      str(distro),
                                                                                      str(driver),
                                                                                      str(masters),
                                                                                      str(workers),
                                                                                      str(hypervisors),
                                                                                      str(job_type),
                                                                                      str(launch_from))
        print("'launch_e2e.py' ==> The deployment command is:")
        print(deployment_command)

        launch_output = subprocess.run(deployment_command, shell=True, check=True)
        print("'launch_e2e.py' ==> ./ci/launch_e2e.sh output")
        print(launch_output)
    except Exception as e:
        print("'launch_e2e.py' ==> An exception hapened executing Ansible, the playbook failed")
        badge_code = badge(left_text=badge_text,
                           right_text='failure',
                           right_color='red')
        print(e)
        output = 1

    with open("/root/badge_status.svg", "w+") as text_file:
        text_file.write(badge_code)

    try:
        print("'launch_e2e.py' ==> Render ara data")
        file_output = output
        if job_type == 'periodic':
            # We change here the pipeline id from GitLab
            # to have always the same value so we can fetch
            # it from the job status page
            split_job_name = job_name.split('-')
            split_job_name[7] = 'pid'
            job_name = "-".join(split_job_name)
            file_output = 'u'
        print("'launch_e2e.py' ==> Ara command")
        ara_command = "./ci/launch_e2e_ara.sh %s" % (str(job_name) + "-" + str(file_output))
        print(ara_command)
        ara_output = subprocess.run(ara_command, shell=True, check=True)
        print("'launch_e2e.py' ==> ./ci/launch_e2e_ara.sh output")
        print(ara_output)
    except Exception as e:
        print("'launch_e2e.py' ==> An exception hapened rendering ara data")
        print(e)
        output = 1

    file_output = output
    if job_type == 'periodic':
        # We change here the pipeline id from GitLab
        # to have always the same value so we can fetch
        # it from the job status page
        split_job_name = job_name.split('-')
        split_job_name[7] = 'pid'
        job_name = "-".join(split_job_name)
        file_output = 'u'

    root_folder_path = os.path.join(os.getcwd(), str(job_name) + "-" + str(file_output))

    print("'launch_e2e.py' ==> starting the uploader job")
    upload_logs_to_google_cloud(str(job_name) + "-" + str(file_output))

    print("'launch_e2e.py' ==> rendering the index job page")
    render_index()

    print("'launch_e2e.py' ==> Removing aux files: " + root_folder_path)
    shutil.rmtree(root_folder_path)

    print("'launch_e2e.py' ==> finishing the uploader job")
    return output


if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print("'launch_e2e.py' ==> This can only take arguments like:")
        print("'launch_e2e.py' ==> launch_e2e.py [singlenode|multinode] [periodic|pr|submariner]")
        sys.exit()
    elif (sys.argv[1] != 'multinode' and sys.argv[1] != 'singlenode'):
        print("'launch_e2e.py' ==> The second argument must be [singlenode|multinode]")
        sys.exit()

    elif (not re.match(r"periodic=([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+", sys.argv[2]) and
          not re.match(r"periodic(=[a-z|0-9|,|\.]+)?", sys.argv[2]) and
          sys.argv[2] != 'pr' and
          sys.argv[2] != 'submariner'):
        print("'launch_e2e.py' ==> The third argument must be [periodic|pr|submariner]")
        print("'launch_e2e.py' ==> periodic, can be periodic|periodic=okd,eks|periodic=okd.rke ...")
        print("'launch_e2e.py' ==> also the periodic job can trigger a specfic label like:")
        print("'launch_e2e.py' ==> periodic=okd-libvirt-3-1-1-h")
        sys.exit()

    elif (re.match(r"periodic=([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[2-9]-[c|h],?)+", sys.argv[2]) and
          sys.argv[1] == 'singlenode'):
        print("'launch_e2e.py' ==> The parameter " + sys.argv[2] + " and " + sys.argv[1] + " are incompatible")
        print("'launch_e2e.py' ==> singlenode configurations can not have multinode labels")
        sys.exit()

    elif (re.match(r"periodic=([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-1-[c|h],?)+", sys.argv[2]) and
          sys.argv[1] == 'multinode'):
        print("'launch_e2e.py' ==> The parameter " + sys.argv[2] + " and " + sys.argv[1] + " are incompatible")
        print("'launch_e2e.py' ==> multinode configurations can not have singlenode labels")
        sys.exit()

    elif (re.match(r"periodic=([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-0-[c|h],?)+", sys.argv[2])):
        print("'launch_e2e.py' ==> Is not possible to deploy with 0 hypervisors")
        sys.exit()

    print("---")
    print("'launch_e2e.py' ==> Main argument: " + sys.argv[0])
    print("'launch_e2e.py' ==> Cluster type: " + sys.argv[1])
    print("'launch_e2e.py' ==> Job type: " + sys.argv[2])
    print("---")
    main(sys.argv[1], sys.argv[2])
