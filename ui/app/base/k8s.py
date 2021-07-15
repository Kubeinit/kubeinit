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
# import tempfile
# import json
# import os
# import sys
# import urllib
# import yaml

# from flask import Flask, redirect, render_template, request, url_for

import kubernetes
# from kubernetes import client
# from kubernetes.client import Configuration
# from kubernetes.config import kube_config

from pystol.operator import load_kubernetes_config

PYSTOL_BRANCH = "master"

#
# We load the Kubernetes cluster config depending
# where we execute the operator from.
#


def state_cluster(api_client=None):
    """
    List component of cluster.

    This is a main component of the input for the controller
    """
    load_kubernetes_config()
    api = kubernetes.client.CustomObjectsApi(api_client=api_client)

    group = "kubeinit.com"
    version = "v1alpha1"
    namespace = "pystol"
    plural = "pystolactions"
    pretty = 'true'

    ret = []
    try:
        resp = api.list_namespaced_custom_object(group=group,
                                                 version=version,
                                                 namespace=namespace,
                                                 plural=plural,
                                                 pretty=pretty)
        for action in resp['items']:
            ret.append({'name':
                        action['metadata']['name'],
                        'creationTimestamp':
                        action['metadata']['creationTimestamp'],
                        'action_state':
                        action['spec']['action_state'],
                        'workflow_state':
                        action['spec']['workflow_state']})
    except Exception:
        print("No objects found...")
    return ret
