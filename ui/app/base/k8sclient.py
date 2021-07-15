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


import subprocess
# from flask import redirect, render_template, request, url_for
from urllib.parse import urlparse

import kubernetes

from pystol.operator import load_kubernetes_config

import yaml


def state_cluster():
    """
    Return useless code.

    This returns useless code
    """
    ret = []
    return ret


def state_nodes(api_client=None):
    """
    Return nodes.

    This returns the nodes names
    """
    datanodes = []

    try:

        load_kubernetes_config()

        core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)
        nodes = core_v1.list_node().items
    except Exception as e:
        print("Cant connect to the cluster: %s" % (e))
        return []

    for node in nodes:
        datanodes.append({'name': node.metadata.name,
                          'status': node.status.phase})
    return datanodes


def state_namespaces(api_client=None):
    """
    Return namespaces.

    This returns some namespace data
    """
    datanamespaces = []

    try:
        load_kubernetes_config()
        core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)
        namespaces = core_v1.list_namespace().items
    except Exception as e:
        print("Cant connect to the cluster: %s" % (e))
        return []

    for namespace in namespaces:
        datanamespaces.append({'name': namespace.metadata.name,
                               'status': namespace.status.phase})
    return datanamespaces


def state_pods(api_client=None):
    """
    Return pods.

    This returns some pod data
    """
    data_pods = []

    try:

        load_kubernetes_config()
        core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)
        pods = core_v1.list_pod_for_all_namespaces().items
    except Exception as e:
        print("Cant connect to the cluster: %s" % (e))
        return []

    for pod in pods:
        data_pods.append({'name': pod.metadata.name,
                          'namespace': pod.metadata.namespace,
                          'host_ip': pod.status.host_ip,
                          'pod_ip': pod.status.pod_ip,
                          'phase': pod.status.phase})

    return data_pods


def web_terminal():
    """
    Get pods.

    This is useless code
    """
    ret = []
    command = 'kubectl get po --all-namespaces'
    output = subprocess.check_output(command,
                                     stderr=subprocess.STDOUT,
                                     shell=True)
    ret.append(output.decode('utf-8'))
    return ret


def cluster_name_configured(api_client=None):
    """
    Get the current cluster name.

    This method should return the cluster name
    """
    cluster_name = "Not found"

    load_kubernetes_config()
    core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)

    try:
        # OpenShift case
        cd = core_v1.read_namespaced_config_map(name='cluster-config-v1',
                                                namespace='kube-system',
                                                pretty='true')
        if cd:
            # This will have a big yaml file
            # we need to convert to a dict
            raw = cd.data["install-config"]
            # We get the YAML from the data field of the configmap
            # And fetch the value we need
            cluster_name = yaml.safe_load(raw)["metadata"]["name"]
            print("Cluster name computed from OpenShift case")
            return cluster_name
    except Exception:
        print("Cant find clustername for OpenShift case")

    try:
        if api_client.configuration.host is not None:
            return urlparse(api_client.configuration.host).hostname
    except Exception:
        print("Cant find the clustername in the config object")

    # If we dont manage to find it we fall back to the CLI as a last resource
    try:
        command = 'kubectl config view -o jsonpath="{.clusters[].name}"'
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
        print(output)
        return output.decode('utf-8')
    except Exception:
        print("Cant find the clustername at all")
    return cluster_name
