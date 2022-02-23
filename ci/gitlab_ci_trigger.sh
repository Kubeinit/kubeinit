#!/bin/bash
set -e

#############################################################################
#                                                                           #
# Copyright kubeinit contributors.                                          #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License"); you may   #
# not use this file except in compliance with the License. You may obtain   #
# a copy of the License at:                                                 #
#                                                                           #
# http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
# License for the specific language governing permissions and limitations   #
# under the License.                                                        #
#                                                                           #
#############################################################################

ci_mock_cmd="${ci_mock_cmd:-0}"

install_deps() {
    echo "(gitlab_ci_trigger.sh) ==> Install packages dependencies"
    # Make sure dependencies are installed
    if [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
        sudo dnf install -y git jq gh
    fi

    if [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then
        sudo apt-get install -y git jq gh
    fi
}

run_pr() {
    echo "(gitlab_ci_trigger.sh) ==> Run PR"
    echo "(gitlab_ci_trigger.sh) ==> Cloning the repo"
    git clone https://github.com/kubeinit/kubeinit.git kubeinit-aux
    cd kubeinit-aux

    echo "(gitlab_ci_trigger.sh) ==> Get open PRs"
    pr_list=$(gh pr list --json title,number,labels)
    ci_label_found=0
    ci_verbosity_label_found=0
    test_params=''

    for pull_request in $(echo "${pr_list}" | jq -r '.[] | @base64'); do
        pr_number=$(echo $pull_request | base64 --decode | jq -r ${1} | jq .number)
        pr_labels=$(echo ${pull_request} | base64 --decode | jq -r ${1} | jq .labels)
        for row in $(echo "${pr_labels}" | jq -r '.[] | @base64'); do
            _jq() {
                echo ${row} | base64 --decode | jq -r ${1}
            }
            label=$(_jq '.name')
            label_regex=".*-.*-.*-.*-.*-.*"
            singlenode_label_regex=".*-.*-.*-.*-1-.*"
            verbosity_regex="verbosity=.*"
            if [[ $label =~ $label_regex ]];then
                echo "(gitlab_ci_trigger.sh) ==> There was found a job matching label: $label" ;
                echo "(gitlab_ci_trigger.sh) ==> We assign the matching PR: $pr_number" ;
                test_params+="--pr_id=${pr_number} "

                if [ "$ci_label_found" -eq "0" ]; then
                    test_params+="--job_label=${label} "
                fi
                ci_label_found=1
            else
                if [[ $label =~ $verbosity_regex ]]; then
                    test_params+="${label} "
                fi
            fi
        done
        if [ "$ci_label_found" -eq "1" ]; then
            echo "(gitlab_ci_trigger.sh) ==> We found a PR with a label that needs to be executed"
            break;
        fi
    done

    if [ "$ci_label_found" -eq "0" ]; then
        echo "(gitlab_ci_trigger.sh) ==> We didnt find any PR matching a job label"
        test_params="--pr_id=none "
    fi
}

run_periodic() {
    echo "(gitlab_ci_trigger.sh) ==> Run periodic"
    # JOB_TYPE='periodic=random'
    # JOB_TYPE='periodic=all'
    # JOB_TYPE='periodic=k8s-libvirt-1-0-1-h'
    test_params+=$JOB_TYPE
}

main() {
    echo "(gitlab_ci_trigger.sh) ==> Job type: $JOB_TYPE"

    pr_regex='pr.*'
    if [[ $JOB_TYPE =~ $pr_regex ]]; then
        echo "(gitlab_ci_trigger.sh) ==> PR testing"
        install_deps
        run_pr
    fi

    periodic_regex='periodic.*'
    if [[ $JOB_TYPE =~ $periodic_regex ]]; then
        echo "(gitlab_ci_trigger.sh) ==> Periodic job testing"
        run_periodic
    fi

    ci_cmd="./ci/launch_e2e.py ${test_params}"

    if [ "$ci_mock_cmd" -eq "0" ]; then
        echo "(gitlab_ci_trigger.sh) ==> Run the deployment script"
        ${ci_cmd}
    else
        echo "(gitlab_ci_trigger.sh) ==> Mock test"
        echo "(gitlab_ci_trigger.sh) ==> OUTPUT: ${ci_cmd}"
    fi
}

main
