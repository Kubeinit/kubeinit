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

from kubeinit import __version__

kubeinit_version = __version__


def get_banner():
    """
    Get banner method.

    This method prints
    the kubeinit.com banner.
    """
    banner = """
888    d8P           888              8888888          d8b 888
888   d8P            888                888            Y8P 888
888  d8P             888                888                888
888d88K     888  888 88888b.   .d88b.   888   88888b.  888 888888
8888888b    888  888 888 "88b d8P  Y8b  888   888 "88b 888 888
888  Y88b   888  888 888  888 88888888  888   888  888 888 888
888   Y88b  Y88b 888 888 d88P Y8b.      888   888  888 888 Y88b.
888    Y88b  "Y88888 88888P"   "Y8888 8888888 888  888 888  "Y888
  (kubeinit.com) agent version {}
""".format(kubeinit_version)
    return banner
