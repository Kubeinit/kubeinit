============
Architecture
============

This section provides an overall
view of the project's architectural design
and components.

Kubeinit design
~~~~~~~~~~~~~~~

High-level development goals
----------------------------

Challenges of the problem domain
--------------------------------

High level architecture
-----------------------

The following diagram how functional components
are deployed.

    .. image:: static/svg/00_architecture.png
      :width: 100%
      :alt: Kubeinit's high level architecture.

The following diagram how functional components
are deployed.

    .. image:: static/svg/01_architecture.png
      :width: 100%
      :alt: Kubeinit's high level architecture.

The following diagram how HAproxy routes traffic.

    .. image:: static/svg/00_net.png
      :width: 100%
      :alt: Kubeinit's haproxy traffic.

The following diagram how the network is configured.

    .. image:: static/svg/01_net.png
      :width: 100%
      :alt: Kubeinit's net configuration.

The following diagram how the OVN network is configured.

    .. image:: static/svg/00_ovn.png
      :width: 100%
      :alt: Kubeinit's OVN configuration.

Basic components overview
-------------------------

The following diagram describes the main high level components involved in a
Kubeinit deployment triggered by Ansible.

    .. image:: static/mingrammer/components.png
      :width: 100%
      :alt: Kubeinit's high level components.

- Controller: Add here a description.
- Bastion host: Add here a description.
- Services pod: Add here a description.
- Baremetal nodes: Add here a description.
- Cluster guests: Add here a description.
- Cluster applications: Add here a description.

Baremetal nodes and cluster guests allocation
---------------------------------------------

The following diagram describes a
potential distribution of hosts, guests, and
services containers.

    .. image:: static/mingrammer/nodes_architecture.png
      :width: 100%
      :alt: Kubeinit's architectural high level description

Each cluster deployment requires a set of infrastructure
services to support its correct functioning, the current
list of services deployed and configured are
Httpd,
Bind,
HAproxy,
Dnsmasq,
Nexus, and a
Local container registry.

This pod (services pod) will be deployed by default in the first hypervisor but
depending on the user's requirements this pod might be scheduled
in any other chassis connected to the cluster.

Services pod architecture
--------------------------

The following diagram describes
the reasoning for the infrastructure services
to support the multiple clusters that can be deployed

    .. image:: static/mingrammer/containers_architecture.png
      :width: 100%
      :alt: Kubeinit's architectural high level description

Underlying OVN networking layer
-------------------------------

The following diagram describes
the networking infrastructure to
give networking services to the cluster or
multiple clusters deployed.

    .. image:: static/mingrammer/ovn_network.png
      :width: 100%
      :alt: Kubeinit's architectural high level description

Ansible deployment sequence diagram
-----------------------------------

The following diagram describes the internal sequence diagram
of a Kubeinit deployment.

    .. image:: static/plantuml/ansible_deployment_sequence_diagram.png
      :width: 100%
      :alt: Sequence diagram of an Ansible deployment
