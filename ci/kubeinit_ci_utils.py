#!/bin/python3

"""KubeInit's CI utils."""

import base64
import os
import re

from github import Github
from github import InputGitTreeElement

from google.cloud import storage

from jinja2 import Environment, FileSystemLoader


def render_index(gc_token_path):
    """Render and upload the index file."""
    # Google cloud Storage init
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gc_token_path
    bucket_name = "kubeinit-ci"
    client = storage.Client()

    jobs = []

    print('Periodic jobs to render')
    prefix_periodic = 'jobs/periodic/'
    prefix_pr = 'jobs/pr/'
    delimiter = None

    root_periodic_blobs = list(client.list_blobs(bucket_name,
                                                 prefix=prefix_periodic,
                                                 delimiter=delimiter))

    filtered = list(dict.fromkeys([re.sub('/.*', '', sub.name.replace(prefix_periodic, '')) for sub in root_periodic_blobs]))

    for idx, blob in enumerate(filtered):
        fields = blob.split("-")
        stat = fields[7]
        if stat == '0':
            status = 'Passed'
            badge = 'success'
        elif stat == '1':
            status = 'Failed'
            badge = 'danger'
        elif stat == 'go':
            status = 'Periodic'
            badge = 'primary'
        else:
            status = 'Running'
            badge = 'warning'

        jobs.append({'status': status,
                     'index': idx,
                     'id': fields[0],
                     'distro': fields[1],
                     'driver': fields[2],
                     'masters': fields[3],
                     'workers': fields[4],
                     'scenario': fields[5],
                     'date': fields[6],
                     'badge': badge,
                     'url': 'https://storage.googleapis.com/kubeinit-ci/jobs/periodic/' + blob + '/index.html'})

    print('PR jobs to render')
    root_pr_blobs = list(client.list_blobs(bucket_name,
                                           prefix=prefix_pr,
                                           delimiter=delimiter))

    filtered = list(dict.fromkeys([re.sub('/.*', '', sub.name.replace(prefix_pr, '')) for sub in root_pr_blobs]))

    for idx, blob in enumerate(filtered):
        fields = blob.split("-")
        stat = fields[7]
        if stat == '0':
            status = 'Passed'
            badge = 'success'
        elif stat == '1':
            status = 'Failed'
            badge = 'danger'
        elif stat == 'go':
            status = 'Periodic'
            badge = 'primary'
        else:
            status = 'Running'
            badge = 'warning'

        jobs.append({'status': status,
                     'index': idx,
                     'id': fields[0],
                     'distro': fields[1],
                     'driver': fields[2],
                     'masters': fields[3],
                     'workers': fields[4],
                     'scenario': fields[5],
                     'date': fields[6],
                     'badge': badge,
                     'url': 'https://storage.googleapis.com/kubeinit-ci/jobs/pr/' + blob + '/index.html'})

    path = os.path.join(os.path.dirname(__file__))
    file_loader = FileSystemLoader(searchpath=path)
    env = Environment(loader=file_loader)
    template_index = "kubeinit_ci_logs.html.j2"
    print("The path for the template is: " + path)
    template = env.get_template(template_index)
    output = template.render(jobs=jobs)

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('index.html')
    blob.upload_from_string(output, content_type='text/html')


def upload_logs_to_google_cloud(pipeline_id, gc_token_path):
    """Upload the CI results to Google cloud Cloud Storage."""
    return_code = 0

    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gc_token_path
        bucket_name = "kubeinit-ci"
        bucket = storage.Client().get_bucket(bucket_name)

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

        if 'periodic' in pipeline_id:
            type = 'jobs/periodic'
        else:
            type = 'jobs/pr'

        for entry in file_list:
            try:
                blob = bucket.blob(type + '/' + entry.replace(prefix_path, ''))
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
