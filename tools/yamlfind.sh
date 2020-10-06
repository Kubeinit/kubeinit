#!/bin/bash

count=`find . -not -wholename "*/node_modules/*" -and -not -wholename "*.tox/*" -and -name "*.yaml" | wc -l`
if [ "$count" != "0" ]; then
    echo "yaml extension not allowed"
    exit 1
else
    echo "no yaml found"
fi


# Match both docs and modules/roles

roles_docs_number=`ls docs/src/roles | wc -l`
roles_readmes_number=`find kubeinit/roles/ -name README.md | wc -l`
roles_number=`ls kubeinit/roles/ | wc -l`

modules_docs_number=`ls docs/src/modules | wc -l`
modules_number=`ls kubeinit/plugins/modules/ | wc -l`

echo "Roles in docs: $roles_docs_number"
echo "Roles: $roles_number"
echo "Roles READMEs: $roles_readmes_number"

echo "Modules in docs: $modules_docs_number"
echo "Modules: $modules_number"

if [ "$roles_readmes_number" -ne "$roles_number" ];then
    echo "The README.md file in each role do not";
    echo "match with the number of existing roles";
    exit 1;
fi

if [ "$roles_docs_number" -ne "$roles_number" ];then
    echo "Links in the roles docs section";
    echo "do not match with the number of existing roles";
    exit 1;
fi

if [ "$modules_docs_number" -ne "$modules_number" ];then
    echo "Links in the modules docs section";
    echo "do not match with the number of existing modules";
    exit 1;
fi
