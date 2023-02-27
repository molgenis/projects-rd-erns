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
    
  def ping(self):
    """Ping the ROR service
    Check the status of the REST API
    """
    url = f"{self.api}/heartbeat"
    response = self.GET(url)
    if response.status_code / 100 == 2:
      print(f'ROR is online {response.status_code}')
    else:
      print(f"ROR service may be disrupted ({response.status_code})")
    
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
    
  def getOrganisationById(self, id):
    """Get organisation by ROR ID
    Retrieve metadata about an organisation using a ROR ID. An ID may contain a full URL (`https://ror.org/<id>`), domain + ID (`ror.org/<id>`), or only the ID.
    
    @param id A ROR identifier; either a URL or ID
    
    @return json
    """
    url = f"{self.api}/organizations/{id}"
    response = self.GET(url)
    return response
    