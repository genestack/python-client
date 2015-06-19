#!python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2011-2015 Genestack Limited
# All Rights Reserved
# THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF GENESTACK LIMITED
# The copyright notice above does not evidence any
# actual or intended publication of such source code.
#

import sys
import os
import urllib2
import zipfile
import xml.dom.minidom as minidom
import json
from collections import namedtuple
from genestack import GenestackException
from genestack.GenestackShell import GenestackShell, Command


def validate_application_id(app_id):
    if len(app_id.split('/')) != 2:
        sys.stderr.write('Invalid application ID, expect "{vendor}/{application}" got: %s\n' % app_id)
        return False
    return True

APPLICATION_ID = 'genestack/application-manager'


SCOPE_DICT = {
    'system': 'SYSTEM',
    'user': 'USER',
    'session': 'SESSION'
}
DEFAULT_SCOPE = 'user'


def strip_appid_list(app_ids):
    return [x.strip(',; \t') for x in app_ids]


class Info(Command):
    COMMAND = 'info'
    DESCRIPTION = 'Read and show info from applications JAR file.'
    OFFLINE = True

    def update_parser(self, p):
        p.add_argument(
            '-f', '--with-filename', action='store_true',
            help='show file names for each JAR'
        )
        p.add_argument(
            '-F', '--no-filename', action='store_true',
            help='do not show file names'
        )
        p.add_argument(
            '--vendor', action='store_true',
            help='show only vendor for each JAR file'
        )
        p.add_argument(
            'files', metavar='<jar_file_or_folder>', nargs='+',
            help='file to upload or folder with single JAR file inside (recursively)'
        )

    def run(self):
        jar_files = [resolve_jar_file(f) for f in self.args.files]
        return show_info(
            jar_files, self.args.vendor,
            self.args.with_filename, self.args.no_filename
        )


class Install(Command):
    COMMAND = 'install'
    DESCRIPTION = 'Upload and install JAR files to Genestack system.'

    def update_parser(self, p):
        p.add_argument(
            '-o', '--override', action='store_true',
            help='overwrite old version of applications with the new one'
        )
        p.add_argument(
            '-s', '--stable', action='store_true',
            help='mark installed applications as stable'
        )
        p.add_argument(
            '-S', '--scope', metavar='<scope>', choices=SCOPE_DICT.keys(),
            default=DEFAULT_SCOPE,
            help='scope in which application will be stable'
                 ' (default is \'%s\'): %s' %
                 (DEFAULT_SCOPE, ' | '.join(SCOPE_DICT.keys()))
        )
        p.add_argument(
            'version', metavar='<version>',
            help='version of applications to upload'
        )
        p.add_argument(
            'files', metavar='<jar_file_or_folder>', nargs='+',
            help='file to upload or folder with single JAR file inside (recursively)'
        )

    def run(self):
        jar_files = [resolve_jar_file(f) for f in self.args.files]
        return upload_file(
            self.connection.application(APPLICATION_ID),
            jar_files, self.args.version, self.args.override,
            self.args.stable, self.args.scope
        )


class ListVersions(Command):
    COMMAND = 'versions'
    DESCRIPTION = 'Show information about available applications.'

    def update_parser(self, p):
        p.add_argument(
            '-s', action='store_true', dest='show_stable',
            help='display stable scopes in output (S: System, U: User, E: sEssion)'
        )
        p.add_argument(
            '-o', action='store_true', dest='show_owned',
            help='show only versions owned by current user'
        )
        p.add_argument(
            'app_id', metavar='<appId>',
            help='application identifier to show versions'
        )

    def run(self):
        app_id = self.args.app_id
        if not validate_application_id(app_id):
            return
        stable_versions = None
        if self.args.show_stable:
            stable_versions = self.connection.application(APPLICATION_ID).invoke('getStableVersions', app_id)
        result = self.connection.application(APPLICATION_ID).invoke('listVersions', app_id, self.args.show_owned)
        result.sort()
        for item in result:
            if stable_versions is None:
                print item
            else:
                print '%1s%1s%1s %s' % (
                    'S' if item == stable_versions.get('SYSTEM') else '-',
                    'U' if item == stable_versions.get('USER') else '-',
                    'E' if item == stable_versions.get('SESSION') else '-',
                    item
                )


class ListApplications(Command):
    COMMAND = 'applications'
    DESCRIPTION = 'Show information about available applications.'

    def run(self):
        result = self.connection.application(APPLICATION_ID).invoke('listApplications')
        result.sort()
        for item in result:
            print item


class MarkAsStable(Command):
    COMMAND = 'stable'
    DESCRIPTION = 'Mark applications of the specified version as stable.'

    def update_parser(self, p):
        p.add_argument(
            'version', metavar='<version>',
            help='applications version or \'-\' (minus sign) to remove'
                 ' stable version'
        )
        p.add_argument(
            'app_id_list', metavar='<appId>', nargs='+',
            help='application identifier to mark as stable'
        )
        p.add_argument(
            '-S', '--scope', metavar='<scope>', choices=SCOPE_DICT.keys(),
            default=DEFAULT_SCOPE,
            help='scope in which application will be stable'
                 ' (default is \'%s\'): %s' %
                 (DEFAULT_SCOPE, ' | '.join(SCOPE_DICT.keys()))
        )

    def run(self):
        apps_ids = strip_appid_list(self.args.app_id_list)
        if not all(map(validate_application_id, apps_ids)):
            return
        version = self.args.version
        if version == '-':
            version = None
        return mark_as_stable(
            self.connection.application(APPLICATION_ID), version, apps_ids,
            self.args.scope
        )


class Remove(Command):
    COMMAND = 'remove'
    DESCRIPTION = 'Remove specific version of applications.'

    def update_parser(self, p):
        p.add_argument(
            'version', metavar='<version>', help='applications version'
        )
        p.add_argument(
            'app_id_list', metavar='<appId>', nargs='+',
            help='identifier of application to remove'
        )

    def run(self):
        apps_ids = strip_appid_list(self.args.app_id_list)
        if not all(map(validate_application_id, apps_ids)):
            return
        return remove_applications(
            self.connection.application(APPLICATION_ID), self.args.version, apps_ids
        )


class Reload(Command):
    COMMAND = 'reload'
    DESCRIPTION = 'Reload specific version of applications.'

    def update_parser(self, p):
        p.add_argument(
            'version', metavar='<version>', help='applications version'
        )
        p.add_argument(
            'app_id_list', metavar='<appId>', nargs='+',
            help='application identifier to mark as stable'
        )

    def run(self):
        apps_ids = strip_appid_list(self.args.app_id_list)
        if not all(map(validate_application_id, apps_ids)):
            return
        return reload_applications(
            self.connection.application(APPLICATION_ID), self.args.version, apps_ids
        )


# FIXME: This class should be removed; it is written only for debug purposes:
class Invoke(Command):
    COMMAND = 'invoke'
    DESCRIPTION = 'Invoke method of stable application.'

    def update_parser(self, p):
        p.add_argument(
            'app_id', metavar='<appId>',
            help='application identifier'
        )
        p.add_argument(
            'method_name', metavar='<method>',
            help='application method to call'
        )
        p.add_argument(
            'arguments', metavar='<args>', nargs='*',
            help='application method to call'
        )

    def run(self):
        application = self.connection.application(self.args.app_id)
        args = []
        for arg in self.args.arguments:
            try:
                args.append(json.loads(arg))
            except ValueError:
                args.append(arg)
        response = application.invoke(self.args.method_name, *args)
        if isinstance(response, list):
            for item in response:
                print item
        else:
            print response


def resolve_jar_file(file_path):
    if not os.path.isdir(file_path):
        return file_path

    jar_files = []
    for dirpath, dirnames, filenames in os.walk(file_path, followlinks=True):
        for f in filenames:
            if f.lower().endswith('.jar'):
                jar_files.append(os.path.join(dirpath, f))

    if len(jar_files) > 1:
        raise GenestackException('Too many JAR files found inside folder: %s' % file_path)
    elif not jar_files:
        raise GenestackException('No JAR files found inside folder: %s' % file_path)

    return jar_files[0]


def mark_as_stable(application, version, app_id_list, scope):
    try:
        print('Mark as stable (%s scope)' % scope)
        scope = SCOPE_DICT[scope]
        for app_id in app_id_list:
            sys.stdout.write('%-40s ... ' % app_id)
            sys.stdout.flush()
            application.invoke('markAsStable', app_id, scope, version)
            sys.stdout.write('ok\n')
            sys.stdout.flush()
    except Exception as e:
        sys.stdout.flush()
        sys.stderr.write('%s\n' % e.message)
        sys.stderr.flush()
        return 1


def remove_applications(application, version, app_id_list):
    try:
        print('Removing application(s) with version')
        for app_id in app_id_list:
            sys.stdout.write('%s ... ' % app_id)
            sys.stdout.flush()
            application.invoke('removeApplication', app_id, version)
            sys.stdout.write('ok\n')
            sys.stdout.flush()
    except Exception as e:
        sys.stdout.flush()
        sys.stderr.write('%s\n' % e.message)
        sys.stderr.flush()
        return 1


def reload_applications(application, version, app_id_list):
    try:
        print('Reloading applications')
        for app_id in app_id_list:
            sys.stdout.write('%s ... ' % app_id)
            sys.stdout.flush()
            application.invoke('reloadApplication', app_id, version)
            sys.stdout.write('ok\n')
            sys.stdout.flush()
    except Exception as e:
        sys.stdout.flush()
        sys.stderr.write('%s\n' % e.message)
        sys.stderr.flush()
        return 1


def upload_file(application, files_list, version, override, stable, scope):
    for file_path in files_list:
        result = upload_single_file(
            application, file_path, version, override,
            stable, scope
        )
        if result is not None and result != 0:
            return result


def upload_single_file(application, file_path, version, override,
                       stable, scope):
    try:
        parameters = {'version': version, 'override': override}
        upload_token = application.invoke('getUploadToken', parameters)
    except Exception as e:
        sys.stdout.flush()
        sys.stderr.write('%s\n' % e.message)
        sys.stderr.flush()
        return 1

    if upload_token is None:
        sys.stdout.flush()
        sys.stderr.write('Received null token, the upload is not accepted')
        sys.stderr.flush()
        return 1

    # upload_token, as returned by json.load(), is a Unicode string.
    # Without the conversion, urllib2.py passes a Unicode URL created from it
    # to httplib.py, and httplib.py fails in a non-graceful way
    # (http://bugs.python.org/issue12398)
    upload_token = upload_token.encode('UTF-8', 'ignore')
    try:
        result = application.upload_file(file_path, upload_token)
        # hack before fix ApplicationManagerApplication#processReceivedFile // TODO: return some useful information
        if result:
            print result

    except urllib2.HTTPError as e:
        sys.stdout.flush()
        sys.stderr.write('HTTP Error %s: %s\n' % (e.code, e.read()))
        sys.stderr.flush()
        return 1

    if not stable:
        return

    app_info = read_jar_file(file_path)

    return mark_as_stable(application, version, app_info.identifiers, scope)


AppInfo = namedtuple('AppInfo', [
    'vendor', 'identifiers'
])


def read_jar_file(file_path):
    with zipfile.ZipFile(file_path) as zip_file:
        try:
            info = zip_file.getinfo('applications.xml')
            with zip_file.open(info) as manifest:
                doc = minidom.parse(manifest)
                namespace = doc.documentElement.namespaceURI
                applications = doc.getElementsByTagNameNS(namespace, 'application')
                vendor = doc.getElementsByTagNameNS(namespace, 'vendor')[0].firstChild.nodeValue
                identifiers = [
                    vendor + '/' + a.getElementsByTagNameNS(namespace, 'id')[0].firstChild.nodeValue
                    for a in applications
                ]
        except KeyError as e:
            raise GenestackException('Unable to read applications.xml manifest from %s: %s' % (
                os.path.abspath(file_path), e))
        return AppInfo(vendor, identifiers)


def show_info(files, vendor_only, with_filename, no_filename):
    first_file = True
    for file_path in files:
        app_info = read_jar_file(file_path)

        if vendor_only:
            if no_filename:
                print app_info.vendor
            else:
                print '%s %s' % (file_path, app_info.vendor)
            continue

        if with_filename or not no_filename and len(files) > 1:
            if not first_file:
                print ''
            print 'File:', file_path

        print 'Vendor:', app_info.vendor
        print 'Applications:'
        for app_id in app_info.identifiers:
            print '\t%s' % app_id

        first_file = False


class ApplicationManager(GenestackShell):
    DESCRIPTION = ('Application manager is a script that lets you to add new applications into the system, '
                   'remove your uploaded applications from the system, '
                   'list available applications and do other related things.')
    INTRO = "Application manager shell.\nType 'help' for list of available commands.\n\n"
    COMMAND_LIST = [Info, Install, ListVersions, ListApplications, MarkAsStable, Remove, Reload, Invoke]


if __name__ == '__main__':
    shell = ApplicationManager()
    shell.cmdloop()
