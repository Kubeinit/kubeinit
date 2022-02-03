#!/bin/python3

"""
Copyright kubeinit contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import os

from diagrams import Cluster, Diagram
from diagrams.custom import Custom
from diagrams.generic.os import Centos
from diagrams.generic.os import Ubuntu
from diagrams.k8s.ecosystem import Kustomize
from diagrams.k8s.infra import Node
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Crio
from diagrams.onprem.iac import Ansible

filename = os.path.splitext(os.path.basename(__file__))[0]
title = "Kubeinit's high level components"
direction = 'LR'
graph_attr = {
    "pad": "0"
}

with Diagram(title, filename=filename, graph_attr=graph_attr, outformat='png', direction=direction, show=False):
    controller = Client("Controller")
    bare_metal_machines = Server("Server(s)")

    with Cluster("Baremetal node(s)"):
        ansible = Ansible("Ansible")
        kubeinit = Custom("Kubeinit", "./resources/kubeinit.png")
        libvirt = Custom("Libvirt", "./resources/libvirt.png")

        with Cluster("Distros") as distros:
            os1 = Centos()
            Ubuntu()

        with Cluster("Bastion services", direction='LR'):
            dnsmasq = Crio("dnsmasq", width='0.5')
            Crio("HAproxy", width='0.5', pin="true", pos="1,0")
            Crio("Nginx", width='0.5', pin="true", pos="2,0")
            Crio("Registry", width='0.5')
            Crio("Apache", width='0.5')
            Crio("Bind", width='0.5')

        controller >> ansible
        ansible >> kubeinit
        kubeinit >> libvirt
        kubeinit >> dnsmasq
        libvirt >> os1
        os1 >> bare_metal_machines

        with Cluster("Cluster(s) guest(s)"):
            ansible2 = Ansible("Ansible")
            kubeinit2 = Custom("Kubeinit", "./resources/kubeinit.png")
            kubernetes_nodes = Node("Kuberentes node(s)")

            controller >> ansible2
            ansible2 >> kubeinit2
            kubeinit2 >> kubernetes_nodes

            with Cluster("Cluster applications"):
                kustomize = Kustomize("Kustomize")
                kubeinit2 >> kustomize
