============
Contributing
============

Communication
~~~~~~~~~~~~~
* Join the `kubeinit Slack channel <https://kubernetes.slack.com/archives/C01FKK19T0B>`__.

Creating new roles automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding roles into this project is easy and starts with a compatible skeleton.

We will use the same role generation script from tripleo-ansible
to automatically create new roles based in a pre-defined skeleton.

From the repository root directory execute:

.. code-block:: console

    ansible-playbook \
        -i 'localhost,' \
        role-addition.yml \
        -e ansible_connection=local \
        -e role_name=kubeinit-example

.. note::  Please use only *kubeinit-rolename* words for defining the role name, for example, replace **kubeinit-example** with **kubeinit-bind**, **kubeinit-kubevirt**, or whatever the service name will be.

This command will generate the role, initial molecule default tests, and the documentation stub.

Linting new roles and code
~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to run a lint check automatically before pushing
code or pull requests.

From the repository root directory execute:

.. code-block:: console

    tox -e linters

If the test pass all the executed tests should have succeeded.

Linting commits
~~~~~~~~~~~~~~~

For every pull request is executed a syntax check, this is
for multiple reasons.

- Automatic generating of the changelog.
- Simple navigation through git history (e.g. ignoring style changes).

Format
------

.. code-block:: console

    <feat>: <add an awesome feature>
    ^----^  ^----------------------^
    |       |
    |       +-> Summary in present tense.
    |
    +-------> Type: chore, docs, feat, fix, refactor, style, test, build, ci, perf, and revert (always lowercase).

    <body> ----> The commit's body.

    <footer> ----> An optional footer.

Accepted types:

- `feat`: new feature for the user, not a new feature for build script
- `fix`: bug fix for the user, not a fix to a build script
- `docs`: changes to the documentation
- `style`: formatting, missing semi colons, etc; no production code change
- `refactor`: refactoring production code, eg. renaming a variable
- `test`: adding missing tests, refactoring tests; no production code change
- `chore`: updating grunt tasks etc; no production code change
- `build`: a change to the build process
- `ci`: changes to CI configuration files and scripts
- `perf`: a code change that improves performance
- `revert`: reverting a change

Message subject (first line)
----------------------------

The first line cannot be longer than 70 characters, the second line is always
blank and other lines should be wrapped at 80 characters. The type and scope
should always be lowercase as shown below.

Message body
------------

Uses the imperative, present tense: “change” not “changed” nor “changes” and
includes motivation for the change and contrasts with previous behavior.

Footer
------

An optional, last line separated by a blank line with keywords like:

.. code-block:: console

    ...

    Close #123

or

.. code-block:: console

    ...

    Fixes #123


Examples
--------

OK:

.. code-block:: console

    feat: include a new role

    This feature adds a new role to implement
    an awesome new feature.

WRONG:

.. code-block:: console

    Feat: Include a new role

    This feature adds a new role to implement
    an awesome new feature.
