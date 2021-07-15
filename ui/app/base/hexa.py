#!/usr/bin/env python

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

from app.base.allocated import compute_node_resources

# from flask import redirect, render_template, request, url_for, session

import kubernetes

from pystol.operator import load_kubernetes_config


def hexagons_data(api_client=None):
    """
    Get the hexagons data for the index.

    This method fetch the data for the index
    """
    hexa_data = []

    load_kubernetes_config()

    core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)
    try:
        nodes_list = core_v1.list_node().items
    except Exception:
        print("Error listing nodes")
        nodes_list = []

    for node in nodes_list:
        node_name = node.metadata.name
        node_labels = node.metadata.labels
        if "node-role.kubernetes.io/master" in node_labels:
            if node_labels['node-role.kubernetes.io/master'] == 'true':
                node_role = "Master"
            else:
                node_role = "Non master"
        else:
            node_role = "Non master"

        allocatable = node.status.allocatable
        node_info = node.status.node_info

        hdata = {}
        hdata['name'] = node_name
        hdata['role'] = node_role
        hdata['cpu'] = allocatable["cpu"]
        if 'ephemeral-storage' in allocatable:
            hdata['ephstorage'] = allocatable["ephemeral-storage"]
        else:
            hdata['ephstorage'] = 0
        hdata['mem'] = allocatable["memory"]
        hdata['maxpods'] = allocatable["pods"]

        hdata['arch'] = node_info.architecture
        hdata['crver'] = node_info.container_runtime_version
        hdata['kernelver'] = node_info.kernel_version
        hdata['kubeproxyver'] = node_info.kube_proxy_version
        hdata['kubeletver'] = node_info.kubelet_version
        hdata['os'] = node_info.operating_system

        state_info = compute_node_resources(
            node_name=node_name, api_client=api_client)
        hdata['state_info'] = state_info
        max_pods = int(int(allocatable["pods"]) * 1.5)
        field_selector = ("spec.nodeName=" + node_name)
        pods = core_v1.list_pod_for_all_namespaces(limit=max_pods,
                                                   field_selector=field_selector).items
        hdata['pods'] = []
        for pod in pods:
            hdata['pods'].append({'name': pod.metadata.name,
                                  'namespace': pod.metadata.namespace,
                                  'host_ip': pod.status.host_ip,
                                  'pod_ip': pod.status.pod_ip,
                                  'phase': pod.status.phase})
        hexa_data.append(hdata)
    return hexa_data
