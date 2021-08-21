#!/usr/bin/env python

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
import sys
import urllib.request
from pathlib import Path

from ansible.errors import AnsibleParserError
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.task import Task
from ansible.vars.manager import VariableManager

import ruamel.yaml
import ruamel.yaml.util

yaml = ruamel.yaml.YAML()

Task._validate_attributes = lambda *args: None


def get_tasks(obj):
    """Get each task."""
    if isinstance(obj, list):
        for o in obj:
            yield from get_tasks(o)
    else:
        found = False
        for key in ('tasks',
                    'pre_tasks',
                    'post_tasks',
                    'handlers',
                    'block',
                    'rescue',
                    'always'):
            if obj.get(key):
                found = True
                yield from get_tasks(obj.get(key))
        if not found:
            yield obj


def check_tasks(file):
    """Parse a tasks file."""
    print(file)
    errors = []
    with open(file) as f:
        data = yaml.load(f)

    # If data is None it means is not a valid YAML file
    if data:
        for ds in get_tasks(data):
            try:
                task = Task.load(ds,
                                 variable_manager=variable_manager,
                                 loader=loader)
                route_class = ['modules',
                               'connection',
                               'module_utils',
                               'cliconf',
                               'terminal',
                               'action',
                               'become',
                               'cache',
                               'callback',
                               'doc_fragments',
                               'filter',
                               'httpapi',
                               'inventory',
                               'lookup',
                               'netconf',
                               'shell',
                               'test']

                for route in route_class:
                    module = routing[route].get(task.action,
                                                {}).get('redirect')
                    if module:
                        errors.append((file, task.action, "this task should be called as: " + str(module)))
                        break

                print(task.action)
                if '.' not in task.action:
                    errors.append((file, task.action, "all tasks must have dots in namespace"))

                if task.action == 'ansible.builtin.shell':
                    if 'executable' not in task._attributes['args']:
                        errors.append((file, task.action, "must define the executable as an args, like /bin/bash"))

            except AnsibleParserError:
                pass
            except Exception:
                pass
    return errors


loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='localhost,')
variable_manager = VariableManager(loader=loader, inventory=inventory)

url = ("https://raw.githubusercontent.com/"
       "ansible/ansible/devel/lib/ansible/config/"
       "ansible_builtin_runtime.yml")

response = urllib.request.urlopen(url)
data = response.read()

routing = yaml.load(data)['plugin_routing']

dirname = os.path.abspath(os.path.dirname(__file__))
search_folder = os.path.join(dirname, '../kubeinit/roles/')

to_fix = []

for path in Path(search_folder).rglob('*.yml'):
    to_fix = to_fix + check_tasks(path)

if len(to_fix) > 0:
    msg = 'There are some tasks not properly defined: ' + str(to_fix)
    print(msg)
    sys.exit(1)
