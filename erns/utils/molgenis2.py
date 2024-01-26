# '////////////////////////////////////////////////////////////////////////////
# ' FILE: molgenis2.py
# ' AUTHOR: David Ruvolo
# ' CREATED: 2022-07-28
# ' MODIFIED: 2022-11-10
# ' PURPOSE: molgenis.client extensions for DataTable
# ' STATUS: stable
# ' PACKAGES: molgenis-py-client >= 2.4.0
# ' COMMENTS: NA
# '////////////////////////////////////////////////////////////////////////////

from os.path import abspath, getsize
import tempfile
import csv
import mimetypes
import json
import numpy as np
import molgenis.client as molgenis

from erns.utils.utils import print2


class Molgenis(molgenis.Session):
    """Molgenis client extensions"""

    def __init__(self, *args, **kwargs):
        super(Molgenis, self).__init__(*args, **kwargs)
        self.api_file_import = f"{self._root_url}plugin/importwizard/importFile"

    def _dt_to_csv(self, path, datatable):
        """Write datatable object to csv

        :param path: location to save the file
        :type path: str

        :param data: dataset to save
        :type data: datatable
        """
        data = datatable.to_pandas().replace({np.nan: None})
        data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)

    def import_dt(self, pkg_entity: str, data):
        """Import datatable object as a CSV file

        :param pkg_entity: the identifier of a table in EMX format (package_entity)
        :type pkg_entity: str

        :param data: the dataset to import
        :type data: datatable

        :param label: a description to print (e.g., table name)
        :type label: str

        :returns: response
        :rtype: response
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = f"{tmp_dir}/{pkg_entity}.csv"
            self._dt_to_csv(file_path, data)

            with open(abspath(file_path), 'r') as file:
                response = self._session.post(
                    url=self.api_file_import,
                    headers=self._headers.token_header,
                    files={'file': file},
                    params={
                        'action': 'add_update_existing',
                        'metadataAction': 'ignore'
                    }
                )

                if (response.status_code // 100) != 2:
                    print2('Failed to import data into', pkg_entity,
                           '(', response.status_code, ')')
                else:
                    print2('Imported data into', pkg_entity)

                file.close()
            return response

    def import_file(self, file):
        """Import a file into Molgenis
        Import a file (pdf, txt, docx, etc.) into the files table. Content type
        and size is automatically determined.

        @param file location and name of the file to import

        @section

        If the file was successfully imported, you will receive information about
        the file and the location in the database. Use the file identifier to set
        additional permissions. This can be done using the molgenis commander.

        ```zsh
        mcmd config set host
        mcmd give \ 
        --user <user> <read|view|write|...> \
        --entity <file-identifier-in-database> \
        --package sys_FileMeta
        ```

        @return a status message with import metadata
        """
        with open(file, 'rb') as stream:
            data = stream.read()
            stream.close()

        headers = self._headers.token_header
        headers['x-molgenis-filename'] = file
        headers['Content-Type'] = mimetypes.guess_type(file)[0]
        headers['Content-Size'] = str(getsize(file))

        url = f"{self._root_url}api/files"
        response = self._session.post(
            url=url,
            headers=headers,
            data=data
        )

        if response.status_code // 100 == 2:
            result = json.loads(response.text)
            print(response.status_code)
            print(result)
            return response
        else:
            print(f"Failed to import {file}")
            print(response.status_code)
            return response
