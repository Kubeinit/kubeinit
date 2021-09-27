=====
Usage
=====

There are two ways of launching KubeInit, directly using the
ansible-playbook command from the project's source code,
or by running it inside a container.

Requirements
~~~~~~~~~~~~

* A fresh deployed server with enough RAM and disk space (120GB in RAM and 300GB in disk) and CentOS 8 (it should work also in Fedora/Debian/Ubuntu hosts).
* We assume that the hypervisor node is called nyctea (defined in the inventory).
* Have root passwordless access with certificates.
* Adjust the inventory file to suit your needs i.e. `the worker nodes <https://github.com/Kubeinit/kubeinit/blob/master/kubeinit/hosts/okd/inventory#L66>`_ you will need in your cluster.
* Having podman installed in the machine where you are running ansible-playbook.

Installing dependencies
~~~~~~~~~~~~~~~~~~~~~~~

KubeInit calls additional Ansible collections that needs to be installed.
If there are dependencies issues when executing the collection, install
them by executing:

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    ansible-galaxy collection install --force -r kubeinit/requirements.yml

An example of a possible dependency issue is the following:

.. code-block:: console

    TASK [Configure the cluster service node] ***************************************************************************************************************
    ERROR! couldn't resolve module/action 'community.general.docker_login'. This often indicates a misspelling, missing collection, or incorrect module path.

By default the KubeInit's container image installs these requirements, this should only affect
those executing directly the collection from the source code.

Directly executing the deployment playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example command will deploy a multi-master OKD 4.5 cluster with 1 worker node
in a single command and in approximately 30 minutes.

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        ./playbooks/okd.yml

After provisioning any of the scenarios, you should have your environment ready to go.
To connect to the nodes from the hypervisor use the IP addresses from the inventory files.

Running the deployment command from a container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
-------------------------------

.. code-block:: console

    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    podman build -t kubeinit/kubeinit .
    run_as='root'
    podman run --rm -it \
        -v ~/.ssh/id_rsa:/${run_as}/.ssh/id_rsa:z \
        -v ~/.ssh/id_rsa.pub:/${run_as}/.ssh/id_rsa.pub:z \
        -v /etc/hosts:/etc/hosts \
        kubeinit/kubeinit \
            --user ${run_as} \
            -v -i ./hosts/okd/inventory \
            -e ansible_ssh_user=${run_as} \
            --become \
            --become-user ${run_as} \
            ./playbooks/okd.yml

Running from a release
----------------------

.. code-block:: console

    # Get the latest release tag
    TAG=$(curl --silent "https://api.github.com/repos/kubeinit/kubeinit/releases/latest" | jq -r .tag_name)
    podman run --rm -it \
        -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
        -v ~/.ssh/id_rsa.pub:/root/.ssh/id_rsa.pub:z \
        -v /etc/hosts:/etc/hosts \
        quay.io/kubeinit/kubeinit:$TAG \
            --user root \
            -v -i ./hosts/okd/inventory \
            --become \
            --become-user root \
            ./playbooks/okd.yml

Accessing the cluster resources
-------------------------------

Once the deployment is finished the service
node has access to the cluster resources.
For example, once logged in the service
machine a user can execute:

.. code-block:: console

    # From the hypervisor node the user should
    # have passwordless access to the service machine
    root@mocoloco kubeinit]# ssh root@10.0.0.100
    Welcome to Ubuntu 20.10 (GNU/Linux 5.8.0-53-generic x86_64)
      System load:  0.0                Users logged in:               0
      Usage of /:   2.5% of 147.34GB   IPv4 address for docker0:      172.17.0.1
      Memory usage: 4%                 IPv4 address for enp1s0:       10.0.0.100
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

Cleaning up the environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each time a cluster is deployed, all the previously created resources are removed.
In case a user needs to remove the resources created by Kubeinit execute
from the project's root folder:

.. code-block:: console

    # Create a playbook to run the cleanup tasks
    cat << EOF > ./playbooks/clean.yml
    ---
    - name: Clean
      hosts: hypervisor_hosts
      tasks:
        - name: Run the prepare tasks
          ansible.builtin.include_role:
            name: kubeinit.kubeinit.kubeinit_prepare
            tasks_from: main.yml
        - name: Clean the environment
          ansible.builtin.include_role:
            name: kubeinit.kubeinit.kubeinit_libvirt
            tasks_from: 10_cleanup
    EOF
    # Run the cleanup playbook
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        ./playbooks/clean.yml
    # Remove cleanup playbook
    rm -rf ./playbooks/clean.yml
