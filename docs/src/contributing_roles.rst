============
Contributing
============

Adding roles into this project is easy and starts with a compatible skeleton.


Creating new roles automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will use the same role generation script from tripleo-ansible
to automatically create new roles based in a pre-defined skeleton.

From the repository root directory execute:

.. code-block:: console

    ansible-playbook \
        -i 'localhost,' \
        role-addition.yml \
        -e ansible_connection=local \
        -e role_name=kubeinit-example

This command will generate the role, initial molecule default tests, and the documentation stub.
