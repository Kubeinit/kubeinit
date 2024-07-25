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

from jinja2 import Environment, FileSystemLoader

from kubeinit_ci_utils import get_periodic_jobs_labels


def main():
    """Run the main method."""
    labels = get_periodic_jobs_labels()

    jobs = []

    # If using Backblaze B2
    data_backend_url = 'https://ci.kubeinit.org/file/kubeinit-ci/jobs/'
    # If using Google cloud
    # data_backend_url = 'https://storage.googleapis.com/kubeinit-ci/jobs/''
    for label in labels:

        if re.match(r"[a-z|0-9|\.]+-[a-z]+-\d+-\d+-\d+-[c|h]", label):
            print("'render_periodic_jobs_page.py' ==> Matching a periodic job label")
            params = label.split("-")
            distro = params[0]
            driver = params[1]
            masters = params[2]
            workers = params[3]
            hypervisors = params[4]
            launch_from = params[5]

            if distro == 'okd':
                distro = "Origin Distribution of K8s"
            elif distro == 'kid':
                distro = "KubeInit distro"
            elif distro == 'k8s':
                distro = "Vanilla K8s"
            elif '.' in distro:
                distro = distro.upper().replace('.', '/')

            if launch_from == 'h':
                launch_from = "Host"
            elif launch_from == 'c':
                launch_from = "Container"
        else:
            print("'render_periodic_jobs_page.py' ==> This label do not match")
            print(label)
            raise Exception("'render_periodic_jobs_page.py' ==> This label do not match: %s" % (label))

        jobs.append({'distro': distro,
                     'driver': driver,
                     'masters': masters,
                     'workers': workers,
                     'hypervisors': hypervisors,
                     'launch_from': launch_from,
                     'url': "<a href='" + data_backend_url + label + "-periodic-pid-weekly-u/index.html'><img height='20px' src='" + data_backend_url + label + "-periodic-pid-weekly-u/badge_status.svg'/></a>"})

    path = os.path.join(os.path.dirname(__file__))
    file_loader = FileSystemLoader(searchpath=path)
    env = Environment(loader=file_loader)
    template_index = "periodic_jobs.md.j2"
    print("'render_periodic_jobs_page.py' ==> The path for the template is: " + path)
    template = env.get_template(template_index)
    output = template.render(jobs=jobs)

    with open("periodic_jobs.md", "w+") as text_file:
        text_file.write(output)


if __name__ == "__main__":
    main()
