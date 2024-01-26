# ///////////////////////////////////////////////////////////////////////////////
# FILE: index.py
# AUTHOR: David Ruvolo
# CREATED: 2023-05-17
# MODIFIED: 2024-01-26
# PURPOSE: misc emx2 commands
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from os import environ
from csv import QUOTE_ALL
from dotenv import load_dotenv
from datatable import dt, f
import molgenis.client as Emx1
from emx2.api.emx2 import Molgenis as Emx2
load_dotenv()


def to_text_csv(data):
    """DataTable to text/csv
    Convert a datatable object to a text/csv string.

    @param data datatable object

    @return text/csv string
    """
    return data.to_pandas().to_csv(index=False, quoting=QUOTE_ALL, encoding='UTF-8')


# start sessions
emx1 = Emx1.Session(environ['GENTURIS_PROD_HOST'])
emx1.login(environ['GENTURIS_PROD_USR'], environ['GENTURIS_PROD_PWD'])

emx2 = Emx2(url='https://david-emx2.molgeniscloud.org')
emx2.signin(username='admin', password='snazzy-pintail-woo-MOVER')

# ///////////////////////////////////////

# ~ 1 ~
# Import providers

data = dt.Frame(emx1.get('ernstats_dataproviders'))
del data['_href']

# create structure for ontology table
organisations = data.copy()
organisations['name'] = organisations['projectName']

del organisations['projectName']
del organisations['id']
del organisations['displayName']

organisations.names = {
    'databaseID': 'providerIdentifier',
    'iri': 'ontologyTermURI'
}

# create structure for the providers table
providers = organisations[:,
                          (f.providerIdentifier, f.hasSubmittedData, f.name)]
providers.names = {'name': 'organisation'}

del organisations['hasSubmittedData']
del organisations['providerIdentifier']


# import objects
orgs = to_text_csv(organisations).encode('utf-8')
prov = to_text_csv(providers).encode('utf-8')

emx2.importData(
    database='DashboardStats',
    table='organisations',
    data=orgs
)

emx2.importData(
    database='DashboardStats',
    table='dataproviders',
    data=prov
)

# ///////////////////////////////////////


# ~ 2 ~
# Import Stats Data
stats = dt.Frame(emx1.get('ernstats_stats'))
del stats['_href']

# recode component names
stats['component'] = dt.Frame([
    value.replace(
        'table-', '') if value == 'table-enrollment-disease-group' else value
    for value in stats['component'].to_list()[0]
])

components = dt.unique(stats['component'])
components.names = {'component': 'name'}

emx2.importData(
    database='DashboardStats',
    table='components',
    data=to_text_csv(components)
)

emx2.importData(
    database='DashboardStats',
    table='statistics',
    data=to_text_csv(stats).encode('utf-8')
)
