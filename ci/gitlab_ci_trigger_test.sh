#!/bin/bash

#
# Avoid setting `set -e` in this script,
# if it fails inmediatelly the output wont
# be displayed in the GH job output
#

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

output_file='./trigger_results.txt'

#
# (( periodic simple test ))
# This should return a
echo "(gitlab_ci_trigger_test.sh) ==> Run periodic job"
TEST_RESULT=$(JOB_TYPE='periodic' ci_mock_cmd=1 ./ci/gitlab_ci_trigger.sh 2>&1)
TEST_RESULT_REGEX='OUTPUT: ./ci/launch_e2e.py periodic.*'
if [[ $TEST_RESULT =~ $TEST_RESULT_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> Periodic job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" > $output_file
else
    echo "(gitlab_ci_trigger_test.sh) ==> FAIL: $TEST_RESULT should match $TEST_RESULT_REGEX" > $output_file
fi

#
# (( periodic random ))
# This should return a
echo "(gitlab_ci_trigger_test.sh) ==> Run periodic=random job"
TEST_RESULT=$(JOB_TYPE='periodic=random' ci_mock_cmd=1 ./ci/gitlab_ci_trigger.sh 2>&1)
TEST_RESULT_REGEX='OUTPUT: ./ci/launch_e2e.py periodic=random'
if [[ $TEST_RESULT =~ $TEST_RESULT_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> Periodic job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" >> $output_file
else
    echo "(gitlab_ci_trigger_test.sh) ==> FAIL: $TEST_RESULT should match $TEST_RESULT_REGEX" >> $output_file
fi

#
# (( periodic all ))
# This should return a
echo "(gitlab_ci_trigger_test.sh) ==> Run periodic=all job"
TEST_RESULT=$(JOB_TYPE='periodic=all' ci_mock_cmd=1 ./ci/gitlab_ci_trigger.sh 2>&1)
TEST_RESULT_REGEX='OUTPUT: ./ci/launch_e2e.py periodic=all'
if [[ $TEST_RESULT =~ $TEST_RESULT_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> Periodic job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" >> $output_file
else
    echo "(gitlab_ci_trigger_test.sh) ==> FAIL: $TEST_RESULT should match $TEST_RESULT_REGEX" >> $output_file
fi

#
# (( periodic specific ))
# This should return a
echo "(gitlab_ci_trigger_test.sh) ==> Run periodic=k8s-libvirt-1-0-1-h job"
TEST_RESULT=$(JOB_TYPE='periodic=k8s-libvirt-1-0-1-h' ci_mock_cmd=1 ./ci/gitlab_ci_trigger.sh 2>&1)
TEST_RESULT_REGEX='OUTPUT: ./ci/launch_e2e.py periodic=k8s-libvirt-1-0-1-h'
if [[ $TEST_RESULT =~ $TEST_RESULT_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> Periodic job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" >> $output_file
else
    echo "(gitlab_ci_trigger_test.sh) ==> FAIL: $TEST_RESULT should match $TEST_RESULT_REGEX" >> $output_file
fi

#
# (( pr none or valid test ))
# This should return a
echo "(gitlab_ci_trigger_test.sh) ==> Run pr job"
TEST_RESULT=$(JOB_TYPE='pr' ci_mock_cmd=1 ./ci/gitlab_ci_trigger.sh 2>&1)
TEST_RESULT_NONE_REGEX='OUTPUT: ./ci/launch_e2e.py pr_number=none'
TEST_RESULT_REGEX='OUTPUT: .\/ci\/launch_e2e\.py (verbosity=v+)|(pr_number=[0-9]+)|(job_label=[a-z]+-[a-z]+-[1|3]-[0-9]-[0-9]-h)'

if [[ $TEST_RESULT =~ $TEST_RESULT_NONE_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> PR job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" >> $output_file
elif [[ $TEST_RESULT =~ $TEST_RESULT_REGEX ]]; then
    echo "(gitlab_ci_trigger_test.sh) ==> PR job unit test passed"
    echo "(gitlab_ci_trigger_test.sh) ==> PASS: $TEST_RESULT" >> $output_file
else
    echo "(gitlab_ci_trigger_test.sh) ==> FAIL: $TEST_RESULT should match $TEST_RESULT_REGEX or $TEST_RESULT_NONE_REGEX" >> $output_file
fi

if [ -f "$output_file" ]; then
    ERRORS=$(cat $output_file | grep FAIL | wc -l)
    if [ $ERRORS -gt 0 ]; then
        echo "(gitlab_ci_trigger_test.sh) ==> There is a failure in the Gitlab CI trigger script"
        cat $output_file
        exit 1
    else
        echo "(gitlab_ci_trigger_test.sh) ==> All tests passed"
        cat $output_file
    fi

fi
