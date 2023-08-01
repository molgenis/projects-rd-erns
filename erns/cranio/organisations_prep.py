#///////////////////////////////////////////////////////////////////////////////
# FILE: organisations_prep.py
# AUTHOR: David Ruvolo
# CREATED: 2023-08-01
# MODIFIED: 2023-08-01
# PURPOSE: pull organisations metadata and transform
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from erns.utils.utils import flattenDataset
from erns.utils.molgenis2 import Molgenis
from datatable import dt, f
from dotenv import load_dotenv
from os import environ
load_dotenv()

db = Molgenis(environ['CRANIO_PROD_HOST'])
db.login(environ['CRANIO_PROD_USR'], environ['CRANIO_PROD_PWD'])

# get project-organisations data
projects = db.get("organisations_projects")
projectsDT = dt.Frame(
  flattenDataset(
    data = projects,
    columnPatterns="code"
  )
)

# get ROR orgs metdata
organisations = db.get("organisations_organisations")
orgsDT = dt.Frame(organisations)
del orgsDT['_href']


# merge organistations with projects
projectsDT.names = {"organisation": "code"}
projectsDT.key = "code"
orgsDT.key = "code"
projectsDT = projectsDT[:, :, dt.join(orgsDT)]


projectsDT.names = {
  "identifier": "databaseID",
  "name": "projectName",
  "uri": "iri",
  "name.0": "officialName"
}

# init additional columns
projectsDT[:, dt.update(
  id=f.code,
  hasSubmittedData=False,
  displayName=f.projectName,
  codesystem="ROR",  
)]

db.importDatatableAsCsv("ernstats_dataproviders", projectsDT)
