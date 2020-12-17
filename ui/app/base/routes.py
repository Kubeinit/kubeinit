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

import app
from app.base import blueprint
from app.base.k8sclient import (cluster_name_configured,
                                state_namespaces,
                                state_nodes,
                                state_pods,
                                web_terminal)

from flask import jsonify, redirect, render_template, request, url_for
# , session

# from flask_login import (current_user,
#                          login_required,
#                          login_user,
#                          logout_user)

from google.cloud import firestore

from pystol.lister import list_actions, show_actions

try:
    from pystol import __version__
    PYSTOL_VERSION = __version__
except ImportError:
    PYSTOL_VERSION = "Not installed"
#
# Begin authentication
#
try:
    from app.auth.routes import get_session_data
#    from app.auth.util import remote_cluster
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


@blueprint.route('/error-<error>')
def route_errors(error):
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return render_template('errors/{}.html'.format(error))


# API endpoints
@blueprint.route('/api/v1/ListActions', methods=['GET'])
def api_list_actions():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(list_actions())


@blueprint.route('/api/v1/ShowActions', methods=['GET'])
def api_show_actions():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(show_actions())


@blueprint.route('/api/v1/StateNamespaces', methods=['GET'])
def api_state_namespaces():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(state_namespaces())


@blueprint.route('/api/v1/StateNodes', methods=['GET'])
def api_state_nodes():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(state_nodes())


@blueprint.route('/api/v1/StatePods', methods=['GET'])
def api_state_pods():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(state_pods())


@blueprint.route('/api/v1/Terminal', methods=['GET'])
def api_web_terminal():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(web_terminal())


@blueprint.route('/api/v1/ClusterName', methods=['GET'])
def api_cluster_name_configured():
    """
    Define a route.

    This is a main routing method
    """
    #
    # Basic authentication module requirement
    # If the auth module is installed and the user is not authenticated, so go to login
    #
    session = {}
    if hasattr(app, 'auth'):
        try:
            session = get_session_data(transaction=transaction, session_id=request.cookies.get('session_id'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth_blueprint.login'))
    else:
        session['kubeconfig'] = None
    # not current_user.is_authenticated:
    if hasattr(app, 'auth') and session['email'] is None:
        return redirect(url_for('auth_blueprint.login'))
    #
    # End basic authentication requirement
    #

    return jsonify(cluster_name_configured())


@blueprint.route('/shutdown')
def shutdown():
    """
    Define a route.

    This is a main routing method
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@blueprint.errorhandler(404)
def not_found_error(error):
    """
    Define a route.

    This is a main routing method
    """
    return render_template('page-404.html',
                           template_folder="../home/templates/"), 404


@blueprint.errorhandler(404)
def internal_error(error):
    """
    Define a route.

    This is a main routing method
    """
    return render_template('page-500.html',
                           template_folder="../home/templates/"), 500

# Errors
# @login_manager.unauthorized_handler
# def unauthorized_handler():
#    """
#    Define a route.
#
#    This is a main routing method
#    """
#    return render_template('page-403.html',
#                           template_folder="../home/templates/"), 403


# @blueprint.errorhandler(403)
# def access_forbidden(error):
#    """
#    Define a route.
#
#    This is a main routing method
#    """
#    return render_template('page-403.html',
#                           template_folder="../home/templates/"), 403
