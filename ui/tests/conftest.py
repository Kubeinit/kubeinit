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

from threading import Thread
from time import sleep

from app import create_app, db

from config import config_dict

from pytest import fixture

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@fixture
def base_client():
    """
    Test the base app.

    This is method function
    """
    app = create_app(config_dict['Debug'])
    app_ctx = app.app_context()
    app_ctx.push()
    db.session.close()
    db.drop_all()
    yield app.test_client()


@fixture
def user_client():
    """
    Test the base app.

    This is method function
    """
    app = create_app(config_dict['Debug'])
    app_ctx = app.app_context()
    app_ctx.push()
    db.session.close()
    db.drop_all()
    client = app.test_client()
    create = {'username': '', 'password': '', 'create_account': ''}
    login = {'username': '', 'password': '', 'login': ''}
    with app.app_context():
        client.post('/create_user', data=create)
        client.post('/login', data=login)
        yield client


@fixture
def selenium_client():
    """
    Test the base app.

    This is method function
    """
    app = create_app(config_dict['Debug'], True)
    app_context = app.app_context()
    app_context.push()
    db.session.close()
    db.drop_all()
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # Flask can run in a separate thread, but the reloader expects to run in
    # the main thread: it must be disabled
    client = None
    try:
        client = webdriver.Chrome('./tests/chromedriver',
                                  chrome_options=options)
    except Exception:
        pass
    # if the client cannot start, we don't want to start a Thread as the
    # test execution would be stuck
    if client:
        Thread(
            target=app.run,
            kwargs={
                'host': '0.0.0.0',
                'port': 5000,
                'use_reloader': False
            }
        ).start()
        # give the server some time to start
        sleep(1)
        yield client
        client.get('http://127.0.0.1:5000/shutdown')
        client.quit()
    app_context.pop()
