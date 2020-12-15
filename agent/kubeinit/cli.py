#!/usr/bin/env python

"""
Copyright 2019 Kubeinit (kubeinit.com).

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at:

http://www.apache.com/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""


import logging
import logging.handlers
import os
import threading
from argparse import ArgumentParser

from kubeinit import __version__
from kubeinit.const import KUBEINIT_LOG_FILE
from kubeinit.get_banner import get_banner
from kubeinit.lib import connect_to_aas, connect_to_aas2


kubeinit_version = __version__

t1_stop = threading.Event()
t2_stop = threading.Event()

handler = logging.handlers.WatchedFileHandler(
    KUBEINIT_LOG_FILE)
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def main():
    """
    Application's entry point.

    Here, application's settings are read from the command line,
    environment variables and CRD. Then, retrieving and processing
    of Kubernetes events are initiated.
    """
    parser = ArgumentParser(
        description='Kubeinit - CLI',
        prog='kubeinit'
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' + kubeinit_version
    )

    parser.add_argument(
        '-b',
        '--banner',
        action='store_true',
        help='Print Kubeinit.com banner'
    )

    subparsers = parser.add_subparsers(title="Kubeinit subcommands",
                                       dest="command",
                                       help=("These are the options "
                                             "supported: \n"
                                             "The listen option will "
                                             "watch for CRD events. "
                                             "The run option will "
                                             "execute the Kubeinit "
                                             "actions against the cluster."))

    parser_connect = subparsers.add_parser('connect', help=("CLI options to run the "
                                                            "Kubeinit actions."))

    parser_connect.add_argument(
        '-k',
        '--key',
        default="",
        type=str,
        help=("The connection key:"
              "--extra-vars thisisakey"
              "Defaults to: empty"))

    subparsers.add_parser('status', help=("Show the connections status."))

    parser_show = subparsers.add_parser('show',
                                        help=("Get info from a connection."))

    parser_show.add_argument(
        "connection",
        nargs='?',
        default='',
        type=str,
        help=("Specify the connection to fetch details"))

    args = parser.parse_args()

    # print("Kubeinit called with the folowing parameters")
    # print(parser.parse_args())

    if args.banner:
        print(get_banner())
        exit()

    try:
        if (args.command == 'connect'):
            print("We will watch for objects to process")
            try:
                print(args.key)
                t1 = threading.Thread(target=connect_to_aas,
                                      args=(t1_stop,))
                t1.start()
                t2 = threading.Thread(target=connect_to_aas2,
                                      args=(t2_stop,))
                t2.start()
            except Exception as err:
                print("Error: unable to start thread: " + err)
        elif (args.command == 'status'):
            print(u"\U0001F4DA" + " Listing the deployed actions"
                                  " from the cluster.")
            print(u"\U0001F4A1" + " For further information use:"
                                  " kubeinit get <action_name> [--debug]")
            exit()
        elif (args.command == 'show'):
            print(u"\U0001F4E4" + " Getting the details from"
                                  " an specific action.")
            print(args.connection)
            exit()

    except KeyboardInterrupt:
        pass
    except Exception as err:
        raise RuntimeError('There is something wrong...' + err)

    while not t2_stop.is_set() or not t1_stop.is_set():
        pass
