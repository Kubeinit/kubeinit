# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import subprocess

def test_molecule(pytestconfig):
    cmd = ['python', '-m', 'molecule', '--debug']
    scenario = pytestconfig.getoption("scenario")
    ansible_args = pytestconfig.getoption("ansible_args")
    if ansible_args:
        cmd.append('converge')
        if scenario:
            cmd.extend(['--scenario-name', scenario])
        cmd.append('--')
        cmd.extend(ansible_args.split())
    else:
        cmd.append('test')
        if scenario:
            cmd.extend(['--scenario-name', scenario])
        else:
            cmd.append('--all')
    try:
        assert subprocess.call(cmd) == 0
    finally:
        if ansible_args:
            cmd = ['python', '-m', 'molecule', 'destroy']
            if scenario:
                cmd.extend(['--scenario-name', scenario])
            subprocess.call(cmd)
