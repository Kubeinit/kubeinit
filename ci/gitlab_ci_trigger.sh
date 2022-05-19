#!/bin/bash
set -ex

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

run_pr() {
    echo "(gitlab_ci_trigger.sh) ==> Run PR"
    echo "(gitlab_ci_trigger.sh) ==> Get open PRs"

    pr_list=$(gh pr list --json title,number,labels)
    ci_label_found=0
    ci_verbosity_label_found=0
    test_params=''
    test_params+="--job_type=pr "
    pr_id="${pr_id:-0}"

    for pull_request in $(echo "${pr_list}" | jq -r '.[] | @base64'); do
        pr_number=$(echo $pull_request | base64 --decode | jq -r ${1} | jq .number)
        pr_labels=$(echo ${pull_request} | base64 --decode | jq -r ${1} | jq .labels)
        for row in $(echo "${pr_labels}" | jq -r '.[] | @base64'); do
            _jq() {
                echo ${row} | base64 --decode | jq -r ${1}
            }
            label=$(_jq '.name')
            if [ "$CLUSTER_TYPE" = 'singlenode' ]; then
                label_regex=".*-.*-.*-.*-1-.*"
            else
                label_regex=".*-.*-.*-.*-[^1]-.*"
            fi
            verbosity_regex="verbosity=.*"
            if [[ $label =~ $label_regex ]];then
                echo "(gitlab_ci_trigger.sh) ==> There was found a job matching label: $label" ;
                echo "(gitlab_ci_trigger.sh) ==> We assign the matching PR: $pr_number" ;
                if [ "$ci_label_found" -eq "0" ]; then
                    test_params+="--job_label=${label} "
                    test_params+="--pr_id=${pr_number} "
                    pr_id=${pr_number}
                fi
                ci_label_found=1
            else
                if [[ $label =~ $verbosity_regex ]]; then
                    test_params+="--${label} "
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
        test_params="--job_type=pr --pr_id=none "
    else
        echo "(gitlab_ci_trigger.sh) ==> We found a PR that will be tested with a valid label"
        echo "(gitlab_ci_trigger.sh) ==> Downloading KubeInit's code that will be tested ..."
        git fetch origin pull/${pr_id}/head:testbranch
        git checkout testbranch
        git remote add upstream https://github.com/kubeinit/kubeinit.git
        git fetch upstream
        git rebase upstream/main
        echo "(gitlab_ci_trigger.sh) ==> Last 10 commit from this branch ..."
        git log -10 --pretty=oneline --abbrev-commit
    fi
}

get_code(){
    echo "(gitlab_ci_trigger.sh) ==> Cloning the repo"
    rm -rf kubeinit-aux
    git clone https://github.com/kubeinit/kubeinit.git kubeinit-aux
    cd kubeinit-aux
}

run_periodic() {
    echo "(gitlab_ci_trigger.sh) ==> Run periodic"
    if [[ $CLUSTER_TYPE ]]; then
        test_params+="--cluster_type=${CLUSTER_TYPE} "
    fi
    if [[ $JOB_TYPE ]]; then
        test_params+="--job_type=${JOB_TYPE} "
    fi
    if [[ $JOB_LABEL ]]; then
        test_params+="--job_label=${JOB_LABEL} "
    fi
}

main() {
    echo "(gitlab_ci_trigger.sh) ==> Script parameters:"
    echo "(gitlab_ci_trigger.sh) ==>   - Cluster type: $CLUSTER_TYPE"
    echo "(gitlab_ci_trigger.sh) ==>   - Job type: $JOB_TYPE"
    echo "(gitlab_ci_trigger.sh) ==>   - Job label: $JOB_LABEL"

    pr_regex='pr.*'
    if [[ $JOB_TYPE =~ $pr_regex ]]; then
        echo "(gitlab_ci_trigger.sh) ==> PR testing"
        get_code
        run_pr
    fi

    periodic_regex='periodic.*'
    if [[ $JOB_TYPE =~ $periodic_regex ]]; then
        echo "(gitlab_ci_trigger.sh) ==> Periodic job testing"
        get_code
        run_periodic
    fi

    ci_cmd="./ci/launch_e2e.py ${test_params}"
    echo "(gitlab_ci_trigger.sh) ==> The GitLab CI trigger output is: ${ci_cmd}"

    if [ "$ci_mock_cmd" -eq "0" ]; then
        echo "(gitlab_ci_trigger.sh) ==> Run the deployment script"
        if [[ "${test_params}" == *pr* ]] && [[ "${test_params}" == *none* ]] ; then
            echo "(gitlab_ci_trigger.sh) ==> There is no open PRs with labels"
            exit 0
        fi
        ${ci_cmd}
    else
        echo "(gitlab_ci_trigger.sh) ==> Mock test"
        echo "(gitlab_ci_trigger.sh) ==> OUTPUT: ${ci_cmd}"
    fi
}

main
