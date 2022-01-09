from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: cli_args
    author: Kubeinit contributors
    short_description: Lookup Ansible command-line arguments
    description: Retrieves the values of Ansible command-line arguments
    options:
      _terms:
        description: The command-line arguments to look up
        required: True
"""

EXAMPLES = """
    - name: Show remote_user command line argument (-u | --user <username>)
      debug: msg="{{ lookup('config', 'remote_user') }}"
"""

RETURN = """
_raw:
  description:
    - value(s) of the arguments from the command-line
  type: raw
"""

from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase

try:
  from __main__ import context
except ImportError:
  context = False

class LookupModule(LookupBase):

  def run(self, terms, variables=None, **kwargs):

    ret = []

    if context:
      for term in terms:
        if not isinstance(term, string_types):
          raise AnsibleOptionsError('Invalid setting identifier, "%s" is not a string, its a %s' % (term, type(term)))

        result = context.CLIARGS[term]
        ret.append(result)

    return ret
