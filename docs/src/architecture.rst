============
Architecture
============

This section provides an overall
view of the project's architectural design
and components.

Services pod
~~~~~~~~~~~~

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
