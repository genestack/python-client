# -*- coding: utf-8 -*-

from genestack_client import GenestackException, Metainfo, Application, SudoUtils

MAX_SEARCH_LIMIT = 100

CALCULATE_CHECKSUMS_KEY = 'genestack.checksum:markedForTests'
EXPECTED_CHECKSUM_PREFIX = 'genestack.checksum.expected:'


class SpecialFolders:
    """
    - ``IMPORTED``: folder where new files are created by Data Importers
    - ``CREATED``: default folder for files created by ``Preprocess`` and ``Analyse`` applications
    - ``TEMPORARY``: folder for temporary files
    - ``UPLOADED``:  folder where raw files are stored
    """
    IMPORTED = 'imported'
    CREATED = 'created'
    TEMPORARY = 'temporary'
    UPLOADED = 'uploaded'


class FilesUtil(Application):
    """
    An application to perform file management operations on Genestack.
    """
    APPLICATION_ID = 'genestack/filesUtil'

    CONTAINER = 'com.genestack.api.files.IContainerFile'
    FOLDER = 'com.genestack.api.files.IFolder'
    EXPERIMENT = 'com.genestack.bio.files.IExperiment'

    FILE = 'com.genestack.api.files.IFile'
    UNALIGNED_READS = 'com.genestack.bio.files.IUnalignedReads'
    ALIGNED_READS = 'com.genestack.bio.files.IAlignedReads'
    VARIATION_FILE = 'com.genestack.bio.files.IVariationFile'
    APPLICATION_PAGE_FILE = 'com.genestack.api.files.IApplicationPageFile'
    REFERENCE_GENOME = 'com.genestack.bio.files.IReferenceGenome'
    AUXILIARY_FILE = 'com.genestack.api.files.IAuxiliaryFile'
    INDEX_FILE = 'com.genestack.api.files.IIndexFile'
    CODON_TABLE = 'com.genestack.bio.files.ICodonTable'
    GENOME_BED_DATA = 'com.genestack.bio.files.genomedata.IGenomeBEDData'
    GENOME_WIGGLE_DATA = 'com.genestack.bio.files.genomedata.IGenomeWiggleData'
    GENOME_ANNOTATIONS = 'com.genestack.bio.files.IGenomeAnnotations'
    HTSEQ_COUNTS = 'com.genestack.bio.files.IHTSeqCounts'
    EXTERNAL_DATABASE = 'com.genestack.bio.files.IExternalDataBase'
    PREFERENCES_FILE = 'com.genestack.api.files.IPreferencesFile'
    REPORT_FILE = 'com.genestack.api.files.IReportFile'
    RAW_FILE = 'com.genestack.api.files.IRawFile'
    MICROARRAY_ASSAY = 'com.genestack.bio.files.IMicroarrayAssay'
    SEQUENCING_ASSAY = 'com.genestack.bio.files.ISequencingAssay'


    def find_reference_genome(self, organism, assembly, release):
        """
        Returns the accession of the reference genome with the specified parameters:
        ``organism``, ``assembly``, ``release``.
        If more than one or no genome is found, the corresponding exceptions are thrown.

        :param organism: organism
        :type organism: str
        :param assembly: assembly
        :type assembly: str
        :param release: release
        :type release: str
        :return: accession
        :rtype: str
        :raises: :py:class:`~genestack_client.genestack_exceptions.GenestackServerException` if more than one genome, or no genome is found
        """
        return self.invoke('findReferenceGenome', organism, assembly, release)

    def find_file_by_name(self, name, parent=None, file_class=FILE):
        """
        Finds file with specified name (ignore case!) and type.
        If no file is found ``None`` is returned.
        If more than one file is found the first one is returned.
        If the parent container is not found, the corresponding exceptions are thrown.

        :param name: file name
        :type name: str
        :param parent: parent accession, private folder is default
        :type parent: str
        :param file_class: File class to be returned, default IFile
        :type file_class: str
        :return: file accession
        :rtype: str
        """
        return self.invoke(
            'getFileByName',
            name, parent, file_class
        )

    # SA: TODO: remove this methods and change usage to findFileByName
    def find_folder_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.FOLDER)

    def find_aligned_reads_file_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.ALIGNED_READS)

    def find_unaligned_reads_file_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.UNALIGNED_READS)

    def find_variation_file_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.VARIATION_FILE)

    def find_experiment_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.EXPERIMENT)

    def find_application_page_file_by_name(self, name, parent=None):
        return self.find_file_by_name(name, parent, self.APPLICATION_PAGE_FILE)

    # FIXME: use pagination in this method, see #5063
    def collect_initializable_files_in_container(self, accession):
        """
        Recursively search for all initialisable file in container.

        :param accession: accession of container
        :type accession: str
        :return: list of accessions
        :rtype: list
        """
        return self.invoke('collectInitializableFilesInContainer', accession)

    def get_file_children(self, container_accession):
        """
        Return accessions of files linked to current container.

        :param container_accession:  accession of container
        :type container_accession: str
        :return: list of accessions
        :rtype: list
        """
        return self.invoke('getFileChildren', container_accession)

    def create_folder(self, name, parent=None, description=None, metainfo=None):
        """
        Create a folder.

        :param name: name of the folder
        :type name: str
        :param parent: if not specified, create folder in the user's private folder
        :type parent: str
        :param description: description of the folder (goes into the metainfo)
        :type description: str
        :param metainfo: additional :py:class:`~genestack_client.Metainfo`.
            Description and accession should be specified either via arguments or in a metainfo object (but not in both).
        :type metainfo: Metainfo
        :return: accession of created folder
        """
        metainfo = metainfo or Metainfo()
        metainfo.add_string(Metainfo.NAME, name)
        if description is not None:
            metainfo.add_string(Metainfo.DESCRIPTION, description)
        return self.invoke('createFolder', parent, metainfo)

    def find_or_create_folder(self, name, parent=None):
        """
        Return the folder accession if it already exists, and create it otherwise.
        If more than one folder is found the first one is returned.

        :param name: display name
        :type name: str
        :param parent: parent accession, use home folder if None
        :type parent: str
        :return: accession of folder
        :rtype: str
        """
        return self.invoke('findOrCreateFolder', name, parent)

    def link_file(self, accession, parent):
        """
        Link a file to a folder.

        :param accession: file accession
        :type accession: str
        :param parent: parent folder accession
        :type parent: str
        :rtype: None
        """
        self.invoke('linkFiles', {accession: [parent]})

    def unlink_file(self, accession, parent):
        """
        Unlink a file from a folder.

        :param accession: file accession
        :type accession: str
        :param parent: folder accession
        :type parent: str
        :rtype: None
        """
        self.invoke('unlinkFiles', {accession: [parent]})

    def link_files(self, children_to_parents_dict):
        """
        Link files to containers.

        :param children_to_parents_dict: dictionary where keys are accessions of the files to link, and
            values are lists of accessions of the containers to link into
        :type: dict

        :rtype: None
        """
        self.invoke('linkFiles', children_to_parents_dict)

    def unlink_files(self, children_to_parents_dict):
        """
        Unlink files from containers.

        :param children_to_parents_dict: dictionary where keys are accessions of the files to unlink, and
            values are lists of accessions of the containers to unlink from
        :type children_to_parents_dict: dict[str, list[str]]
        :rtype: None
        """
        self.invoke('unlinkFiles', children_to_parents_dict)

    def clear_container(self, container_accession):
        """
        Unlink all files from a container.

        :param container_accession: accession of the container
        :type container_accession: str
        :rtype: None
        """
        self.invoke('clearContainer', container_accession)

    def add_metainfo_string_value(self, accession_list, key, value):
        """
        Add a string value to the metainfo of specified files.

        :param accession_list: list of files to be updated
        :type accession_list: list
        :param key: metainfo key
        :type key: str
        :param value: string
        :type value: str
        :rtype: None
        """
        self.invoke('addMetainfoStringValue', accession_list, key, value)

    def replace_metainfo_string_value(self, accession_list, key, value):
        """
        Replace a string value in the metainfo of specified files.

        :param accession_list: list of files to be updated
        :type accession_list: list
        :param key: metainfo key
        :type key: str
        :param value: string
        :type value: str
        :rtype: None
        """
        self.invoke('replaceMetainfoStringValue', accession_list, key, value)

    def remove_metainfo_value(self, accession_list, key):
        """
        Delete a key from the metainfo of specified files.

        :param accession_list: list of files to be updated
        :type accession_list: list
        :param key: metainfo key
        :type key: str
        :rtype: None
        """
        self.invoke('removeMetainfoValue', accession_list, key)

    def add_metainfo_values(self, accession, metainfo, skip_existing_keys=True, replace_existing_keys=False):
        """
        Add metainfo to a specified file.
        By default, metainfo keys that are already present in the file will be skipped.

        :param accession: accession of the file to update
        :param metainfo: metainfo object containing the metainfo to add
        :type metainfo: Metainfo
        :param skip_existing_keys: ignore metainfo keys that are already present in the file's metainfo
            (default: ``True``)
        :type skip_existing_keys: bool
        :param replace_existing_keys: replace the existing metainfo value for the metainfo keys
            that are already present in the file's metainfo (default: ``False``)
        :type replace_existing_keys: bool
        :rtype: None
        """
        self.invoke('addMetainfoValues', accession, metainfo, skip_existing_keys, replace_existing_keys)

    def get_metainfo_values_as_strings(self, accessions_list, keys_list):
        """
        Retrieve metainfo values as strings for specific files and metainfo keys.
        The function returns a dictionary.

        :param accessions_list: accessions of the files to retrieve
        :type: accessions: list[str]
        :param keys_list: metainfo keys to retrieve
        :type: keys: list[str]
        :return: a two-level dictionary with the following structure: accession -> key -> value
        :rtype: dict
        """
        return self.invoke('getMetainfoValuesAsStrings', accessions_list, keys_list)

    def get_special_folder(self, name):
        """
        Return the accession of a special folder.

        Available special folders are described in :class:`.SpecialFolders`

        :param name: special folder name
        :type name: str
        :return: accession
        :rtype: str
        :raises: GenestackException: if folder name is unknown
        """
        special_folders = (SpecialFolders.IMPORTED, SpecialFolders.CREATED, SpecialFolders.TEMPORARY,
                           SpecialFolders.UPLOADED)
        if name not in special_folders:
            raise GenestackException("Name '%s' must be one of %s" % (name, ', '.join(special_folders)))
        return self.invoke('getSpecialFolder', name)

    def share_files(self, accessions, group, destination_folder=None, password=None):
        """
        Share files.

        :param accessions: files accessions
        :type accessions: list
        :param group: accession of the group to share the files with
        :type group: str
        :param destination_folder: folder in which to link the shared files. No links are created if ``None``.
        :type destination_folder: str
        :param password: password for sharing.
            If not specified, will be asked in an interactive prompt (if supported)
        :type: str
        :rtype: None
        """
        SudoUtils(self.connection).ensure_sudo_interactive(password)
        share_utils = self.connection.application('genestack/shareutils')
        share_utils.invoke('shareFilesForViewing', accessions, [group])
        if destination_folder is not None:
            share_utils.invoke('linkFiles', accessions, destination_folder, group)

    def get_groups_to_share(self):
        """
        Returns a dictionary of the form ``group_accession: group_name``.

        :return: group dict
        :rtype: dict

        """
        share_utils = self.connection.application('genestack/shareutils')
        return share_utils.invoke('getGroupsToShare')

    def get_group_folder_info(self, group_accession):
        """
        Return dictionary with information about group folder.
        It has two keys: ``name`` (name of the group) and ``accession`` (accession of the group folder).

        :param group_accession: group accession
        :type group_accession: str
        :return: dictionary with keys ``name`` (name of the group) and ``accession`` (accession of the group folder)
        :rtype: dict
        """
        share_utils = self.connection.application('genestack/shareutils')
        return share_utils.invoke('getGroupFolderInfo', group_accession)

    def get_folder(self, parent, *names, **kwargs):
        """
        Finds path recursively. As first argument it accepts any existing folder accession.
        For each path in path corresponding folder founded.  If folder is not found exception raised,
        except key ``create=True`` specified. In that case all folders will be created.

        :param parent: parent accession
        :type parent: str
        :param names: tuple of folder names that should be found/created
        :type names: tuple
        :param created: set True if missed folder should be created. Default is False
        :type created: bool
        :return: accession of last folder in paths.
        :rtype: str
        :raises:  GenestackException: when paths are not specified or parent cannot be found.
        """
        if not names:
            raise GenestackException("At least one path should be specified")

        create = bool(kwargs.get('create'))
        for path in names:
            if create:
                parent = self.find_or_create_folder(path, parent=parent)
            else:
                _parent_accession = self.find_file_by_name(path, parent=parent, file_class=self.FOLDER)
                if _parent_accession is None:
                    raise Exception('Cant find folder with name "%s" in folder with accession: %s' % (path, parent))
                parent = _parent_accession
        return parent

    def get_home_folder(self):
        """
        Return the accession of the current user's home folder.

        :return: accession of home folder
        :rtype: str
        """
        return 'private'

    def get_public_folder(self):
        """
        Return the accession of the ``Public`` folder on the current Genestack instance.

        :return: accession of ``Public`` folder
        :rtype: str
        """
        return 'public'

    def get_complete_infos(self, accession_list):
        """
        Returns a list of dictionaries with complete information about each of the specified files.
        This will return an error if any of the accessions is not valid.
        The order of the output list is the same as the order of the accessions input list.

        The information dictionaries have the following structure:

            - accession
            - kind
            - owner
            - name
            - typeKey
            - application

                - id
                - name

            - initializationStatus

                - displayString
                - isError
                - id

            - permissionsByGroup (the value for each key is a dictionary with group accessions as keys)

                - displayStrings
                - groupNames
                - ids

            - time

                - fileCreation
                - initializationQueued
                - initializationStart
                - initializationEnd
                - fileCreation
                - lastMetainfoModification


        :param accession_list: list of valid accessions.
        :type accession_list: list
        :return: list of file info dictionaries.
        :rtype: list
        """
        return self.invoke('getCompleteInfos', accession_list)

    def get_infos(self, accession_list):
        """
        Returns a list of dictionaries with information about each of the specified files.
        This will return an error if any of the accessions is not valid.
        The order of the returned list is the same as the one of the accessions list.

        The information dictionaries have the following structure:

            - accession
            - owner
            - name
            - application

                - id

            - initializationStatus

                - isError
                - id

            - permissionsByGroup (the value for each key is a dictionary with group accessions as keys)

                - groupNames
                - ids

            - time

                - fileCreation
                - initializationQueued
                - initializationStart
                - initializationEnd
                - fileCreation
                - lastMetainfoModification


        :param accession_list: list of valid accessions.
        :type accession_list: list
        :return: list of file info dictionaries.
        :rtype: list[dict[str, object]]
        """
        return self.invoke('getInfos', accession_list)

    def rename_file(self, accession, name):
        """
        Rename a file.

        :param accession: file accession
        :type accession: str
        :param name: name
        :type name: str
        :rtype: None
        """
        self.invoke('renameFile', accession, name)

    def mark_for_tests(self, app_file):
        """
        Mark Genestack file as test one by adding corresponding key to metainfo.
        Test file will calculate md5 checksums of its encapsulated physical files
        during initialization.

        :param app_file: accession of file
        :return: None
        """
        metainfo = Metainfo()
        metainfo.add_boolean(CALCULATE_CHECKSUMS_KEY, True)
        self.add_metainfo_values(app_file, metainfo)

    def mark_obsolete(self, accession):
        """
        Mark Genestack file as obsolete one by adding corresponding key to metainfo.

        :param accession: accession of file
        :return: None
        """
        metainfo = Metainfo()
        metainfo.add_boolean('genestack:obsolete', True)
        self.add_metainfo_values(accession, metainfo)

    def add_checksums(self, app_file, expected_checksums):
        """
        Add expected MD5 checksum to the metainfo of a CLA file.
        Expected checksums are calculated in the following way:

            - The number of checksums equals number of entries in storage.
              For instance, a Reference Genome file has 2 entries (annotation and sequence files).
            - If there are multiple files in one entry, they will be concatenated in the same order
              as they were ``PUT`` to storage by the initialization script.
            - If a file is marked for testing, then after initialization its metainfo
              will contain both expected and actual checksum values.

        :param app_file: accession of application file
        :param expected_checksums: collection of MD5 checksums
        :return: None
        """
        metainfo = Metainfo()
        for key, value in expected_checksums.items():
            metainfo.add_string('%s%s' % (EXPECTED_CHECKSUM_PREFIX, key), value)
        self.add_metainfo_values(app_file, metainfo)

    def create_sample(self, parent=None, name=None, metainfo=None):
        """
        Create a report file with type ``sample``.
        ``name`` is a required field
        It can be specified through the arguments or
        via a :py:class:`~genestack_client.Metainfo` instance.

        Returns file info dictionary with the same structure as dictionaries
        returned by :py:meth:`~genestack_client.FilesUtil.get_infos` method.

        :param parent: accession of parent folder
            (if not provided, files will be created in
            the :py:data:`SpecialFolders.CREATED <genestack_client.SpecialFolders.CREATED>` folder)
        :type parent: str
        :param name: name of the file
        :type name: str
        :param metainfo: metainfo object
        :type metainfo: Metainfo
        :return: file info dictionary
        :rtype: dict
        """
        metainfo = metainfo or Metainfo()
        name and metainfo.add_string(Metainfo.NAME, name)
        return self.invoke('create', 'sample', metainfo, parent)

    def create_study(self, parent=None, name=None, metainfo=None):
        """
        Create a report file with type ``study``.
        ``name`` is a required field
        It can be specified through the arguments or
        via a :py:class:`~genestack_client.Metainfo` instance.

        Returns file info dictionary with the same structure as dictionaries
        returned by :py:meth:`~genestack_client.FilesUtil.get_infos` method.

        :param parent: accession of parent folder
            (if not provided, files will be created in
            the :py:data:`SpecialFolders.CREATED <genestack_client.SpecialFolders.CREATED>` folder)
        :type parent: str
        :param name: name of the file
        :type name: str
        :param metainfo: metainfo object
        :type metainfo: Metainfo
        :return: file info dictionary
        :rtype: dict
        """
        metainfo = metainfo or Metainfo()
        name and metainfo.add_string(Metainfo.NAME, name)
        return self.invoke('create', 'study', metainfo, parent)

    def __find_files(self, type, parent, name, metainfo, offset, limit):
        if offset < 0:
            raise GenestackException('Expected nonnegative offset, got %d' % offset)
        if limit < 1 or limit > MAX_SEARCH_LIMIT:
            raise GenestackException('Expected limit to be >0 and <=%d, got %d' % (MAX_SEARCH_LIMIT, limit))

        metainfo = metainfo or Metainfo()
        name and metainfo.add_string(Metainfo.NAME, name)

        params = {
            'type': type,
            'metainfo': metainfo,
            'offset': offset,
            'limit': limit,
            'parentAccession': parent
        }

        return self.invoke('find', params)

    def find_samples(self, parent=None, name=None, metainfo=None, offset=0, limit=MAX_SEARCH_LIMIT):
        """
        Search samples by name and metainfo.
        Searches only in ``parent`` folder if provided, otherwise everywhere.

        Returns a list of dictionaries with complete information about each of the specified files.
        Dictionaries have the same structure as dictionaries
        returned by :py:meth:`~genestack_client.FilesUtil.get_infos` method.

        :param parent: accession of parent folder
            (if not provided, files will be searched in all folders)
        :type parent: str
        :param name: file name (optional)
        :type name: str
        :param metainfo: metainfo attributes to build search query
        :type metainfo: Metainfo
        :param offset: offset to start retrieving samples. Must be >= 0
        :type offset: int
        :param limit: maximum number of files to retrieve. Must be <= 100.
        :type limit: int
        :return: list of file info dictionaries
        :rtype: list
        """
        return self.__find_files('sample', parent, name, metainfo, offset, limit)

    def find_studies(self, parent=None, name=None, metainfo=None, offset=0, limit=MAX_SEARCH_LIMIT):
        """
        Search studies by name and metainfo.
        Searches only in ``parent`` folder if provided, otherwise everywhere.

        Returns a list of dictionaries with complete information about each of the specified files.
        Dictionaries have the same structure as dictionaries
        returned by :py:meth:`~genestack_client.FilesUtil.get_infos` method.

        :param parent: accession of parent folder
            (if not provided, files will be searched in all folders)
        :type parent: str
        :param name: file name (optional)
        :type name: str
        :param metainfo: metainfo attributes to build search query
        :type metainfo: Metainfo
        :param offset: offset to start retrieving samples. must be >= 0
        :type offset: int
        :param limit: maximum number of files to retrieve. Must be <= 100.
        :type limit: int
        :return: list of file info dictionaries
        :rtype: list
        """
        return self.__find_files('study', parent, name, metainfo, offset, limit)

    def get_metainfo(self, accession):
        """
        Get file metainfo dictionary.
        Returns dictionary that maps metainfo keys to lists of dictionaries with the following fields:

            - Metainfo value type
            - Metainfo value

        Example dictionary::

            {
                'key1': [
                    {
                        'type': 'string',
                        'value': 'value1'
                    },
                    {
                        'type': 'string',
                        'value': 'value2'
                    }
                ]
            }

        :param accession: file accession
        :type accession: str
        :return: file metainfo dictionary
        :rtype: dict[str, list[dict[str, object]]]
        """
        return self.invoke('getMetainfo', accession)

    def add_metainfo(self, accession, metainfo):
        """
        Add metainfo to a specified file.

        :param accession: file accession
        :type accession: str
        :param metainfo: metainfo to add
        :type metainfo: Metainfo
        :rtype: None
        """
        self.invoke("addMetainfoValues", accession, metainfo)

    def replace_metainfo(self, accession, metainfo):
        """
        Replaces metainfo values for specified file. Only the keys present in ``metainfo`` are affected, other keys
        remain the same.

        :param accession: file accession
        :type accession: str
        :param metainfo: metainfo to replace
        :type metainfo: Metainfo
        :rtype: None
        """
        self.invoke("replaceMetainfoValues", accession, metainfo)

    def remove_metainfo_key(self, accession, key):
        """
        Delete a key from the metainfo of specified file.

        :param accession: file accession
        :type accession: str
        :param key: metainfo key
        :type key: str
        :rtype: None
        """
        self.invoke("removeMetainfoKey", accession, key)

    def remove_metainfo_keys(self, accession, keys):
        """
        Delete multiple keys from the metainfo of specified file.

        :param accession: file accession
        :type accession: str
        :param keys: list of metainfo keys
        :type keys: list
        :rtype: None
        """
        self.invoke("removeMetainfoKeys", accession, keys)
