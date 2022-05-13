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

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""Data center model."""


class DataCenter(db.Model):
    """Data model for the main data center."""

    __tablename__ = "kubeinit-datacenter"
    id = db.Column(db.Integer, primary_key=True)
    availability_zone = db.Column(db.String(80), nullable=False)
    airport_name = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    # hosts = db.relationship('Host', backref='host', lazy=True)

    def __repr__(self):
        """Get the class object name."""
        return "<DataCenter {}>".format(self.name)


class Host(db.Model):
    """Data model for the hosts inside the datacenter."""

    __tablename__ = "kubeinit-host"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    ipmi_user = db.Column(db.String(80), index=True, unique=True, nullable=False)
    ipmi_password = db.Column(db.String(80), index=True, unique=True, nullable=False)
    # datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenter.id'), nullable=False)
    # virtualmachines = db.relationship('VirtualMachine', backref='virtualmachine', lazy=True)

    def __repr__(self):
        """Get the class object name."""
        return "<Host {}>".format(self.name)


class VirtualMachine(db.Model):
    """Data model for the virtual machines in the data center."""

    __tablename__ = "kubeinit-virtualmachine"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    # host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    # datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenter.id'), nullable=False)

    def __repr__(self):
        """Get the class object name."""
        return "<VirtualMachine {}>".format(self.name)


class Cluster(db.Model):
    """Data model for a cluster in the datacenters."""

    __tablename__ = "kubeinit-cluster"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    distro = db.Column(db.String(80), index=True, unique=True, nullable=False)
    # virtualmachines = db.relationship('VirtualMachine', backref='virtualmachine', lazy=True)
    # hosts = db.relationship('Host', backref='host', lazy=True)

    def __repr__(self):
        """Get the class object name."""
        return "<Cluster {}>".format(self.name)
