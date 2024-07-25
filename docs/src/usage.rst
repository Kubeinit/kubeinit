=====
Usage
=====

KubeInit is an Ansible collection, to use it
the only installation requirement is to have Python 3
and Ansible +2.9.

There are two ways of launching KubeInit, directly using the
ansible-playbook command from the project's source code,
or by running it inside a container.

Requirements
~~~~~~~~~~~~

* A fresh deployed server with enough RAM and disk space (120GB in RAM and 300GB in disk) and CentOS 8 (it should work also in Fedora/Debian/Ubuntu hosts).
* We assume that the hypervisor node is called nyctea (defined in the inventory).
* Have root passwordless access with certificates.
* Adjust the inventory file to suit your needs.
* Having podman installed in the machine where you are running ansible-playbook.

Installing dependencies
-----------------------

KubeInit calls additional Ansible collections that needs to be installed.
If there are dependencies issues when executing the collection, install
them by executing:

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    ansible-galaxy collection install --force --requirements-file kubeinit/requirements.yml

An example of a possible dependency issue is the following:

.. code-block:: console

    TASK [Configure the cluster service node] ***************************************************************************************************************
    ERROR! couldn't resolve module/action 'community.general.docker_login'. This often indicates a misspelling, missing collection, or incorrect module path.

By default the KubeInit's container image installs these requirements, this should only affect
those executing directly the collection from the source code.

There is also needed to build and install the collection if its used directly from the
repository.

.. code-block:: console

    # From the root directory in the repository, execute:
    rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
    ansible-galaxy collection build kubeinit --verbose --force --output-path releases/
    ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat kubeinit/galaxy.yml | shyaml get-value version`.tar.gz

Multiple hypervisors support
----------------------------

Currently, it is supported the deployment of multiple Kubernetes clusters
in multiple hosts. While it is supported to deploy different Kubernetes distributions
based in different guest OS, for example Vanilla Kubernetes that is based in CentOS and
OKD based in Fedora CoreOS the operative system of the hosts must be the same, this means
to have 3 hypervisors (chassis) based in Debian that will host any of the currently supported
distribution.

**Any deployment based on mixed versions of the Hypervisors OS is not supported.**
This is motivated on the potential failures due to mismatch in OVS/OVN and Kernel
versions.

Kubeinit spec
-------------

Currently the inventory to deploy the clusters is dynamic,
this means that it is configured based on the variables that are
passed to the deployment command.
The first hypervisor is denoted also as the bastion host or |Dagger|.

In particular the `kubeinit_spec` variable will determine the
amount of controller nodes, compute nodes, and hypervisors that
will be used.

The current supported syntax of this variable is:

`<distro>-<driver>-<controllers>-<computes>-<hypervisors>`

For example, combinations like okd-libvirt-1-2-1, k8s-libvirt-3-1-1,
are all valid.


Deployment
~~~~~~~~~~

Group variables
---------------

All
^^^
Default variables related to Ansible parameters, common
across all the supported scenarios.

.. autoyaml:: kubeinit/group_vars/all.yml

Cluster
^^^^^^^
Initial configuration variables related to the cluster parameters.

.. autoyaml:: kubeinit/group_vars/kubeinit_cluster.yml

Defaults
^^^^^^^^
Default variables related to general cluster parameters.

.. autoyaml:: kubeinit/group_vars/kubeinit_defaults.yml

Environment
^^^^^^^^^^^
The following environment specific variables can be used
with the deployment command.
These variables might be specific to each scenario.

.. autoyaml:: kubeinit/group_vars/kubeinit_env.yml

Network
^^^^^^^
General deployment network parameters.

.. autoyaml:: kubeinit/group_vars/kubeinit_network.yml

Secrets
^^^^^^^

The common secrets supported across all the scenarios
are handled using the following variables.

.. autoyaml:: kubeinit/group_vars/kubeinit_secrets.yml

Inventory
---------

The following einventory structure must be followed.

.. autoyaml:: kubeinit/inventory.yml

Directly executing the deployment playbook
------------------------------------------

The following example command will deploy a multi-master OKD 4.5 cluster with 1 worker node
in a single command and in approximately 30 minutes.

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    ansible-playbook \
        -v --user root \
        -e kubeinit_spec=okd-libvirt-3-2-1 \
        -i ./kubeinit/inventory.yml \
        ./kubeinit/playbook.yml

After provisioning any of the scenarios, you should have your environment ready to go.
To connect to the nodes from the hypervisor use the IP addresses from the inventory files.



Running the deployment command from a container
-----------------------------------------------

The whole process is explained in the `HowTo's <https://www.anstack.com/blog/2020/09/11/Deploying-KubeInit-from-a-container.html>`_.
The following commands build a container image with the project inside of it, and then
launches the container executing the ansible-playbook command with all the
standard ansible-playbook parameters.

Note: When running the deployment from a container,
`nyctea` can not be 127.0.0.1, it needs to be
the hypervisor's IP address. Also when running the
deployment as a user different than root, the
keys needs to be also updated.

Running from the GIT repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    podman build -t kubeinit/kubeinit .
    podman run --rm -it \
        -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
        -v ~/.ssh/id_rsa.pub:/root/.ssh/id_rsa.pub:z \
        -v ~/.ssh/config:/root/.ssh/config:z \
        kubeinit/kubeinit \
            -v --user root \
            -e kubeinit_spec=okd-libvirt-3-2-1 \
            -i ./kubeinit/inventory.yml \
            ./kubeinit/playbook.yml

Running from a release
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    # Get the latest release tag
    TAG=$(curl --silent "https://api.github.com/repos/kubeinit/kubeinit/releases/latest" | jq -r .tag_name)
    podman run --rm -it \
        -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
        -v ~/.ssh/id_rsa.pub:/root/.ssh/id_rsa.pub:z \
        -v ~/.ssh/config:/root/.ssh/config:z \
        quay.io/kubeinit/kubeinit:$TAG \
            -v --user root \
            -e kubeinit_spec=okd-libvirt-3-2-1 \
            -i ./kubeinit/inventory.yml \
            ./kubeinit/playbook.yml

Connecting to the cluster
-------------------------

Accessing the cluster resources internally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the deployment is finished the machine used
for provisioning the cluster have access to both
the pod services and instances created.
The SSH keys are stored in the .ssh folder from the
home folder of the user triggering the deployment.
For instance:

.. code-block:: console

    # From the hypervisor node the user should
    # have passwordless access to the services pod
    root@mocoloco kubeinit]# ssh -i ~/.ssh/rkecluster_id_rsa root@10.0.0.253
    Welcome to Ubuntu 20.10 (GNU/Linux 5.8.0-53-generic x86_64)
      System load:  0.0                Users logged in:               0
      Usage of /:   2.5% of 147.34GB   IPv4 address for docker0:      172.17.0.1
      Memory usage: 4%                 IPv4 address for enp1s0:       10.0.0.253
      Swap usage:   0%                 IPv4 address for vetha0e3a877: 172.16.16.1
      Processes:    186

    # Get the cluster nodes
    root@rke-service-01:~# kubectl get nodes
    NAME            STATUS   ROLES               AGE   VERSION
    rke-controller-01   Ready    controlplane,etcd   11m   v1.19.3

    # In the root folder there are files with some details about the deployment
    # like the kubeconfig file, the container images used in the deployment,
    # and the registry pull secret.
    root@rke-service-01:~# ls
    cluster.rkestate  httpd.conf               kubeinit_deployment_images.txt  pullsecret.json      rke           snap
    cluster.yml       kube_config_cluster.yml  pod_cidr                        registry-auths.json  service_cidr

    # The cluster config file is also copied to the default folder.
    root@rke-service-01:~# ls .kube/config
    .kube/config


Accessing the cluster resources externally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the services deployment is executed
one of the tasks in the kubeinit_bind role
will create an external ingress script on the primary
(bastion) hypervisor called create-external-ingress.sh.

Running that script will create the required tunnels
for all the service endpoints on the cluster.

A user should be able to fetch the kubeadmin password running a command like:

.. code-block:: console

    echo $(ssh root@nyctea ssh root@10.0.0.100 cat install_dir/auth/kubeadmin-password)

The console should be available at
https://console-openshift-console.apps.okdcluster.kubeinit.local
from the external machine if you have a similar configuration in the
`/etc/resolv.conf`.

.. code-block:: console

    search okdcluster.kubeinit.local
    nameserver <ip of nyctea>
    nameserver 8.8.8.8

Cleaning up the environment
---------------------------

Each time a cluster is deployed, all the previously created resources are removed.
In case a user needs to remove the resources created by Kubeinit execute
from the project's root folder:

.. code-block:: console

    ansible-playbook \
        -v --user root \
        -e kubeinit_spec=okd-libvirt-3-2-1 \
        -e kubeinit_stop_after_task=task-cleanup-hypervisors \
        -i ./kubeinit/inventory.yml \
        ./kubeinit/playbook.yml

In this case the deployment will stop just after cleaning the
hypervisors resources. If its required to remove all the guests
in the hypervisors its also possible to add the following variable
`-e kubeinit_libvirt_destroy_all_guests=True`

.. We define some macros to add symbols when required to the
   docs pages, this is fetched from Docutils
   https://docutils.sourceforge.io/docutils/parsers/rst/include/

.. include:: static/parsers/xhtml1-lat1.txt
.. include:: static/parsers/xhtml1-special.txt
.. include:: static/parsers/xhtml1-symbol.txt
