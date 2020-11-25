#!/bin/python3

"""Main CI job script for submariner tests."""

import base64
import os
import subprocess
import time

from github import Github
from github import InputGitTreeElement

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
                    output = subprocess.check_call("./ci/run_submariner.sh %s %s %s %s %s %s %s %s %s" % (str(branch.name),
                                                                                                          str(pr.number),
                                                                                                          str(vars_file_path),
                                                                                                          str(distro),
                                                                                                          str(driver),
                                                                                                          str(master),
                                                                                                          str(worker),
                                                                                                          str(scenario),
                                                                                                          str(pipeline_id)),
                                                   shell=True)
                    upload_logs(pipeline_id, './')
                    dest_url = 'https://kubeinit-bot.github.io/kubeinit-ci-results/' + pipeline_id + '/'
                    print("The destination URL is: " + dest_url)
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
                #                                        target_url=dest_url,
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


def upload_logs(pipeline_id, logs_folder):
    """Upload the CI results to GitHub."""
    print("----Uploading logs----")

    print("Uploading CI results to the bot account")
    repobot = gh.get_repo('kubeinit-bot/kubeinit-ci-results')

    print("Path at terminal when executing this file")
    print(os.getcwd() + "\n")

    print("This file path, relative to os.getcwd()")
    print(__file__ + "\n")

    file_list = []
    path_to_upload = os.path.join(os.getcwd(), 'tmp/kubeinit', pipeline_id)
    print("Path to upload: " + path_to_upload)

    for r, _d, f in os.walk(path_to_upload):
        for file in f:
            file_list.append(os.path.join(r, file))

    print("CI results to be stored")
    print(file_list)
    commit_message = 'Log files for the job number: ' + pipeline_id

    element_list = list()

    prefix_path = os.getcwd() + '/tmp/kubeinit/'
    print('The initial path: ' + prefix_path + ' will be removed')

    for entry in file_list:
        try:
            with open(entry, 'rb') as input_file:
                print('Opening files for reading data')
                dataraw = input_file.read()
                print('Encoding as base64')
                data = base64.b64encode(dataraw)

            print('Adding blobs')
            if entry.endswith('.png') or entry.endswith('.jpg') or entry.endswith('.woff2') or entry.endswith('.ico'):
                print('A binary file')
                # We add to the commit the literal image as a string in base64
                blob = repobot.create_git_blob(data.decode("utf-8"), encoding="utf-8")
            else:
                print('A text file')
                blob = repobot.create_git_blob(data.decode("utf-8"), encoding="base64")
            blob = repobot.get_git_blob(sha=blob.sha)
            tree_element = InputGitTreeElement(path=entry.replace(prefix_path, ''), mode='100644', type='blob', content=base64.b64decode(blob.content).decode('utf-8'))
            element_list.append(tree_element)
        except Exception as e:
            print('An exception hapened adding the initial log files, some files could not be added')
            print(e)
    head_sha = repobot.get_branch('main').commit.sha
    base_tree = repobot.get_git_tree(sha=head_sha)
    tree = repobot.create_git_tree(element_list, base_tree)
    parent = repobot.get_git_commit(sha=head_sha)
    commit = repobot.create_git_commit(commit_message, tree, [parent])
    master_refs = repobot.get_git_ref('heads/main')
    master_refs.edit(sha=commit.sha)

    print("We wait for 30 seconds to update the binary files")
    time.sleep(30)

    try:
        for entry in file_list:
            with open(entry, 'rb') as input_file:
                data = input_file.read()
            if entry.endswith('.png') or entry.endswith('.jpg') or entry.endswith('.woff2') or entry.endswith('.ico'):
                print('Opening again the file, the file to be opened is: ' + entry)
                old_file = repobot.get_contents(entry)
                commit = repobot.update_file(entry.replace(prefix_path, ''), 'Reconverting binary files for job number: ' + pipeline_id, data, old_file.sha)
    except Exception as e:
        print('An exception hapened updating the binary files, some files could not be added')
        print(e)


if __name__ == "__main__":
    main()
