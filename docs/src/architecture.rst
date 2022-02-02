============
Architecture
============

This section provides an overall
view of the project's architectural design
and components.

Kubeinit design
~~~~~~~~~~~~~~~

The following diagram describes the current main architectural design of a
Kubeinit deployment.

    .. image:: static/mingrammer/arch.png
      :width: 100%
      :alt: Kubeinit's architectural high level description

High-level development goals
----------------------------

Challenges of the problem domain
--------------------------------

Basic Ansible workflow design
-----------------------------

Infrastructure services (Services pod)
--------------------------------------

Each cluster deployment requires a set of infrastructure
services to support its correct functioning, the current
list of services deployed and configured are
Httpd,
Bind,
HAproxy,
Dnsmasq,
Nexus,
Local container registry.

This pod will be deployed by default in the first hypervisor but
depending on the user's requirements this pod might be scheduled
in any other chassis connected to the cluster.
