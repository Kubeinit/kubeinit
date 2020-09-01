#!/usr/bin/python

"""
Plugin example to be removed.

This is a plugin example to be removed
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: package

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
'''


from ansible.module_utils.basic import AnsibleModule


def run_module():
    """Execute the module."""
    module_args = dict(
        path=dict(type='str', required=True),
    )

    result = dict(
        # This module doesn't change anything.
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result['resources'] = "test"

    module.exit_json(**result)


def main():
    """Run the main method."""
    run_module()


if __name__ == '__main__':
    main()
