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


from tests.test_base import check_blueprints, check_pages


@check_pages('/', '/home/index')
def test_pages(base_client):
    """
    Run the selenium test.

    This is a Kubeinit function
    """
    # do something
    base_client.post('/', data={})
    # the pages are tested (GET request: 200) afterwards by the
    # @check_pages decorator


@check_blueprints('/forms', '/ui')
def test_blueprints(base_client):
    """
    Run the selenium test.

    This is a Kubeinit function
    """
    # do something
    base_client.post('/', data={})
    # the blueprints are tested (GET request: 200) afterwards by the
    # @check_blueprints decorator
