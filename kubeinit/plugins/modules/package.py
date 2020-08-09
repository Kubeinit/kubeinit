#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: read_resources

short_description: Example module

version_added: "2.9"

author: "KubeInit (@kubeinit)"

description:
  - "This is an example description"

options:
  path:
    description:
      - Resources YAML file to read.
    required: true
    type: str
'''

EXAMPLES = '''
- name: This is an example
  kubeinit.kubeinit.package:
    path: /opt/test/networks.yml
  register: read_networks

- name: Debug-print resources
  debug:
    msg: "{{ read_networks.resources }}"
'''

RETURN = '''
resources:
    description: List of resources deserialized from YAML file
    returned: success
    type: complex
    contains:
        type:
            description: Type of the resource.
            returned: success
            type: str
        params:
            description: Resource parameters important for import.
            returned: success
            type: complex
        info:
            description: Additional resource information, not needed for import.
            returned: success
            type: complex
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
    )

    result = dict(
        # This module doesn't change anything.
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        # Module doesn't change anything, we can let it run as-is in
        # check mode.
        supports_check_mode=True,
    )

    struct = filesystem.load_resources_file(module.params['path'])
    result['resources'] = struct['resources']

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
