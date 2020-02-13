<p style="text-align: center" align="center">
    <a href="https://www.pystol.org"><img src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/images/logo_readme.svg?sanitize=true" alt="The open source, self-hosted and cloud-native fault injection platform"/></a>
</p>

**The open source, self-hosted and cloud-native fault injection platform**

<p style="text-align: center" align="center">
    <a href="https://www.python.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-python.svg?sanitize=true"/> </a>
    <a href="https://www.ansible.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-ansible.svg?sanitize=true"/> </a>
    <a href="https://www.pystol.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-love.svg?sanitize=true"/> </a>
    <a href="https://www.pystol.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/cloud-native.svg?sanitize=true"/> </a>
</p>

| [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/pystol.svg?sanitize=true)](https://github.com/pystol/pystol) | [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/pystol-galaxy.svg?sanitize=true)](https://github.com/pystol/pystol-galaxy) | [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/pystol-ansible.svg?sanitize=true)](https://github.com/pystol/pystol-ansible) | [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/pystol-docs.svg?sanitize=true)](https://github.com/pystol/pystol-docs) | [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/quay.io.svg?sanitize=true)](https://quay.io/organization/pystol) | [![](https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/information.svg?sanitize=true)](https://docs.pystol.org) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| [![Container image build](https://github.com/pystol/pystol/workflows/container-image/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=container-image) | [![Galaxy publish](https://github.com/pystol/pystol-galaxy/workflows/galaxy-publish/badge.svg?event=push)](https://github.com/pystol/pystol-galaxy/actions?workflow=galaxy-publish) | [![Linters](https://github.com/pystol/pystol-ansible/workflows/linters/badge.svg?event=push)](https://github.com/pystol/pystol-ansible/actions?workflow=linters) | [![Docs build](https://github.com/pystol/pystol-docs/workflows/build/badge.svg?event=push)](https://github.com/pystol/pystol-docs/actions?workflow=build) | [![Docker registry STAGING status](https://quay.io/repository/pystol/pystol-operator-staging/status)](https://quay.io/repository/pystol/pystol-operator-staging) | [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) |
| [![NodeJS](https://github.com/pystol/pystol/workflows/nodeunits/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=nodeunits) | [![linters](https://github.com/pystol/pystol-galaxy/workflows/linters/badge.svg?event=push)](https://github.com/pystol/pystol-galaxy/actions?workflow=linters) | | | [![Docker registry STABLE status](https://quay.io/repository/pystol/pystol-operator-stable/status)](https://quay.io/repository/pystol/pystol-operator-stable) | [![google groups](https://img.shields.io/badge/Groups-groups.pystol.org-blue.svg)](https://groups.pystol.org) |
| [![Linters](https://github.com/pystol/pystol/workflows/linters/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=linters) | | | | | [![IRC channel](https://img.shields.io/badge/Freenode-%23pystol-blue.svg)](http://webchat.freenode.net/?channels=%23pystol) |
| [![pyunits](https://github.com/pystol/pystol/workflows/pyunits/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=pyunits) | | | | | |
| [![E2E install](https://github.com/pystol/pystol/workflows/e2einstall/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=e2einstall) | | | | | |
| [![Pypi publish](https://github.com/pystol/pystol/workflows/pypipublish/badge.svg?event=push)](https://github.com/pystol/pystol/actions?workflow=pypipublish) | | | | | |

## Running Pystol

The easiest way to execute Pystol in a Kubernetes-based cluster is:

```
pip install pystol # Install the operator using a pypi package
pystol -b # Print the Pystol banner
pystol -v # Print the installed version
pystol deploy # Install Pystol in the cluster
# Run the pingtest action.
pystol run --namespace pystol \
           --collection actions \
           --role pingtest
pystol --help # Run the help for further information
```

## Documentation

Please refer to the [official documentation](https://docs.pystol.org)
website for any information related to the project.

## CI dashboard

Pystol uses **GitHub actions**
and **badges** to run all the CI
tasks, the result of running these
tasks is represented using badges.

In particular we embrace the use of
CI dashboard as information radiators.

We created the [badgeboad project](https://badgeboard.pystol.org)
to show the value of any set of badges as a dashboard.

For more information you can open the
[CI dashboard](https://badgeboard.pystol.org)
directly or go to the
[project page in GitHub](https://github.com/pystol/badgeboard).

## Container images

All pystol official container images are hosted in Quay.io under
the [Pystol organization](https://quay.io/organization/pystol).

There you will find two repositories:

* The Pystol [staging repository](https://quay.io/repository/pystol/pystol-operator-staging).
Here you will find all the container images from the upstream end-to-end jobs from the GitHub
Actions jobs.

* The Pystol [stable repository](https://quay.io/repository/pystol/pystol-operator-stable).
Here you will find all the container images from the stable branches.

## License

Pystol is open source software
licensed under the [Apache license](LICENSE).
