#!/bin/python3

"""Main CI job script for submariner tests."""

import os
import subprocess
import time

from github import Github

gh = Github(os.environ['GH_TOKEN'])

vars_file_path = os.getenv('VARS_FILE', "")
pipeline_id = os.getenv('CI_PIPELINE_ID', 0)

repo = gh.get_repo("submariner-io/submariner-operator")
branches = repo.get_branches()

# Something linke:
# url = "https://gitlab.com/kubeinit/kubeinit-ci/pipelines/"
url = os.getenv('CI_PIPELINE_URL', "")

#
# We only execute the submariner job for a specific PR
#


def main():
    """Run the main method."""
    for branch in branches:
        for pr in repo.get_pulls(state='open', sort='created', base=branch.name):
            labels = [item.name for item in pr.labels]

            sha = pr.head.sha
            committer_email = repo.get_commit(sha=sha).commit.committer.email
            print(committer_email)

            execute = False
            scenario = "default"

            #
            # Charmed Distribution of Kubernetes
            #
            if ("check-okd-rke" in labels):
                distro = "multiple"
                driver = "libvirt"
                master = "1"
                worker = "2"
                execute = True
                scenario = "submariner"

            if execute:
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
                # repo.get_commit(sha=sha).create_status(state="pending",
                #                                        target_url=url + str(pipeline_id),
                #                                        description="Running...",
                #                                        context="%s-%s-%s-master-%s-worker-%s" % (distro,
                #                                                                                  driver,
                #                                                                                  master,
                #                                                                                  worker,
                #                                                                                  scenario))
                print("The pipeline ID is: " + str(pipeline_id))
                print("The clouds.yml path is: " + str(vars_file_path))
                # We trigger the e2e job
                start_time = time.time()
                try:
                    print("We call the downstream job configuring its parameters")
                    output = subprocess.check_call("./ci/run_submariner.sh %s %s %s %s %s %s %s %s" % (str(branch.name),
                                                                                                       str(pr.number),
                                                                                                       str(vars_file_path),
                                                                                                       str(distro),
                                                                                                       str(driver),
                                                                                                       str(master),
                                                                                                       str(worker),
                                                                                                       str(scenario)),
                                                   shell=True)
                except Exception:
                    output = 1
                desc = ("Successful in %s minutes" % (round((time.time() - start_time) / 60, 2)))

                if output == 0:
                    state = "success"
                else:
                    state = "failure"

                print(desc)
                print(state)
                # We update the status with the job result
                # repo.get_commit(sha=sha).create_status(state=state,
                #                                        target_url=url + str(pipeline_id),
                #                                        description=desc,
                #                                        context="%s-%s-%s-master-%s-worker-%s" % (distro,
                #                                                                                  driver,
                #                                                                                  master,
                #                                                                                  worker,
                #                                                                                  scenario))
            else:
                print("No need to do anything")
            if execute:
                exit()


def remove_label(the_label, pr):
    """Remove a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda l: l.name == the_label, labels)):
        r_label = repo.get_label(the_label)
    else:
        r_label = repo.create_label(the_label, "32CD32")
    pr.remove_from_labels(r_label)


def assign_label(the_label, pr):
    """Assign a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda l: l.name == the_label, labels)):
        new_label = repo.get_label(the_label)
    else:
        new_label = repo.create_label(the_label, "32CD32")
    pr.add_to_labels(new_label)


if __name__ == "__main__":
    main()
