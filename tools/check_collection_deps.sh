#!/bin/bash
set -o pipefail
set -e

read-0() {
    while [ "$1" ]; do
        IFS=$'\0' read -r -d '' "$1" || return 1
        shift
    done
} &&
cat kubeinit/galaxy.yml | shyaml key-values-0 dependencies |
while read-0 key value; do
    fval=$(echo "${value}" | tr -d '=')
    sval=$(cat kubeinit/requirements.yml | shyaml get-value collections | grep -A1 ${key} | grep -v ${key} | cut -d ':' -f 2 | tr -d ' ')
    if [ "$fval" = "$sval" ]; then
        echo "Versions for ${key} are the same in requirements.yml and galaxy.yml"
    else
        echo "For the ${key} dependency there is a mismatch in"
        echo "/kubeinit/kubeinit/requirements.yml and /kubeinit/kubeinit/galaxy.yml"
        echo "Both versions should be the same"
        exit 1
    fi
done
