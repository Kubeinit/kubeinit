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

# NOTE:
# If there is the need of adding more container images
# to quay.io/kubeinit, then:
# - Make sure the repository is already created
#   and the visibility is public, for example that
#   https://quay.io/repository/kubeinit/haproxy exists.
# - Make sure the bot (kubeinit+sync) have write access
#   to that repository.

if [ -z "$QUAY_BOT_USER" ]; then
    echo "QUAY_BOT_USER is not set";
    exit 1;
fi

if [ -z "$QUAY_BOT_KEY" ]; then
    echo "QUAY_BOT_KEY is not set";
    exit 1;
fi

user=$QUAY_BOT_USER
token=$QUAY_BOT_KEY

skopeo login quay.io -u$user -p$token

# Add here all the images to be syncronized to the main
# quay organization in Kubeinit
declare -a container_images=(
    "library haproxy 2.3"
    "library registry 2"
    "library httpd 2.4"
    "library debian 11"
    "library debian 12"
    "library ubuntu jammy"
    "library ubuntu noble"
    "internetsystemsconsortium bind9 9.18"
    "nginxinc nginx-unprivileged latest"
)

retry() {
    local -r -i max_attempts="$1"; shift
    local -r cmd="$@"
    local -i attempt_num=1
    until $cmd; do
        if ((attempt_num==max_attempts)); then
            echo "Attempt $attempt_num failed and there are no more attempts left!"
            return 1
        else
            echo "Attempt $attempt_num failed! Trying again in $attempt_num seconds..."
            sleep $((attempt_num++))
        fi
    done
}

for image in "${container_images[@]}"; do
    read -a strarr <<< "$image"
    namespace=${strarr[0]}
    container=${strarr[1]}
    tag=${strarr[2]}
    exists=$(curl -H "Authorization: Bearer XYZ" -X GET "https://quay.io/api/v1/repository/kubeinit/$container/tag/" | jq .tags[].name | grep \"$tag\" | uniq)

    if [ -n "$exists" ]; then
        quay_hash=$(skopeo inspect --raw docker://quay.io/kubeinit/$container:$tag | jq -r '.config.digest')
        docker_hash=$(skopeo inspect --raw docker://docker.io/$namespace/$container:$tag | jq -r '.config.digest')

        if [ "$quay_hash" == "$docker_hash" ]; then
            echo "The image hashes for tag $tag in kubeinit/$container and docker.io/$namespace/$container match. No update needed."
            continue
        else
            echo "The image hashes for tag $tag in kubeinit/$container and docker.io/$namespace/$container do not match. Updating the image."
        fi
    else
        echo "The tag $tag in kubeinit/$container is not found. Copying the container image."
    fi

    copy="skopeo copy docker://docker.io/$namespace/$container:$tag docker://quay.io/kubeinit/$container:$tag"
    retry 5 $copy

done
