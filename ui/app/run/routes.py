#!/usr/bin/env python

"""
Copyright 2019 Kubeinit (kubeinit.com).

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


# import os
import json

import app
from app.base.allocated import compute_allocated_resources
# from app.base.hexa import hexagons_data
from app.base.k8sclient import (cluster_name_configured)
#                                 state_namespaces,
#                                 state_nodes,
#                                 state_pods)
from app.run import blueprint
from app.run.forms import RunForm

from flask import current_app, redirect, render_template, request, url_for

from google.cloud import firestore

from jinja2 import TemplateNotFound

from pystol.operator import insert_pystol_object

# from flask_login import (current_user,
#                         login_required,
#                         login_user,
#                         logout_user)

try:
    from pystol import __version__
    KUBEINIT_VERSION = __version__
except ImportError:
    KUBEINIT_VERSION = "Not installed"
#
# Begin authentication
#
try:
    from app.auth.routes import get_session_data
    from app.auth.util import remote_cluster
except ImportError:
    print("Module not available")

try:
    fdb = firestore.Client()
    transaction = fdb.transaction()
except Exception as e:
    print("Cant connect to firestore: %s" % (e))
#
# End authentication
#


@blueprint.route('/', methods=['GET', 'POST'])
def run():
    """
    Render all the templates not from base.

    This is a main method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    form = RunForm(request.form)
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None

    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    if 'kubeconfig' not in session or session['kubeconfig'] is None or session['kubeconfig'] == '':
        kubeconfig = None
        api_client = None
    else:
        kubeconfig = session['kubeconfig']
        api_client = remote_cluster(kubeconfig=kubeconfig)

    if ('username' not in session or
        session['username'] is None or
        session['username'] == '' or
        'email' not in session or
        session['email'] is None or
            session['email'] == ''):

        username = None
        email = None
    else:
        username = session['username']
        email = session['email']

    form = RunForm()

    if request.method == "POST":
        dict = request.form

        namespace = ""
        collection = ""
        role = ""
        source = ""
        extra_vars = {}

        if 'namespace' in dict:
            namespace = dict['namespace']
        else:
            namespace = ""

        if 'collection' in dict:
            collection = dict['collection']
        else:
            collection = ""

        if 'role' in dict:
            role = dict['role']
        else:
            role = ""

        if 'source' in dict:
            source = dict['source']
        else:
            source = ""

        if 'extra_vars' in dict:
            if dict['extra_vars'] == "" or dict['extra_vars'] is None:
                extra_vars = "{}"
            else:
                extra_vars = dict['extra_vars']
        else:
            extra_vars = "{}"

        errors = 0
        try:
            json.loads(extra_vars)
        except ValueError as e:
            print(e)
            errors = errors + 1

        if errors == 0:
            insert_pystol_object(namespace=namespace,
                                 collection=collection,
                                 role=role,
                                 source=source,
                                 extra_vars=extra_vars,
                                 api_client=api_client)
            return redirect(url_for('executed_blueprint.executed'))
        else:
            form.extra_vars.errors = ["This must be a valid JSON"]
    try:
        return render_template('run.html',
                               username=username, email=email,
                               form=form,
                               compute_allocated_resources=compute_allocated_resources(
                                   api_client=api_client),
                               cluster_name_configured=cluster_name_configured(
                                   api_client=api_client),
                               kubeinit_version=KUBEINIT_VERSION,)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except Exception as e:
        print("Exception found in %s: %s" % (blueprint.name, e))
        if current_app.config['DEBUG']:
            raise e
        return render_template('page-500.html'), 500
