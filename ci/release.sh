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

if [ -z "$GITHUB_TOKEN" ]; then
    echo "GITHUB_TOKEN is not set";
    exit 1;
fi

if [ -z "$QUAY_USER" ]; then
    echo "QUAY_USER is not set";
    exit 1;
fi

if [ -z "$QUAY_KEY" ]; then
    echo "QUAY_KEY is not set";
    exit 1;
fi

if [ -z "$GALAXY_KEY" ]; then
    echo "GALAXY_KEY is not set";
    exit 1;
fi

#
# Initial variables
#

namespace=kubeinit
name=kubeinit
all_published_versions=$(curl https://galaxy.ansible.com/api/v2/collections/$namespace/$name/versions/ | jq -r '.results' | jq -c '.[].version')
current_galaxy_version=$(cat kubeinit/galaxy.yml | shyaml get-value version)
current_galaxy_namespace=$(cat kubeinit/galaxy.yml | shyaml get-value namespace)
current_galaxy_name=$(cat kubeinit/galaxy.yml | shyaml get-value name)
publish="1"

# Specific for GH releases
branch=$(git rev-parse --abbrev-ref HEAD)

#
# Post data method for GH release
#

generate_post_data()
{
timestamp=$(date +"%Y-%m-%d-%H-%M-%S")
permadate=$(date +"%Y-%m-%d")
dashed_version="${current_galaxy_version//./-}"

  cat <<EOF
{
  "tag_name": "$current_galaxy_version",
  "target_commitish": "$branch",
  "name": "$current_galaxy_version.kubeinit-$timestamp",
  "body": "Release changelog at: https://docs.kubeinit.org/changelog.html#v$dashed_version-release-date-$permadate",
  "draft": false,
  "prerelease": false
}
EOF
}

#
# Check all the current published versions and if the
# packaged to be created has a different version, then
# we publish it to Galaxy Ansible
#

for ver in $all_published_versions; do
    echo "--"
    echo "Published: "$ver
    echo "Built: "$current_galaxy_version
    echo ""
    if [[ $ver == \"$current_galaxy_version\" ]]; then
        echo "The current version $current_galaxy_version is already published"
        echo "Proceed to update the galaxy.yml file with a newer version"
        echo "After the version change, when the commit is merged, then the package"
        echo "will be published automatically."
        publish="0"
    fi
done

if [ "$publish" == "1" ]; then
    echo 'This version is not published, publishing!...'

    echo 'Building and pushing the container image to quay...'
    docker login -u="$QUAY_USER" -p="$QUAY_KEY" quay.io
    docker build . --file Dockerfile --tag quay.io/kubeinit/kubeinit:$current_galaxy_version
    docker push quay.io/kubeinit/kubeinit:$current_galaxy_version

    echo 'Building and pushing the Ansible collection to Ansible Galaxy...'
    cd ./kubeinit/
    mkdir -p releases
    ansible-galaxy collection build -v --force --output-path releases/
    ansible-galaxy collection publish \
        releases/$current_galaxy_namespace-$current_galaxy_name-$current_galaxy_version.tar.gz \
        --server https://beta-galaxy.ansible.com \
        --ignore-certs \
        --verbose \
        --api-key $GALAXY_KEY

    echo 'Building and pushing a new tag GitHub...'
    curl -H "Authorization: token $GITHUB_TOKEN" --data "$(generate_post_data)" "https://api.github.com/repos/kubeinit/kubeinit/releases"
fi
