"""Organistations Prep

FILE: organisations_prep.py
AUTHOR: David Ruvolo
CREATED: 2023-08-01
MODIFIED: 2024-01-26
PURPOSE: pull organisations metadata and transform
STATUS: stable
PACKAGES: **see below**
COMMENTS: NA
"""

from os import environ
from datatable import dt, f
from dotenv import load_dotenv
from erns.utils.utils import flatten_data
from erns.utils.molgenis2 import Molgenis
load_dotenv()

db = Molgenis(environ['CRANIO_PROD_HOST'])
db.login(environ['CRANIO_PROD_USR'], environ['CRANIO_PROD_PWD'])

# get project-organisations data
projects = db.get("organisations_projects")
projectsDT = dt.Frame(flatten_data(data=projects, col_patterns="code"))

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
projectsDT['id'] = projectsDT[:, (f.code)]
projectsDT['hasSubmittedData'] = False
projectsDT['displayName'] = projectsDT[:, (f.projectName)]
projectsDT['codesystem'] = "ROR"

db.import_dt("ernstats_dataproviders", projectsDT)
