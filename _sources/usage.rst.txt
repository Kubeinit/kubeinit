=====
Usage
=====

Once kubeinit has been installed navigate to the share path,
usually `/usr/share/ansible` path to access the installed roles, playbooks, and
libraries.

---------
Scenarios
---------

Here are described the currently supported scenarios.

.. note::  All the commands must be executed from the project's root directory.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OKD 4.5 multi-master cluster with 1-10 worker nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    ansible-playbook \
        -vvv \
        --user root \
        -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        ./playbooks/okd.yml

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OKD 4.5 multi-master cluster with 1-10 worker nodes + KubeVirt support (WIP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    ansible-playbook \
        -vvv \
        --user root \
        -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        --tags=kubeinit_kubevirt,provision_libvirt \
        ./playbooks/okd.yml
