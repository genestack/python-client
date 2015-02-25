Getting Started with Python SDK
###############################

Installing genestack
********************

- clone `repo <https://github.com/genestack/pythonSDK/>`_ or download and unpack  `latest release <https://github.com/genestack/pythonSDK/releases/latest/>`_
- navigate to repository folder or unpacked folder


Installing
----------

Install via pip:

.. code-block:: sh

    $ sudo pip install .

If you want you can install manually

Ensure that `keyring <https://pypi.python.org/pypi/keyring>`_ is installed


.. code-block:: sh

    $ sudo python setup.py install

Test your installation:

.. code-block:: sh

    $ python -c 'import genestack; print genestack.__version__'


Configuring Credentials
***********************

Create genestack account if you don't have one.

Run init script:


.. code-block:: sh

    $ genestack-user-setup.py init

Input email and password for genestack platform. If your email and password match setup is finished.

To check result execute:

.. code-block:: sh

    $ genestack-user-setup.py list
    user@email.com (default):
    email     user@email.com
    host      platform.genestack.org

.. note::

   Password is stored in system secure storage (See https://pypi.python.org/pypi/keyring for more information)
   If system storage is not accessible it will ask your permission to store password as plain text in config file.


.. note::

   This data is not synchronized with server, if you change password on server you need to change it here too.


Setup additional users
----------------------

If you have more then one account on genestack platform you may want to add other users.

Each user needs to have unique alias, email, host and password. There is not limitation to number of aliases.
You can even create couple of them for one account. To add user execute:

.. code-block:: sh

    $ genestack-user-setup.py add

.. note::

    See more info about user management: :doc:`scripts/genestack-user-setup`

.. _Connection:

Connection
**********

To work with platform you should have connection. First thing you need is to have account at genestack platform.


Connection via arguments
------------------------

Preferred way to get connection via helper function.  First thing you need to setup users.
get_connection use Argparse module to get your credentials from config file. By default it uses credentials of default user.
You can specify other user by adding ``-u <alias>`` to command line argument.

**Get connection**::

    from genestack import get_connection

    connection = get_connection()
    print connection.whoami()

**Run script from commandline**:

.. code-block:: sh

    # with default user
    $ ./script.py
    user@email.com

    # with user bob@email.com that present in config with alias bob
    $ ./script.py -u bob
    bob@email.com

.. note::

    In case then you need more arguments you need to add it to parser that returned by :py:func:`~genestack.make_connection_parser`.
    Arguments ``-u``, ``-p`` and ``-H`` are reserved for connection.


**Connection with additional script arguments**::

    from genestack import get_connection, make_connection_parser

    # create instance of argparse.ArgumentParser with predefined arguments for connection
    parser = make_connection_parser()
    parser.add_argument('-c', '--unicorn',  dest='unicorn', action='store_true', help='Set if you have unicorn.')
    args = parser.parse_args()
    connection = get_connection(args)
    if args.unicorn:
        print connection.whoami(), 'has unicorn!'
    else:
        print connection.whoami(), 'does not have unicorn.'

.. code-block:: sh

    $ ./script.py
    user@email.com has unicorn!

    $ ./script.py -u bob
    bob@email.com does not have unicorn.


**Arguments for connection parser**

* Using settings:

  if no argument specified get_connection will return connection to default user

  if only ``-u <alias>`` is specified will be used user from settings. If user is not present system will switch to interactive login with default server.

* Raw input:

    if ``-H <host>`` or ``-p <password>`` or both will be specified login will treat it as raw input

    ``-u <email>`` expects email

    ``-H <host>`` server host, if it is not specified will use default host.

    ``-p <password>`` if password is not specified user should add it in interactive mode.

    .. code-block:: sh

        $ ./script.py -u user@email.com -H platform.genestack.org -p passwords


Create connection directly in code
----------------------------------

This approach required more efforts and require to store your password as plain text

.. code-block:: python

    from genestack import Connection

    # crease connection object for server
    connection = Connection('https://platform.genestack.org/endpoint')

    # login as user: 'user@email.com' with password 'password'
    connection.login('user@email.com', 'password')
    print connection.whoami()


Run script from commandline:

.. code-block:: sh

    $ ./script.py
    user@email.com

Calling application methods with connection
*******************************************

To call application method you need to know application_id and method name::

    from genestack import get_connection


    connection = get_connection()
    print connection.application('genestack/signin').invoke('whoami')


If your application have a lot of methods you may create own class::

    from genestack import Application, get_connection


    class SignIn(Application):
        APPLICATION_ID = 'genestack/signin'

        def whoami(self):
            return self.invoke('whoami')


    connection = get_connection()
    signin = SignIn(connection)
    print signin.whoami()

Calling method with arguments::

    from genestack import get_connection, Metainfo, PRIVATE


    connection = get_connection()
    metainfo = Metainfo()
    metainfo.add_string(Metainfo.NAME, "New folder")
    print connection.application('genestack/filesUtil').invoke('createFolder', PRIVATE, metainfo)

Number, order and type of arguments should match for python and java method.


Using predefined wrappers
*************************

FilesUtil
=========

File utils used for common file operations: find, link, remove and share.

To work with FilesUtil you need to connection::

    >>> from genestack import get_connection
    >>> connection = get_connection()

Create instance::

    >>> from genestack import FilesUtil
    >>> file_utils = FilesUtil(connection)


Create folder in user folder::

    >>> folder_accession = file_utils.create_folder("My new folder")
    >>> print folder_accession
    GSF000001

You can specify any folder you want as parent::

    >>> inner_folder_accession = file_utils.create_folder("My inner folder", parent=folder_accession)
    >>> print inner_folder_accession
    GSF000002


Find folder by its name::

    >>> folder_accession = file_utils.find_file_by_name("My inner folder", file_class=FilesUtil.IFolder)
    >>> print folder_accession
    GSF000002


See :ref:`FilesUtil` for more methods.


Importers
*********

First step you need connection::

    >>> from genestack import get_connection
    >>> connection = get_connection()

To import data instantiate data importer with connection::

    >>> from genestack import DataImporter
    >>> importer = DataImporter(connection)

Create experiment in ``Imported files``::

    >>> experiment = importer.create_experiment(name='Sample of paired-end reads from A. fumigatus WGS experiment',
    ... description='A segment of a paired-end whole genome sequencing experiment of A. fumigatus')


Add sequencing assay for experiment. Use local files as sources::


    >>> assay = importer.create_sequencing_assay(experiment,
    ...                                          name='Test paired-end sequencing of A. fumigatus',
    ...                                          links=['ds1.gz', 'ds2.gz'],
    ...                                          organism='Aspergillus fumigatus',
    ...                                          method='genome variation profiling by high throughput sequencing')
    Uploading ds1.gz - 100.00%
    Uploading ds2.gz - 100.00%

To find out file in system print result::

    >>> print 'Successfully load assay with accession', assay, 'to experiment', experiment
    Successfully load assay with accession GSF000002 to experiment GSF000001

Start file initialization::

    >>> from genestack import FileInitializer
    >>> initializer = FileInitializer(connection)
    >>> initializer.initialize([assay])
    >>> print 'Start initialization of', assay
    Start initialization of GSF000002

As result you will have:

    - ``Experiment`` folder in ``Imported files``
    - ``Sequencing assay`` file in experiment
    - Two ``Raw Upload`` files in ``Uploaded files`` folder. This is your local files located on genestack storage. You can remove them after initialization of assay.


See :ref:`DataImporter` for more methods.