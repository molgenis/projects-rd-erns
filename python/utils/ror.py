#'////////////////////////////////////////////////////////////////////////////
#' FILE: ror.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-06-17
#' MODIFIED: 2022-11-30
#' PURPOSE: ROR REST API Client
#' STATUS: stable
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import requests
import urllib.parse

class RorClient:
  def __init__(self):
    self.session = requests.Session()
    self.api = 'https://api.ror.org'
    
  def GET(self, url, **kwargs):
    response = self.session.get(url, **kwargs)
    response.raise_for_status()
    if 'errors' in response:
      raise print('Error in request', str(response['errors']))
    return response.json()
    
  def searchOrganizations(self, query):
    """Search Organizations
    
    @param query String containing search query and or filters
    
    @references https://ror.readme.io/docs/rest-api
    @return record set
    """
    q = urllib.parse.quote(query)
    url = f"{self.api}/organizations?query={q}"
    response = self.GET(url)
    
    print('Found', response.get('number_of_results'), 'records')
    return response.get('items')