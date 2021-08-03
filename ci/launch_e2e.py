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

import os
import re
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

#
# We only execute the e2e jobs for those PR having
# `whitelist_domain` as part of the committer's email
#


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
        c_type = '((?!1)[0-9]+)'

    now = datetime.now()
    if job_type == 'pr':
        #
        # We will check for labels in opened PRs in the main
        # kubeinit project
        #
        print("'launch_e2e.py' ==> Pull request job")
        gh = Github(os.environ['GH_TOKEN'])
        gc_token_path = os.environ['GC_STORAGE_KEY']
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
                sha = pr.head.sha
                execute = False
                for label in labels:
                    # DISTRO-DRIVER-CONTROLLERS-COMPUTES-HYPERVISORS-[VIRTUAL_SERVICES|CONTAINERIZED_SERVICES]-[LAUNCH_FROM_CONTAINER|LAUNCH_FROM_HOST]
                    if re.match(r"[a-z|0-9|\.]+-[a-z]+-\d+-\d+-" + c_type + "-[v|c]-[c|h]", label):
                        print("'launch_e2e.py' ==> Matching a PR label")
                        params = label.split("-")
                        distro = params[0]
                        driver = params[1]
                        masters = params[2]
                        workers = params[3]
                        hypervisors = params[4]
                        services = params[5]
                        launch_from = params[6]
                        execute = True
                        remove_label(label, pr, repo)
                        break
                if execute:
                    repo.get_commit(sha=sha).create_status(state="pending",
                                                           target_url=url + str(pipeline_id),
                                                           description="Running...",
                                                           context="%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                             driver,
                                                                                             masters,
                                                                                             workers,
                                                                                             hypervisors,
                                                                                             services,
                                                                                             launch_from))
                    repository = repo.name
                    branch_name = branch.name
                    pr_number = pr.number
                    start_time = time.time()
                    timestamp = now.strftime("%Y.%m.%d.%H.%M.%S")
                    job_name = (distro + "-" +
                                driver + "-" +
                                masters + "-" +
                                workers + "-" +
                                hypervisors + "-" +
                                services + "-" +
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
                                         services,
                                         job_type,
                                         pipeline_id,
                                         gc_token_path,
                                         repository,
                                         branch_name,
                                         pr_number,
                                         launch_from,
                                         job_name)
                    if output == 0:
                        state = "success"
                    else:
                        state = "failure"

                    desc = ("Ended with %s in %s minutes" % (state,
                                                             round((time.time() - start_time) / 60, 2)))

                    dest_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/' + str(job_name) + "-" + str(output) + '/index.html'
                    print("'launch_e2e.py' ==> The destination URL is: " + dest_url)
                    # We update the status with the job result
                    repo.get_commit(sha=sha).create_status(state=state,
                                                           target_url=dest_url,
                                                           description=desc,
                                                           context="%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                             masters,
                                                                                             driver,
                                                                                             workers,
                                                                                             hypervisors,
                                                                                             services,
                                                                                             launch_from))

                else:
                    print("'launch_e2e.py' ==> No need to do anything")
                    exit()

    if re.match(r"periodic(=[a-z|0-9|,|\.]+)?", job_type):
        #
        # We will run the periodic jobs depending on the
        # hardware we called this script from [multinode-singlenode]
        #
        gc_token_path = os.environ['GC_STORAGE_KEY']
        pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

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
            if re.match(r"[a-z|0-9|\.]+-[a-z]+-\d+-\d+-" + c_type + "-[v|c]-[c|h]", label):
                print("'launch_e2e.py' ==> Matching a PR label")
                params = label.split("-")
                distro = params[0]
                driver = params[1]
                masters = params[2]
                workers = params[3]
                hypervisors = params[4]
                services = params[5]
                launch_from = params[6]
                execute = True

            if execute:
                repository = 'kubeinit/kubeinit'
                branch_name = 'main'
                pr_number = 'latest'
                timestamp = 'weekly'
                job_name = (distro + "-" +
                            driver + "-" +
                            masters + "-" +
                            workers + "-" +
                            hypervisors + "-" +
                            services + "-" +
                            launch_from + "-" +
                            job_type + "-" +
                            pipeline_id + "-" +
                            timestamp
                            )

                # print(distro)
                # raise Exception("'launch_e2e.py' ==> STOP!")

                run_e2e_job(distro,
                            driver,
                            masters,
                            workers,
                            hypervisors,
                            services,
                            job_type,
                            pipeline_id,
                            gc_token_path,
                            repository,
                            branch_name,
                            pr_number,
                            launch_from,
                            job_name)

    if job_type == 'submariner':
        gh = Github(os.environ['GH_SUBMARINER_TOKEN'])
        gc_token_path = os.environ['GC_STORAGE_KEY']

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
                    services = "v"
                    launch_from = "h"
                    execute = True
                    remove_label("check-okd-rke", pr, repo)

                if execute:
                    repo.get_commit(sha=sha).create_status(state="pending",
                                                           target_url=url + str(pipeline_id),
                                                           description="Running...",
                                                           context="%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                             driver,
                                                                                             masters,
                                                                                             workers,
                                                                                             hypervisors,
                                                                                             services,
                                                                                             launch_from))
                    repository = repo.name
                    branch_name = branch.name
                    pr_number = pr.number
                    start_time = time.time()
                    timestamp = now.strftime("%Y.%m.%d.%H.%M.%S")
                    job_name = (distro + "-" +
                                driver + "-" +
                                masters + "-" +
                                workers + "-" +
                                hypervisors + "-" +
                                services + "-" +
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
                                         services,
                                         job_type,
                                         pipeline_id,
                                         gc_token_path,
                                         repository,
                                         branch_name,
                                         pr_number,
                                         launch_from,
                                         job_name)
                    if output == 0:
                        state = "success"
                    else:
                        state = "failure"

                    desc = ("Ended with %s in %s minutes" % (state,
                                                             round((time.time() - start_time) / 60, 2)))
                    dest_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/' + str(job_name) + "-" + str(output) + '/index.html'

                    print("'launch_e2e.py' ==> The destination URL is: " + dest_url)
                    # We update the status with the job result
                    repo.get_commit(sha=sha).create_status(state=state,
                                                           target_url=dest_url,
                                                           description=desc,
                                                           context="%s-%s-%s-%s-%s-%s-%s" % (distro,
                                                                                             driver,
                                                                                             masters,
                                                                                             workers,
                                                                                             hypervisors,
                                                                                             services,
                                                                                             launch_from))
                else:
                    print("'launch_e2e.py' ==> No need to do anything")
                    exit()


def run_e2e_job(distro, driver, masters, workers,
                hypervisors, services, job_type,
                pipeline_id, gc_token_path, repository,
                branch_name, pr_number, launch_from, job_name):
    """Run the e2e job."""
    output = 0
    badge_text = "%s-%s-%s-%s-%s-%s-%s" % (distro,
                                           driver,
                                           masters,
                                           workers,
                                           hypervisors,
                                           services,
                                           launch_from)
    badge_code = badge(left_text=badge_text,
                       right_text='passing',
                       right_color='green')
    try:
        print("'launch_e2e.py' ==> We call the downstream job configuring its parameters")
        print("'launch_e2e.py' ==> Deployment command")
        deployment_command = "./ci/run_e2e.sh %s %s %s %s %s %s %s %s %s %s %s" % (str(repository),
                                                                                   str(branch_name),
                                                                                   str(pr_number),
                                                                                   str(distro),
                                                                                   str(driver),
                                                                                   str(masters),
                                                                                   str(workers),
                                                                                   str(hypervisors),
                                                                                   str(services),
                                                                                   str(job_type),
                                                                                   str(launch_from))
        print(deployment_command)
        subprocess.check_call(deployment_command, shell=True)
    except Exception as e:
        print("'launch_e2e.py' ==> An exception hapened executing Ansible")
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
            split_job_name[8] = 'pid'
            job_name = "-".join(split_job_name)
            file_output = 'u'
        subprocess.check_call("./ci/ara.sh %s" % (str(job_name) + "-" +
                                                  str(file_output)),
                              shell=True)
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
        split_job_name[8] = 'pid'
        job_name = "-".join(split_job_name)
        file_output = 'u'

    print("'launch_e2e.py' ==> starting the uploader job")
    upload_logs_to_google_cloud(str(job_name) + "-" + str(file_output),
                                gc_token_path)

    print("'launch_e2e.py' ==> rendering the index job page")
    render_index(gc_token_path)

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

    elif (not re.match(r"periodic(=[a-z|0-9|,|\.]+)?", sys.argv[2]) and sys.argv[2] != 'pr' and sys.argv[2] != 'submariner'):
        print("'launch_e2e.py' ==> The third argument must be [periodic|pr|submariner]")
        print("'launch_e2e.py' ==> periodic can be periodic|periodic=okd,eks|periodic=okd.rke ...")
        sys.exit()

    print("---")
    print("'launch_e2e.py' ==> Main argument: " + sys.argv[0])
    print("'launch_e2e.py' ==> Cluster type: " + sys.argv[1])
    print("'launch_e2e.py' ==> Job type: " + sys.argv[2])
    print("---")
    main(sys.argv[1], sys.argv[2])
