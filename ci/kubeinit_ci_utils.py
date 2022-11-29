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

"""KubeInit's CI utils."""

import os
import random
import re
import tempfile
import time

from b2sdk.v2 import B2Api, InMemoryAccountInfo

from google.cloud import storage

from jinja2 import Environment, FileSystemLoader

import requests


def render_index(destination='b2'):
    """Render and upload the index file."""
    if destination == 'gcp':
        # Google cloud Storage init
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ['GC_STORAGE_KEY']
        bucket_name = "kubeinit-ci"
        client = storage.Client()
        data_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/'
        prefix = 'jobs/'
        delimiter = None

        root_blobs = list(client.list_blobs(bucket_name,
                                            prefix=prefix,
                                            delimiter=delimiter))
        filtered = list(dict.fromkeys([re.sub('/.*', '', sub.name.replace(prefix, '')) for sub in root_blobs]))

    if destination == 'b2':
        # The prefix should be jobs/

        b2_token_id = os.environ['B2_STORAGE_ID']
        b2_token_key = os.environ['B2_STORAGE_KEY']
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        bucket_name = "kubeinit-ci"
        b2_api.authorize_account("production", b2_token_id, b2_token_key)
        bucket = b2_api.get_bucket_by_name(bucket_name)
        data_url = 'https://ci.kubeinit.org/file/kubeinit-ci/jobs/'
        prefix = 'jobs/'
        root_blobs = []
        for file_version, folder_name in bucket.ls(folder_to_list='jobs', latest_only=True):
            print("'kubeinit_ci_utils.py' ==> Folder name: " + folder_name)
            root_blobs.append(file_version.file_name)
        filtered = list(dict.fromkeys([re.sub('/.*', '', sub.replace(prefix, '')) for sub in root_blobs]))

    jobs = []

    print("'kubeinit_ci_utils.py' ==> Rendering CI jobs index page")
    print("'kubeinit_ci_utils.py' ==> Filtered blobs")
    print(filtered)

    print("'kubeinit_ci_utils.py' ==> Rendering page indexes")
    for idx, blob in enumerate(filtered):
        print(str(blob))
        fields = blob.split("-")
        stat = fields[9]
        if stat == '0':
            status = 'Passed'
            badge = 'success'
        elif stat == '1':
            status = 'Failed'
            badge = 'danger'
        # If not stat == 'u' it means this is a PR job
        # we check the index content to verify it didnt fail.
        elif stat == 'u':
            index_data_url = data_url + blob + '/index.html'
            resp = requests.get(url=index_data_url, timeout=5, verify=False)
            m = re.search("btn-danger", resp.text)
            if m:
                print("'kubeinit_ci_utils.py' ==> The periodic job failed...")
                status = 'Failed'
                badge = 'danger'
            else:
                print("'kubeinit_ci_utils.py' ==> The periodic job passed...")
                status = 'Passed'
                badge = 'success'
        else:
            status = 'Running'
            badge = 'warning'

        extra_data_date_url = data_url + blob + '/records/1.html'
        resp = requests.get(url=extra_data_date_url, timeout=5, verify=False)

        m = re.search("[0-9][0-9][0-9][0-9]\\.[0-9][0-9]\\.[0-9][0-9]\\.[0-9][0-9]\\.[0-9][0-9]\\.[0-9][0-9]", resp.text)
        # stat == 'u' means that this is a periodic job
        if m and stat == 'u':
            date = str(m.group(0))
        else:
            date = fields[8]

        m = re.search("https:\\/\\/gitlab\\.com\\/kubeinit\\/kubeinit\\/-\\/jobs\\/[0-9]+", resp.text)
        # stat == 'u' means that this is a periodic job
        if m:
            job_id = str(m.group(0))
        else:
            job_id = 'Missing field in the record data.'

        m = re.search("The pull request is: [0-9]+", resp.text)
        if m:
            pr_number = str(m.group(0).split(' ')[-1])
        else:
            pr_number = 'Periodic'

        jobs.append({'status': status,
                     'index': idx,
                     'distro': fields[0],
                     'driver': fields[1],
                     'masters': fields[2],
                     'workers': fields[3],
                     'hypervisors': fields[4],
                     'launch_from': fields[5],
                     'job_type': fields[6],
                     'id': job_id,
                     'pr_number': pr_number,
                     'date': date,
                     'badge': badge,
                     'url': data_url + blob + '/index.html'})

    path = os.path.join(os.path.dirname(__file__))
    file_loader = FileSystemLoader(searchpath=path)
    env = Environment(loader=file_loader)
    template_index = "kubeinit_ci_logs.html.j2"
    print("'kubeinit_ci_utils.py' ==> The path for the template is: " + path)
    template = env.get_template(template_index)
    output = template.render(jobs=jobs)

    if destination == 'gcp':
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob('index.html')
        blob.upload_from_string(output, content_type='text/html')
    if destination == 'b2':
        tmp = tempfile.NamedTemporaryFile()
        with open(tmp.name, 'w') as f:
            f.write(output)
        file_info = {'type': 'Main index file'}
        bucket.upload_local_file(
            local_file=tmp.name,
            file_name='index.html',
            file_infos=file_info,
        )


def upload_logs_to_google_cloud(job_path):
    """Upload the CI results to Google cloud Cloud Storage."""
    return_code = 0

    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ['GC_STORAGE_KEY']
        bucket_name = "kubeinit-ci"
        bucket = storage.Client().get_bucket(bucket_name)

        print("'kubeinit_ci_utils.py' ==> ----Uploading logs----")

        print("'kubeinit_ci_utils.py' ==> Path at terminal when executing this file")
        print(os.getcwd() + "\n")

        print("'kubeinit_ci_utils.py' ==> This file path, relative to os.getcwd()")
        print(__file__ + "\n")

        file_list = []
        path_to_upload = os.path.join(os.getcwd(), job_path)
        print("'kubeinit_ci_utils.py' ==> Path to upload: " + path_to_upload)

        for r, _d, f in os.walk(path_to_upload):
            for file in f:
                file_list.append(os.path.join(r, file))

        prefix_path = os.getcwd() + '/'
        print("'kubeinit_ci_utils.py' ==> The initial path: " + prefix_path + " will be removed")

        for entry in file_list:
            try:
                blob = bucket.blob('jobs/' + entry.replace(prefix_path, ''))
                blob.upload_from_filename(entry)
            except Exception as e:
                print("'kubeinit_ci_utils.py' ==> An exception hapened adding the initial log files, some files could not be added")
                print(e)
                return_code = 1
    except Exception as e:
        print("'kubeinit_ci_utils.py' ==> An exception hapened uploading files to Google Cloud Storage")
        print(e)
        return_code = 1
    return return_code


def upload_files_to_b2(job_path, prefix='jobs/'):
    """Upload the CI results to Backblaze b2."""
    return_code = 0

    # The prefix should be jobs/

    b2_token_id = os.environ['B2_STORAGE_ID']
    b2_token_key = os.environ['B2_STORAGE_KEY']

    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        bucket_name = "kubeinit-ci"
        b2_api.authorize_account("production", b2_token_id, b2_token_key)

        bucket = b2_api.get_bucket_by_name(bucket_name)
        print("'kubeinit_ci_utils.py' ==> ----Uploading logs to B2----")

        print("'kubeinit_ci_utils.py' ==> Path at terminal when executing this file")
        print(os.getcwd() + "\n")

        print("'kubeinit_ci_utils.py' ==> This file path, relative to os.getcwd()")
        print(__file__ + "\n")

        file_list = []
        path_to_upload = os.path.join(os.getcwd(), job_path)
        print("'kubeinit_ci_utils.py' ==> Path to upload: " + path_to_upload)

        for r, _d, f in os.walk(path_to_upload):
            for file in f:
                file_list.append(os.path.join(r, file))

        prefix_path = os.getcwd() + '/'
        print("'kubeinit_ci_utils.py' ==> The initial path: " + prefix_path + " will be removed")

        for entry in file_list:
            try:
                # blob = bucket.blob('jobs/' + entry.replace(prefix_path, ''))
                # blob.upload_from_filename(entry)
                file_info = {'how': 'good-file'}
                bucket.upload_local_file(
                    local_file=entry,
                    file_name=prefix + entry.replace(prefix_path, ''),
                    file_infos=file_info,
                )
            except Exception as e:
                print("'kubeinit_ci_utils.py' ==> An exception hapened adding the initial log files, some files could not be added")
                print(e)
                return_code = 1
    except Exception as e:
        print("'kubeinit_ci_utils.py' ==> An exception hapened uploading files to Backblaze B2")
        print(e)
        return_code = 1
    return return_code


def remove_label(the_label, pr, repo):
    """Remove a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda labl: labl.name == the_label, labels)):
        r_label = repo.get_label(the_label)
    else:
        r_label = repo.create_label(the_label, "32CD32")
    pr.remove_from_labels(r_label)


def add_label(the_label, pr, repo):
    """Assign a label."""
    labels = [label for label in repo.get_labels()]
    if any(filter(lambda labl: labl.name == the_label, labels)):
        new_label = repo.get_label(the_label)
    else:
        new_label = repo.create_label(the_label, "32CD32")
    pr.add_to_labels(new_label)


def clean_old_files_b2():
    """Clean the old files in B2."""
    b2_token_id = os.environ['B2_STORAGE_ID']
    b2_token_key = os.environ['B2_STORAGE_KEY']

    #
    # This method is higly API intensive as it
    # will list all the files in the bucket,
    # use it with precaution!!!!!!!!!!!!!!
    #

    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    bucket_name = "kubeinit-ci"
    b2_api.authorize_account("production", b2_token_id, b2_token_key)

    bucket = b2_api.get_bucket_by_name(bucket_name)

    older_than = (10 * 24 * 3600 * 1000)  # 10 days in milliseconds
    compare_older_than = int(round(time.time() * 1000) - int(older_than))

    for file_version, folder_name in bucket.ls(recursive=True):
        # The following condition allows only to remove PR job files
        # older than 10 days, in this case we will skip all the periodic
        # jobs files and the main index file.
        if 'jobs' in file_version.file_name and 'pr' in file_version.file_name:
            if compare_older_than > int(file_version.upload_timestamp):  # This means that is older than 10 days
                print("'kubeinit_ci_utils.py' ==> Deleting files from:" + str(folder_name))
                b2_api.delete_file_version(file_version.id_, file_version.file_name)


def get_periodic_jobs_labels(cluster_type='all', distro='all'):
    """Get the labels for an specific distro."""
    # DISTRO-DRIVER-CONTROLLERS-COMPUTES-HYPERVISORS-[VIRTUAL_SERVICES|CONTAINERIZED_SERVICES]-[LAUNCH_FROM_CONTAINER|LAUNCH_FROM_HOST]

    if cluster_type == 'multinode':
        cluster_type_regex = '^.+-.+-.+-.+-[2-9]-.+$'
    elif cluster_type == 'singlenode':
        cluster_type_regex = '^.+-.+-.+-.+-1-.+$'
    # This includes the label for both single node and multinode scenarios
    elif cluster_type == 'all':
        cluster_type_regex = '^.+-.+-.+-.+-[1-9]-.+$'

    cluster_pattern = re.compile(cluster_type_regex)

    cdk_configs = ["cdk-libvirt-3-1-2-h",
                   "cdk-libvirt-3-1-1-h",
                   "cdk-libvirt-1-1-1-h",
                   "cdk-libvirt-1-2-1-h"]

    okd_configs = ["okd-libvirt-3-1-1-h",
                   "okd-libvirt-3-0-2-h",
                   "okd-libvirt-1-1-1-h",
                   "okd-openstack-1-1-0-h",
                   "okd-libvirt-1-0-1-h"]

    rke_configs = ["rke-libvirt-3-1-2-h",
                   "rke-libvirt-3-0-1-h",
                   "rke-libvirt-1-1-1-h",
                   "rke-libvirt-1-0-1-h"]

    k8s_configs = ["k8s-libvirt-3-1-1-h",
                   "k8s-libvirt-3-0-2-h",
                   "k8s-libvirt-1-1-1-h",
                   "k8s-libvirt-1-0-1-h"]

    eks_configs = ["eks-libvirt-3-1-2-h",
                   "eks-libvirt-3-0-1-h",
                   "eks-libvirt-1-1-1-h",
                   "eks-libvirt-1-0-1-h"]

    kid_configs = ["kid-libvirt-3-1-1-h",
                   "kid-libvirt-3-0-2-h",
                   "kid-libvirt-1-1-1-h",
                   "kid-libvirt-1-0-1-h"]

    multicluster_configs = ["k8s.rke-libvirt-1-0-1-h",
                            "okd.rke-libvirt-1-2-1-h",
                            "okd.rke-libvirt-3-1-1-h"]

    if re.match(r"([a-z|0-9|\.]+-[a-z]+-[1-9]-[0-9]-[1-9]-[c|h],?)+", distro):
        print("'kubeinit_ci_utils.py' ==> We are requesting specific job labels")
        req_labels = set(distro.split(","))
        all_labels = set(okd_configs + kid_configs + eks_configs + rke_configs + cdk_configs + k8s_configs + multicluster_configs)
        if (req_labels.issubset(all_labels)):
            print("'kubeinit_ci_utils.py' ==> The requested labels are defined correctly")
            # We return the labels filtered by cluster_type, multinode or singlenode
            filtered_return = [lab for lab in req_labels if cluster_pattern.match(lab)]
            print("'kubeinit_ci_utils.py' ==> " + str(filtered_return))
            return filtered_return
        else:
            print("'kubeinit_ci_utils.py' ==> The requested labels are not a subset of the allowed labels")
            raise Exception("'kubeinit_ci_utils.py' ==> STOP!")
    elif distro == 'random':
        print("'kubeinit_ci_utils.py' ==> Returning 4 random scenarios to test")
        # If the distro parameter is random we return 4 random distros to test
        all_scenarios = okd_configs + kid_configs + eks_configs + rke_configs + cdk_configs + k8s_configs + multicluster_configs
        return_labels = random.sample(all_scenarios, 4)
        # We return the labels filtered by cluster_type, multinode or singlenode
        filtered_return = [lab for lab in return_labels if cluster_pattern.match(lab)]
        print("'kubeinit_ci_utils.py' ==> " + str(filtered_return))
        return filtered_return
    elif distro == "all":
        print("'kubeinit_ci_utils.py' ==> Appending all configs")
        return_labels = okd_configs + kid_configs + eks_configs + rke_configs + cdk_configs + k8s_configs + multicluster_configs
        # We return the labels filtered by cluster_type, multinode or singlenode
        filtered_return = [lab for lab in return_labels if cluster_pattern.match(lab)]
        print("'kubeinit_ci_utils.py' ==> " + str(filtered_return))
        return filtered_return
    else:
        configs = []
        if '.' in distro or "multicluster" in distro:
            print("'kubeinit_ci_utils.py' ==> Appending the multicluster configs")
            configs = configs + multicluster_configs
        if 'okd' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending OKD configs")
            configs = configs + okd_configs
        if 'rke' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending RKE configs")
            configs = configs + rke_configs
        if 'kid' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending KID configs")
            configs = configs + kid_configs
        if 'eks' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending EKS configs")
            configs = configs + eks_configs
        if 'cdk' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending CDK configs")
            configs = configs + cdk_configs
        if 'k8s' in distro and '.' not in distro:
            print("'kubeinit_ci_utils.py' ==> Appending K8S configs")
            configs = configs + k8s_configs
        # We return the labels filtered by cluster_type, multinode or singlenode
        filtered_return = [lab for lab in configs if cluster_pattern.match(lab)]
        print("'kubeinit_ci_utils.py' ==> " + str(filtered_return))
        return filtered_return
