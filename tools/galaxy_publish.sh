#!/bin/bash

PARAMS=""
while (( "$#" )); do
    case "$1" in
        -k|--galaxy-key)
            KARG=$2
            shift 2
            ;;
        --) # end argument parsing
            shift
            break
            ;;
        -*|--*=) # unsupported flags
            echo "Error: Unsupported flag $1" >&2
            echo "Please use ./publish.sh [-k <galaxy key> | --galaxy-key <galaxy key>]" >&2
            exit 1
            ;;
        *) # preserve positional arguments
            PARAMS="$PARAMS $1"
            shift
            ;;
    esac
done

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
token=$(git config --global github.token)

#
# Post data method for GH release
#

generate_post_data()
{
timestamp=$(date +"%Y-%m-%d-%M-%S")
  cat <<EOF
{
  "tag_name": "$current_galaxy_version",
  "target_commitish": "$branch",
  "name": "$current_galaxy_version.kubeinit-$timestamp",
  "body": "Release changelog at: https://docs.kubeinit.com/changelog.html#$current_galaxy_version",
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

    cd ./kubeinit/
    mkdir -p releases
    ansible-galaxy collection build -v --force --output-path releases/
    ansible-galaxy collection publish \
        releases/$current_galaxy_namespace-$current_galaxy_name-$current_galaxy_version.tar.gz --api-key $KARG

    curl --data "$(generate_post_data)" "https://api.github.com/repos/kubeinit/kubeinit/releases?access_token=$GITHUB_TOKEN"
fi
