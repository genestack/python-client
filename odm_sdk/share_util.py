import collections

from odm_sdk import Application

try:
    collectionsAbc = collections.abc
except AttributeError:
    collectionsAbc = collections


class ShareUtil(Application):
    """
    Application that acts as a facade for sharing-related operations.
    """
    APPLICATION_ID = 'genestack/shareutils'
    SHARE_FOLDER_LIMIT = 100

    class Permissions(object):
        """
        Supported permission values that can be used in :meth:`ShareUtil.share_files` and
        :meth:`ShareUtil.share_folder` methods.

        .. attribute:: VIEW

            Allows finding files via search and reading files' content

        .. attribute:: EDIT

            Allows finding files via search, reading files' content and modifying files' metainfo

        .. attribute:: SHARE

            Allows finding files via search, reading files' content and sharing them with other
            groups. This permissions type only allows sharing by group members from the same
            organization as the file owner. When sharing, non-owners are only allowed to set
            permissions that are the same or narrower that they currently have for the given file.

        """
        VIEW = "VIEW"
        EDIT = "EDIT"
        SHARE = "SHARE"

    def share_files_for_view(self, file_accessions, group_accession, destination_folder=None):
        """
        Share files with viewing permissions. Viewing permissions include finding the shared files
        and running tasks that access their content.

        This method is equivalent to calling :meth:`share_files` method with
        :attr:`ShareUtil.Permissions.VIEW` permission.

        :param file_accessions: accession or an iterable of accessions of files to be shared
        :type file_accessions: str | collections.Iterable[str]
        :param group_accession: accession of the group to share the files with
        :type group_accession: str
        :param destination_folder: accession of the folder to link shared files into. Typically
                                   this parameter should be used for linking files into group
                                   folders, which is currently impossible to do using the
                                   :meth:`FilesUtil.link_file` method. No links will be created if
                                   this parameter is equal to `None`.
        :type destination_folder: str
        """
        self.share_files(
            file_accessions, group_accession, [ShareUtil.Permissions.VIEW], destination_folder
        )

    def share_files_for_edit(self, file_accessions, group_accession, destination_folder=None):
        """
        Share files with editing permissions. Editing permissions include viewing permissions and
        also allow modifying metainfo and linking/unlinking files (only applicable to containers
        and datasets).

        This method is equivalent to calling :meth:`share_files` method with
        :attr:`ShareUtil.Permissions.EDIT` permission.

        :param file_accessions: accession or an iterable of accessions of files to be shared
        :type file_accessions: str | collections.Iterable[str]
        :param group_accession: accession of the group to share the files with
        :type group_accession: str
        :param destination_folder: accession of the folder to link shared files into. Typically
               this parameter should be used for linking files into group folders, which is
               currently impossible to do using the :meth:`FilesUtil.link_file` method. No links
               will be created if this parameter is equal to `None`.
        :type destination_folder: str
        """
        self.share_files(
            file_accessions, group_accession, [ShareUtil.Permissions.EDIT], destination_folder
        )

    def share_files(self, file_accessions, group_accession, permissions, destination_folder=None):
        """
        Share files with the given permissions with the given groups. Available permission values
        are listed in the :class:`ShareUtil.Permissions` class.

        :param file_accessions: accession or an iterable of accessions of files to be shared
        :type file_accessions: str | collections.Iterable[str]
        :param group_accession: accession of the group to share the files with
        :type group_accession: str
        :param permissions: permissions that should be assigned to the provided files. Must consist
               of :class:`ShareUtil.Permissions` values
        :type permissions: str | collections.Iterable[str]
        :param destination_folder: accession of the folder to link shared files into. Typically
               this parameter should be used for linking files into group folders, which is
               currently impossible to do using the :meth:`FilesUtil.link_file` method. No links
               will be created if this parameter is equal to `None`
        :type destination_folder: str

        :raises GenestackServerException: if some of the given files cannot be shared by the current
                user (i.e. he doesn't own them or doesn't have the
                :attr:`ShareUtil.Permissions.SHARE` permission).
        """
        permissions = self.__to_list(permissions)
        self.__share(
            file_accessions, group_accession, destination_folder, 'shareFiles', permissions
        )

    def safe_share_files(
            self, file_accessions, group_accession, permissions, destination_folder=None
    ):
        """
        Same as :meth:`share_files` but does not throw an exception in case some of the given files
        cannot be shared (i.e. the current user doesn't own them or doesn't have the
        :attr:`ShareUtil.Permissions.SHARE` permission).

        :param file_accessions: accession or an iterable of accessions of files to be shared
        :type file_accessions: str | collections.Iterable[str]
        :param group_accession: accession of the group to share the files with
        :type group_accession: str
        :param permissions: permissions that should be assigned to the provided files. Must consist
               of :class:`ShareUtil.Permissions` values
        :type permissions: str | collections.Iterable[str]
        :param destination_folder: accession of the folder to link shared files into. Typically
               this parameter should be used for linking files into group folders, which is
               currently impossible to do using the :meth:`FilesUtil.link_file` method. No links
               will be created if this parameter is equal to `None`
        :type destination_folder: str
        """
        permissions = self.__to_list(permissions)
        self.__share(
            file_accessions, group_accession, destination_folder, 'safeShareFiles', permissions
        )

    def __share(
            self, file_accessions, group_accession, destination_folder, method, *args
    ):
        file_accessions = self.__to_list(file_accessions)
        self.invoke(method, file_accessions, [group_accession], *args)
        if destination_folder is not None:
            self.invoke('linkFiles', file_accessions, destination_folder, group_accession)

    def share_folder(self, folder_accession, group_accession, permissions, destination_folder=None):
        """
        Recursively share the given folder, its subfolders and files inside them. Files that
        cannot be shared by the current user will be skipped.

        This method is useful for sharing folders with a lot of files because calling
        :meth:`share_files` may result in a timeout. This method shares files in chunks and may take
        significant time to complete.

        :param folder_accession: accession of the folder
        :type folder_accession: str
        :param group_accession: accession of the group to share the files with
        :type group_accession: str
        :param permissions: permissions that should be assigned to the provided files. Must consist
               of :class:`ShareUtil.Permissions` values
        :type permissions: str | collections.Iterable[str]
        :param destination_folder: accession of the folder to link shared files into. Typically
               this parameter should be used for linking files into group folders, which is
               currently impossible to do using the :meth:`FilesUtil.link_file` method. No links
               will be created if this parameter is equal to `None`
        :type destination_folder: str
        """

        # This method makes repeated calls to server, each method call
        # shares chunk of files in the given folder that aren't shared yet with the provided group
        # or ``WORLD``.
        # Due to the indexing lag, same files can be included in different calls. See the
        # `ShareUtilsApplication.shareChunkInFolder` javadoc for details.
        from time import sleep

        permissions = self.__to_list(permissions)

        self.share_files(folder_accession, group_accession, permissions, destination_folder)

        delay_seconds = 1  # delay between attempts

        offset = 0
        while True:
            count = self.invoke(
                'shareChunkInFolder',
                folder_accession, group_accession, permissions, offset, self.SHARE_FOLDER_LIMIT
            )
            if count == 0 and offset == 0:
                return
            if count < self.SHARE_FOLDER_LIMIT:
                sleep(delay_seconds)
                offset = 0
            else:
                offset += self.SHARE_FOLDER_LIMIT

    @staticmethod
    def __to_list(args):
        if isinstance(args, list):
            return args
        is_iterable = isinstance(args, collectionsAbc.Iterable)
        if is_iterable and not isinstance(args, str):
            return list(args)
        else:
            return [args]

    def get_available_sharing_groups(self):
        """
        Find groups that the current user can share files with, which means that he is either
        a sharing user or an administrator of these groups.

        :return: dictionary in format 'group accession' -> 'group name'
        :rtype: dict
        """
        return self.invoke('getGroupsToShare')
