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

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ApplicationAutoScaling, EC2
from diagrams.aws.network import ELB, PrivateSubnet, PublicSubnet, VPC
from diagrams.custom import Custom
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Crio

filename = os.path.splitext(os.path.basename(__file__))[0]
title = "Network layout"
direction = 'TB'
graph_attr = {
    "pad": "0"
}


class Region(Cluster):
    """Region."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "dotted",
        "labeljust": "l",
        "pencolor": "#AEB6BE",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }


class AvailabilityZone(Cluster):
    """Availability zone."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "dashed",
        "labeljust": "l",
        "pencolor": "#27a0ff",
        "fontname": "sans-serif",
        "fontsize": "12",
    }


class VirtualPrivateCloud(Cluster):
    """Virtual private cloud."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "",
        "labeljust": "l",
        "pencolor": "#00D110",
        "fontname": "sans-serif",
        "fontsize": "12",
    }
    _icon = VPC


class PrivateSubnet(Cluster):
    """Private subnet."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "",
        "labeljust": "l",
        "pencolor": "#329CFF",
        "fontname": "sans-serif",
        "fontsize": "12",
    }
    _icon = PrivateSubnet


class PublicSubnet(Cluster):
    """Public subnet."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "",
        "labeljust": "l",
        "pencolor": "#00D110",
        "fontname": "sans-serif",
        "fontsize": "12",
    }
    _icon = PublicSubnet


class SecurityGroup(Cluster):
    """Security group."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "dashed",
        "labeljust": "l",
        "pencolor": "#FF361E",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }


class AutoScalling(Cluster):
    """Auto scalling."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "dashed",
        "labeljust": "l",
        "pencolor": "#FF7D1E",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }
    _icon = ApplicationAutoScaling


class EC2Contents(Cluster):
    """EC2 contents."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "",
        "labeljust": "l",
        "pencolor": "#FFB432",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }
    _icon = EC2


class ServerContents(Cluster):
    """Server contents."""

    _default_graph_attrs = {
        "shape": "box",
        "style": "rounded,dotted",
        "labeljust": "l",
        "pencolor": "#A0A0A0",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }
    _icon = Server


with Diagram(title, filename=filename, graph_attr=graph_attr, outformat='png', direction=direction, show=False):
    with Cluster("Multicloud deployment", graph_attr={"fontsize": "15"}):  # overwrite attributes for the default cluster
        with ServerContents("chassis 1: Bastion host"):
            Custom("Chassis", "./resources/ovn.png")
            Crio("HAproxy")
            Crio("Nginx")
            Crio("Registry")
            Crio("Apache")
            Crio("Bind")
            Crio("dnsmasq")
        with AvailabilityZone("chassis 2"):
            Custom("Chassis", "./resources/ovn.png")
            Server("nyctea")
        with AvailabilityZone("chassis 3"):
            Server("tyto")
            Custom("Central", "./resources/ovn.png")
        with Region("chassis 4", graph_attr={"pencolor": "#60193C", "bgcolor": "#E587B5"}):  # one cluster defined but with overwritten attributes
            Custom("Chassis", "./resources/ovn.png")
            Server("strix")
            with VirtualPrivateCloud(""):
                with PrivateSubnet("Private"):
                    with SecurityGroup("web sg"):
                        with AutoScalling(""):
                            with EC2Contents("A"):
                                d1 = Crio("Container")
                            with ServerContents("A1"):
                                d2 = Crio("Container")

                    with PublicSubnet("Public"):
                        with SecurityGroup("elb sg"):
                            lb1 = ELB()
        with Region("chassis 5", graph_attr={"pencolor": "#60193C", "bgcolor": "#E587B5"}):  # one cluster defined but with overwritten attributes
            Custom("Chassis", "./resources/ovn.png")
            Server("otus")
            with VirtualPrivateCloud(""):
                with PrivateSubnet("Private"):
                    with SecurityGroup("web sg"):
                        with AutoScalling(""):
                            with EC2Contents("A"):
                                d3 = Crio("Container")
                            with ServerContents("A1"):
                                d4 = Crio("Container")

                with PublicSubnet("Public"):
                    with SecurityGroup("elb sg"):
                        lb2 = ELB()

    lb1 >> Edge(forward=True, reverse=True) >> d1
    lb1 >> Edge(forward=True, reverse=True) >> d2

    lb2 >> Edge(forward=True, reverse=True) >> d3
    lb2 >> Edge(forward=True, reverse=True) >> d4
