#///////////////////////////////////////////////////////////////////////////////
# FILE: ror.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-15
# MODIFIED: 2023-06-15
# PURPOSE: query ror
# STATUS: stable on.going
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from erns.utils.ror import RorClient

ror = RorClient()

response = ror.getOrganisationById(id='001f7a930')
response['name']

response['addresses'][0].get('city')
response['country']['country_name']

response['addresses'][0].get('lat')
response['addresses'][0].get('lng')