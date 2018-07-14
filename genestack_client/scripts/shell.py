#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
import json
import shlex

from getpass import getpass
from datetime import datetime

from genestack_client.genestack_shell import Command, GenestackShell
from genestack_client import ShareUtil

APPLICATION_SHELL = 'genestack/shell'


def serialize_params(params):
    args = []
    for arg in params:
        try:
            args.append(json.loads(arg))
        except ValueError:
            args.append(arg)
    return args

class Call(Command):
    COMMAND = 'call'
    DESCRIPTION = 'call another application\'s method'
    OFFLINE = False

    def update_parser(self, p):
        p.add_argument(
            'applicationId',
            help='full application id'
        )
        p.add_argument(
            'method',
            help='application method'
        )
        p.add_argument(
            'params', nargs=argparse.REMAINDER,
            help='params'
        )

    def do_request(self):
        params = serialize_params(self.args.params)
        return self.connection.application(self.args.applicationId).invoke(self.args.method, *params)

    def run(self):
        res = self.do_request()
        print(json.dumps(res, indent=2))

class Sudo(Call):
    COMMAND = 'sudo'
    DESCRIPTION = 'call a command as another user'
    OFFLINE = False

    def update_parser(self, p):
        p.add_argument('email', help='user email to act as')
        p.add_argument('application', help='application id')
        p.add_argument('method', help='application method')
        p.add_argument('params', nargs=argparse.REMAINDER, help='params')

    def do_request(self, password):
        params = [self.args.email, password, self.args.application, self.args.method] + self.args.params
        params = serialize_params(params)
        #print(params)
        return self.connection.application('genestack/shell').invoke('sudo', *params)

    def run(self):
        res = self.do_request('')
        password_attempts = 0
        while password_attempts < 3 and isinstance(res, basestring) and res.startswith('Incorrect password!'):
            if password_attempts > 0:
                print('Sorry, try again.')
            password = getpass('Password: ')
            res = self.do_request(password)
            password_attempts += 1
        if password_attempts == 3:
            print('sudo: 3 incorrect password attempts')

class Time(Call):
    DESCRIPTION = 'invoke with timer'
    COMMAND = 'time'

    def run(self):
        start = datetime.now()
        Call.run(self)
        print('Execution time: %s' % (datetime.now() - start))

class Groups(Command):
    DESCRIPTION = 'print information about user groups'
    COMMAND = 'groups'

    def run(self):
        share_util = ShareUtil(self.connection)
        print('User groups:')
        for accession, name in share_util.get_available_sharing_groups().items():
            print('  %s (%s)' % (name, accession))


class Shell(GenestackShell):
    COMMAND_LIST = [Time, Call, Groups, Sudo]

    def get_commands_for_help(self):
        commands = GenestackShell.get_commands_for_help(self)
        for data in self.connection.application(APPLICATION_SHELL).invoke('getCommands'):
            commands.append((data['name'],
                            'args: %s returns: %s. %s' % (
                                                ', '.join(data['params']) or 'None',
                                                data['returns'],
                                                data['docs'] or 'No documentation')))
        return commands

    def default(self, line):
        try:
            args = shlex.split(line)
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            return
        if args and args[0] in self.COMMANDS:
            self.process_command(self.COMMANDS[args[0]](), args[1:], self.connection)
        else:
            self.process_command(Call(), ['genestack/shell'] + args, self.connection)


def main():
    shell = Shell()
    shell.cmdloop()

if __name__ == '__main__':
    main()
