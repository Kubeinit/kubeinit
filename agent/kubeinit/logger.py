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

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from kubeinit.const import KUBEINIT_LOG_FILE

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - "
                              "%(levelname)s - %(message)s")


def get_console_handler():
    """
    Get logger console handler.

    This is a main component of the input for the controller
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    """
    Get logger file handler.

    This is a main component of the input for the controller
    """
    file_handler = TimedRotatingFileHandler(
        KUBEINIT_LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    """
    Get logger.

    This is a main component of the input for the controller
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # We do not want to print in the console
    # logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
