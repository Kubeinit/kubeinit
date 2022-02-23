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

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime

from github import Github

from kubeinit_ci_utils import (clean_old_files_b2,
                               get_periodic_jobs_labels,
                               remove_label,
                               render_index,
                               upload_files_to_b2)

from pybadges import badge


GH_LABELS = []


def main(job_type, cluster_type, job_label, pr_id, verbosity):
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
        url = os.getenv('CI_PIPELINE_URL', "")
        print("'launch_e2e.py' ==> The job results will be published in runtime at: " + url)
        global GH_LABELS
        GH_LABELS.append('GH_ANSIBLE_VERBOSITY=' + verbosity)
        pr = repo.get_pull(pr_id)
        sha = pr.head.sha
        execute = False
        # In a PR we only test one label at the time
        print("'launch_e2e.py' ==> The label to be tested in PR: " + str(pr_id) + " is: " + str(job_label))

        if re.match(r"[a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-" + c_type + "-[c|h]", job_label):
            print("'launch_e2e.py' ==> Matching a PR label")
            params = job_label.split("-")
            distro = params[0]
            driver = params[1]
            masters = params[2]
            workers = params[3]
            hypervisors = params[4]
            launch_from = params[5]
            execute = True
            remove_label(job_label, pr_id, repo)

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
            branch_name = 'main'  # The main brach for this project is called 'main'
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

    #
    # KubeInit's periodic job check
    #
    if (re.match(r"([a-z|0-9|,|\.]+)?", job_label) or
            re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+", job_label) or
            job_label == 'random' or job_label == 'all') and job_type == 'periodic':

        #
        # We will run the periodic jobs depending on the
        # hardware we called this script from [multinode-singlenode]
        #
        gh = Github(os.environ['GH_TOKEN'])
        pipeline_id = os.getenv('CI_PIPELINE_ID', 0)
        repo = gh.get_repo("kubeinit/kubeinit")

        output = "go"
        # Something like:
        # url = "https://gitlab.com/kubeinit/kubeinit-ci/pipelines/"
        url = os.getenv('CI_PIPELINE_URL', "")
        print("'launch_e2e.py' ==> The job results will be published in runtime at: " + url)

        labels = get_periodic_jobs_labels(job_label)
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

    with open("/tmp/badge_status.svg", "w+") as text_file:
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
    upload_files_to_b2(str(job_name) + "-" + str(file_output))

    print("'launch_e2e.py' ==> cleaning old B2 files")
    clean_old_files_b2()

    print("'launch_e2e.py' ==> rendering the index job page")
    render_index()

    print("'launch_e2e.py' ==> Removing aux files: " + root_folder_path)
    shutil.rmtree(root_folder_path)

    print("'launch_e2e.py' ==> finishing the uploader job")
    return output


def valid_labels_regex(arg_value, pat=re.compile(r"^all|random|([a-z|0-9|,|\.]+)|([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+$")):
    """Get the params regex."""
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


if __name__ == "__main__":
    """Run the main job."""

    #
    # This script can run like:
    #
    # launch_e2e.py --job_type=pr
    # launch_e2e.py --job_type=pr --pr_id=154
    # launch_e2e.py --job_type=pr --pr_id=submariner
    # launch_e2e.py --job_type=periodic --job_label=eks-libvirt-3-0-1-h
    # launch_e2e.py --job_type=periodic --job_label=eks-libvirt-3-0-1-h,cdk-libvirt-1-0-1-h
    # launch_e2e.py --job_type=periodic --cluster_type=singlenode --job_label=random
    # launch_e2e.py --job_type=periodic --cluster_type=singlenode --job_label=all
    # launch_e2e.py --job_type=periodic --cluster_type=singlenode --job_label=okd
    # launch_e2e.py --job_type=periodic --cluster_type=multinode --job_label=all
    # launch_e2e.py --job_type=periodic --cluster_type=multinode --job_label=okd
    #

    parser = argparse.ArgumentParser(prog='launch_e2e.py')
    parser.add_argument('--job_type',
                        action='store',
                        required=True,
                        choices=['pr', 'periodic', 'submariner'],
                        help='The type of job to run, per PR, periodic or submariner')
    parser.add_argument('--verbosity',
                        action='store',
                        default='v',
                        help='The Ansible verbosity')
    parser.add_argument('--pr_id',
                        action='store',
                        default='none',
                        help='The number of the PR to be tested')
    parser.add_argument('--cluster_type',
                        action='store',
                        choices=['multinode', 'singlenode'],
                        help='The type of the cluster, multinode or singlenode')
    parser.add_argument('--job_label',
                        action='store',
                        type=valid_labels_regex,
                        help='The CI job label to be executed')

    args = parser.parse_args()
    # The job type is a mandatory parameter
    if args.job_type == "periodic":
        if args.job_label is not None and '-' not in args.job_label and args.cluster_type is None:
            parser.error('If there is no job label with the cluster spec, then, the cluster type must be defined')
        if args.cluster_type is None and args.job_label is None:
            parser.error('--cluster_type or --job_label should be defined')

    if (args.job_label is not None and not re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+", args.job_label) and not re.match(r"([a-z|0-9|,|\.]+)?", args.job_label) and args.job_type != 'pr' and args.job_type != 'submariner'):
        print("'launch_e2e.py' ==> The third argument must be [periodic|pr|submariner]")
        print("'launch_e2e.py' ==> periodic, can be periodic|periodic=okd,eks|periodic=okd.rke ...")
        print("'launch_e2e.py' ==> also the periodic job can trigger a specfic label like:")
        print("'launch_e2e.py' ==> periodic=okd-libvirt-3-1-1-h")
        sys.exit()
    elif (args.job_label is not None and re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[2-9]-[c|h],?)+", args.job_label) and args.cluster_type == 'singlenode'):
        print("'launch_e2e.py' ==> The parameter " + args.job_label + " and " + args.cluster_type + " are incompatible")
        print("'launch_e2e.py' ==> singlenode configurations can not have multinode labels")
        sys.exit()
    elif (args.job_label is not None and re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-1-[c|h],?)+", args.job_label) and args.cluster_type == 'multinode'):
        print("'launch_e2e.py' ==> The parameter " + args.job_label + " and " + args.cluster_type + " are incompatible")
        print("'launch_e2e.py' ==> multinode configurations can not have singlenode labels")
        sys.exit()
    elif (args.job_label is not None and re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-0-[c|h],?)+", args.job_label)):
        print("'launch_e2e.py' ==> Is not possible to deploy with 0 hypervisors")
        sys.exit()
    elif (args.job_label is not None and re.match(r"([a-z|0-9|\.]+-[a-z]+-0-[0-9]-[0-9]-[c|h],?)+", args.job_label)):
        print("'launch_e2e.py' ==> Is not possible to deploy with 0 controllers")
        sys.exit()

    print("---")
    print(args)
    print("---")

    main(job_type=args.job_type,
         cluster_type=args.cluster_type,
         job_label=args.job_label,
         pr_id=args.pr_id,
         verbosity=args.verbosity)
