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

from collections import defaultdict
# from types import SimpleNamespace

# from app import app

# from flask import Flask, redirect, render_template, request, url_for

import kubernetes

from pint import UnitRegistry

from pystol.operator import load_kubernetes_config


ureg = UnitRegistry()
# Pod
ureg.define("pods = 1 = [pods]")

# Mem
ureg.define("kmemunits = 1 = [kmemunits]")
ureg.define("Ki = 1024 * kmemunits")
ureg.define("Mi = Ki^2")
ureg.define("Gi = Ki^3")
ureg.define("Ti = Ki^4")
ureg.define("Pi = Ki^5")
ureg.define("Ei = Ki^6")
# CPU
ureg.define("kcpuunits = 1 = [kcpuunits]")
ureg.define("m = 1/1000 * kcpuunits")
ureg.define("k = 1000 * kcpuunits")
ureg.define("M = k^2")
ureg.define("G = k^3")
ureg.define("T = k^4")
ureg.define("P = k^5")
ureg.define("E = k^6")

Q_ = ureg.Quantity


def compute_allocated_resources(api_client=None):
    """
    Get the allocated resources.

    This will get the cluster resources usage
    """
    load_kubernetes_config()
    core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)

    s_i = {'pods': {'allocatable': Q_('0 pods'),
                    'allocated': Q_('0 pods'),
                    'percentage': 0},
           'cpu': {'allocatable': Q_('0 m'),
                   'allocated': Q_('0 m'),
                   'percentage': 0},
           'mem': {'allocatable': Q_('0 Ki'),
                   'allocated': Q_('0 Ki'),
                   'percentage': 0},
           'storage': {'allocatable': Q_('0 Ki'),
                       'allocated': Q_('0 Ki'),
                       'percentage': 0}}

    try:
        nodes_list = core_v1.list_node().items
    except Exception as e:
        print("Something bad happened:  %s" % (e))
        return {'pods': {'allocatable': Q_('0 pods'),
                         'allocated': Q_('0 pods'),
                         'percentage': 0},
                'cpu': {'allocatable': Q_('0 m'),
                        'allocated': Q_('0 m'),
                        'percentage': 0},
                'mem': {'allocatable': Q_('0 Ki'),
                        'allocated': Q_('0 Ki'),
                        'percentage': 0},
                'storage': {'allocatable': Q_('0 Ki'),
                            'allocated': Q_('0 Ki'),
                            'percentage': 0}}

    for node in nodes_list:
        node_name = node.metadata.name
        node_stats = compute_node_resources(
            node_name=node_name, api_client=api_client)

        s_i['pods']['allocatable'] = (s_i['pods']['allocatable'] +
                                      node_stats['pods']['allocatable'])

        s_i['pods']['allocated'] = (s_i['pods']['allocated'] +
                                    node_stats['pods']['allocated'])

        s_i['cpu']['allocatable'] = (s_i['cpu']['allocatable'] +
                                     node_stats['cpu']['allocatable'])

        s_i['cpu']['allocated'] = (s_i['cpu']['allocated'] +
                                   node_stats['cpu']['allocated'])

        s_i['mem']['allocatable'] = (s_i['mem']['allocatable'] +
                                     node_stats['mem']['allocatable'])

        s_i['mem']['allocated'] = (s_i['mem']['allocated'] +
                                   node_stats['mem']['allocated'])

        s_i['storage']['allocatable'] = (s_i['storage']['allocatable'] +
                                         node_stats['storage']['allocatable'])

        s_i['storage']['allocated'] = (s_i['storage']['allocated'] +
                                       node_stats['storage']['allocated'])

    if int(s_i['pods']['allocatable'].magnitude) == 0:
        s_i['pods']['percentage'] = 0
    else:
        s_i['pods']['percentage'] = (
            (int(s_i['pods']['allocated'].magnitude) * 100) //
            (int(s_i['pods']['allocatable'].magnitude)))

    if int(s_i['cpu']['allocatable'].magnitude) == 0:
        s_i['cpu']['percentage'] = 0
    else:
        s_i['cpu']['percentage'] = (
            (int(s_i['cpu']['allocated'].magnitude) * 100) //
            (int(s_i['cpu']['allocatable'].magnitude)))

    if int(s_i['mem']['allocatable'].magnitude) == 0:
        s_i['mem']['percentage'] = 0
    else:
        s_i['mem']['percentage'] = (
            (int(s_i['mem']['allocated'].magnitude) * 100) //
            (int(s_i['mem']['allocatable'].magnitude)))

    if int(s_i['storage']['allocatable'].magnitude) == 0:
        s_i['storage']['percentage'] = 0
    else:
        s_i['storage']['percentage'] = (
            (int(s_i['storage']['allocated'].magnitude) * 100) //
            (int(s_i['storage']['allocatable'].magnitude)))

    return s_i


def compute_node_resources(node_name=None, api_client=None):
    """
    Get the node allocated resources.

    This will get the node resources usage
    """
    load_kubernetes_config()
    core_v1 = kubernetes.client.CoreV1Api(api_client=api_client)

    s_i = {'pods': {'allocatable': Q_('0 pods'),
                    'allocated': Q_('0 pods'),
                    'percentage': 0},
           'cpu': {'allocatable': Q_('0 m'),
                   'allocated': Q_('0 m'),
                   'percentage': 0},
           'mem': {'allocatable': Q_('0 Ki'),
                   'allocated': Q_('0 Ki'),
                   'percentage': 0},
           'storage': {'allocatable': Q_('0 Ki'),
                       'allocated': Q_('0 Ki'),
                       'percentage': 0}}

    field_selector = ("metadata.name=" + node_name)

    try:
        node = core_v1.list_node(
            field_selector=field_selector).items[0]
    except Exception as e:
        print("Something bad happened:  %s" % (e))

    node_name = node.metadata.name
    allocatable = node.status.allocatable
    max_pods = int(int(allocatable["pods"]) * 1.5)

    field_selector = ("status.phase!=Succeeded,status.phase!=Failed," +
                      "spec.nodeName=" + node_name)

    if 'cpu' in allocatable:
        cpu_allocatable = Q_(allocatable["cpu"])
        cpu_allocatable.ito(ureg.m)
        s_i["cpu"]["allocatable"] = cpu_allocatable

    if 'memory' in allocatable:
        mem_allocatable = Q_(allocatable["memory"])
        mem_allocatable.ito(ureg.Mi)
        s_i["mem"]["allocatable"] = mem_allocatable

    if 'ephemeral-storage' in allocatable:
        storage_allocatable = Q_(allocatable["ephemeral-storage"])
        storage_allocatable.ito(ureg.Mi)
        s_i["storage"]["allocatable"] = storage_allocatable

    s_i["pods"]["allocatable"] = max_pods * ureg.pods

    pods = core_v1.list_pod_for_all_namespaces(limit=max_pods,
                                               field_selector=field_selector).items

    s_i["pods"]["allocated"] = len(pods) * ureg.pods

    # compute the allocated resources
    cpureqs, memreqs, storagereqs = [], [], []
    # cpulmts, memlmts, storagelmts = [], [], []

    for pod in pods:
        for container in pod.spec.containers:
            res = container.resources
            reqs = defaultdict(lambda: 0, res.requests or {})
            # lmts = defaultdict(lambda: 0, res.limits or {})

            cpureqs.append(Q_(reqs["cpu"]))
            memreqs.append(Q_(reqs["memory"]))
            storagereqs.append(Q_(reqs["ephemeral-storage"]))

            # cpulmts.append(Q_(lmts["cpu"]))
            # memlmts.append(Q_(lmts["memory"]))
            # storagelmts.append(Q_(lmts["ephemeral-storage"]))

    cpu_allocated = sum(cpureqs)
    cpu_allocated.ito(ureg.m)
    s_i["cpu"]["allocated"] = cpu_allocated

    mem_allocated = sum(memreqs)
    mem_allocated.ito(ureg.Mi)
    s_i["mem"]["allocated"] = mem_allocated

    storage_allocated = sum(storagereqs)
    storage_allocated.ito(ureg.Mi)
    s_i["storage"]["allocated"] = storage_allocated

    if int(s_i['pods']['allocatable'].magnitude) == 0:
        s_i['pods']['percentage'] = 0
    else:
        s_i['pods']['percentage'] = (
            (int(s_i['pods']['allocated'].magnitude) * 100) //
            (int(s_i['pods']['allocatable'].magnitude)))

    if int(s_i['cpu']['allocatable'].magnitude) == 0:
        s_i['cpu']['percentage'] = 0
    else:
        s_i['cpu']['percentage'] = (
            (int(s_i['cpu']['allocated'].magnitude) * 100) //
            (int(s_i['cpu']['allocatable'].magnitude)))

    if int(s_i['mem']['allocatable'].magnitude) == 0:
        s_i['mem']['percentage'] = 0
    else:
        s_i['mem']['percentage'] = (
            (int(s_i['mem']['allocated'].magnitude) * 100) //
            (int(s_i['mem']['allocatable'].magnitude)))

    if int(s_i['storage']['allocatable'].magnitude) == 0:
        s_i['storage']['percentage'] = 0
    else:
        s_i['storage']['percentage'] = (
            (int(s_i['storage']['allocated'].magnitude) * 100) //
            (int(s_i['storage']['allocatable'].magnitude)))

    return s_i
