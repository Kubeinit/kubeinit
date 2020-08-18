=====
Usage
=====

Once kubeInit has been installed navigate to the
project's root directory and run Ansible.

Here are described the currently supported scenarios.

.. note::  All the commands must be executed from the project's root directory.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OKD 4.5 multi-master cluster with 1-10 worker nodes and KubeVirt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    ansible-playbook \
        -vvv \
        --user root \
        -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        ./playbooks/okd.yml

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OKD 4.5 multi-master cluster with 1-10 worker nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the tags are added by default so if KubeVirt is not required
execute:

.. code-block:: console

    ansible-playbook \
        -vvv \
        --user root \
        -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        --tags=provision_libvirt \
        ./playbooks/okd.yml
