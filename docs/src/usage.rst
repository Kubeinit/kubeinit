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

Directly executing the deployment playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example command will deploy a multi-master OKD 4.5 cluster with 1 worker node
in a single command and in approximately 30 minutes.

.. note::  All the commands must be executed from the project's root directory.

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

Running from the GIT repository
-------------------------------

.. code-block:: console
    git clone https://github.com/Kubeinit/kubeinit.git
    cd kubeinit
    podman build -t kubeinit/kubeinit .

    podman run --rm -it \
        -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
        -v /etc/hosts:/etc/hosts \
        kubeinit/kubeinit \
            --user root \
            -v -i ./hosts/okd/inventory \
            --become \
            --become-user root \
            ./playbooks/okd.yml

Running from a release
----------------------

.. code-block:: console
    TAG=0.6.1
    podman run --rm -it \
        -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
        -v /etc/hosts:/etc/hosts \
        quay.io/kubeinit/kubeinit:$TAG \
            --user root \
            -v -i ./hosts/okd/inventory \
            --become \
            --become-user root \
            ./playbooks/okd.yml
