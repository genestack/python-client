#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *
from odm_sdk import TaskLogViewer, get_connection, make_connection_parser

# add extra arguments to the Genestack arguments parser for this script
parser = make_connection_parser()
parser.add_argument('-f', '--follow', action='store_true', help="Follow the logs' output if the task is not done")
parser.add_argument('-t', '--type', metavar='<log_type>',
                    choices=[TaskLogViewer.STDERR, TaskLogViewer.STDOUT],
                    default=TaskLogViewer.STDOUT,
                    help="Type of logs to display ('{0}' or '{1}' ; default is '{0}')".format(
                        TaskLogViewer.STDOUT, TaskLogViewer.STDERR))
parser.add_argument('accession', metavar='<accession>', help='Accession of the file for which to display the logs')
arguments = parser.parse_args()

# connect to Genestack
connection = get_connection(arguments)
log_viewer = TaskLogViewer(connection)

# print task logs
log_viewer.print_log(arguments.accession, log_type=arguments.type, follow=arguments.follow)
