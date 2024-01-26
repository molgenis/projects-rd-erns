"""Interation with the ROR REST API
FILE: ror.py
AUTHOR: David Ruvolo
CREATED: 2022-06-17
MODIFIED: 2024-01-26
PURPOSE: ROR REST API Client
STATUS: stable
PACKAGES: requests
COMMENTS: https://ror.readme.io/docs/rest-api
"""

import urllib.parse
import requests


class RorClient:
    """Interact with the ROR API"""

    def __init__(self):
        self.session = requests.Session()
        self.api = 'https://api.ror.org'

    def _get(self, url, **kwargs):
        """Create a new GET request"""
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        if 'errors' in response:
            raise print('Error in request', str(response['errors']))
        return response.json()

    def _validate_reponse(self, message: str = None, response: dict = None):
        """Validate response from the REST API

        :param message: an error message to display
        :type message: string

        :param response: a response object
        :type response: dict
        """
        if response.status_code / 100 != 2:
            raise requests.exceptions.HTTPError(message, response=response)

    @property
    def ping(self):
        """Check the status of the REST API"""
        url = f"{self.api}/heartbeat"
        response = self._get(url)
        self._validate_reponse('ROR serverice is disrupted', response=response)
        print(f'ROR is online {response.status_code}')

    def search_organizations(self, query):
        """Search for organizations
        :param query: a search query and or filters
        :type query: string

        :return: a response containing one or more organisations
        :rtype: recordset
        """
        q = urllib.parse.quote(query)
        url = f"{self.api}/organizations?query={q}"
        response = self._get(url)
        self._validate_reponse('Unable to retrieve organisations', response)

        print('Found', response.get('number_of_results'), 'records')
        return response.get('items')

    def get_organisation_by_id(self, code):
        """Get organisation by ROR ID
        Retrieve metadata about an organisation using a ROR ID. An ID may contain
        a full URL (`https://ror.org/<id>`), domain + ID (`ror.org/<id>`), or only
        the ID.

        :param code: ROR identifier found in the URL

        :return: information about an organisation
        :rtype: dict
        """
        url = f"{self.api}/organizations/{code}"
        response = self._get(url)
        self._validate_reponse('Unable to retrieve organisation', response)
        return response
