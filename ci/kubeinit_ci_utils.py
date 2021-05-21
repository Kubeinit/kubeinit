#!/bin/python3

"""KubeInit's CI utils."""

import base64
import os

from github import Github
from github import InputGitTreeElement

from google.cloud import storage


def upload_logs_to_google_cloud(pipeline_id, gc_token_path):
    """Upload the CI results to Google cloud Cloud Storage."""
    return_code = 0

    try:
        storage_client = storage.Client()
        bucket_name = "kubeinit-ci"
        bucket = storage_client.create_bucket(bucket_name)

        print("----Uploading logs----")

        print("Path at terminal when executing this file")
        print(os.getcwd() + "\n")

        print("This file path, relative to os.getcwd()")
        print(__file__ + "\n")

        file_list = []
        path_to_upload = os.path.join(os.getcwd(), pipeline_id)
        print("Path to upload: " + path_to_upload)

        for r, _d, f in os.walk(path_to_upload):
            for file in f:
                file_list.append(os.path.join(r, file))

        print("CI results to be stored")
        print(file_list)

        prefix_path = os.getcwd() + '/'
        print('The initial path: ' + prefix_path + ' will be removed')

        for entry in file_list:
            try:
                blob = bucket.blob(entry)
                blob.upload_from_filename(entry)
            except Exception as e:
                print('An exception hapened adding the initial log files, some files could not be added')
                print(e)
                return_code = 1
    except Exception as e:
        print('An exception hapened uploading files to Google Cloud Storage')
        print(e)
        return_code = 1
    return return_code


def upload_logs_to_github(pipeline_id, gh_token):
    """Upload the CI results to GitHub."""
    return_code = 0

    try:
        gh = Github(gh_token)
        print("----Uploading logs----")

        print("Uploading CI results to the bot account")
        repobot = gh.get_repo('kubeinit-bot/kubeinit-ci-results')

        print("Path at terminal when executing this file")
        print(os.getcwd() + "\n")

        print("This file path, relative to os.getcwd()")
        print(__file__ + "\n")

        file_list = []
        path_to_upload = os.path.join(os.getcwd(), pipeline_id)
        print("Path to upload: " + path_to_upload)

        for r, _d, f in os.walk(path_to_upload):
            for file in f:
                file_list.append(os.path.join(r, file))

        print("CI results to be stored")
        print(file_list)
        commit_message = 'Log files for the job number: ' + pipeline_id

        element_list = list()

        prefix_path = os.getcwd() + '/'
        print('The initial path: ' + prefix_path + ' will be removed')

        for entry in file_list:
            try:
                with open(entry, 'rb') as input_file:
                    print('Opening files for reading data')
                    dataraw = input_file.read()
                    print('Encoding as base64')
                    data = base64.b64encode(dataraw)

                print('Adding blobs')
                if entry.endswith('.png') or entry.endswith('.jpg') or entry.endswith('.ttf') or entry.endswith('.woff') or entry.endswith('.woff2') or entry.endswith('.ico'):
                    print('A binary file')
                    # We add to the commit the literal image as a string in base64
                    blob = repobot.create_git_blob(data.decode("utf-8"), "base64")
                    tree_element = InputGitTreeElement(path=entry.replace(prefix_path, ''), mode='100644', type='blob', sha=blob.sha)
                    element_list.append(tree_element)
                else:
                    print('A text file')
                    blob = repobot.create_git_blob(data.decode("utf-8"), encoding="base64")
                    blob = repobot.get_git_blob(sha=blob.sha)
                    tree_element = InputGitTreeElement(path=entry.replace(prefix_path, ''), mode='100644', type='blob', content=base64.b64decode(blob.content).decode('utf-8'))
                    element_list.append(tree_element)
            except Exception as e:
                print('An exception hapened adding the initial log files, some files could not be added')
                print(e)
                return_code = 1
        head_sha = repobot.get_branch('main').commit.sha
        base_tree = repobot.get_git_tree(sha=head_sha)
        tree = repobot.create_git_tree(element_list, base_tree)
        parent = repobot.get_git_commit(sha=head_sha)
        commit = repobot.create_git_commit(commit_message, tree, [parent])
        master_refs = repobot.get_git_ref('heads/main')
        master_refs.edit(sha=commit.sha)
    except Exception as e:
        print('An exception hapened files to GitHub')
        print(e)
        return_code = 1
    return return_code


def remove_label(the_label, pr, repo):
    """Remove a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda l: l.name == the_label, labels)):
        r_label = repo.get_label(the_label)
    else:
        r_label = repo.create_label(the_label, "32CD32")
    pr.remove_from_labels(r_label)


def add_label(the_label, pr, repo):
    """Assign a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda l: l.name == the_label, labels)):
        new_label = repo.get_label(the_label)
    else:
        new_label = repo.create_label(the_label, "32CD32")
    pr.add_to_labels(new_label)
