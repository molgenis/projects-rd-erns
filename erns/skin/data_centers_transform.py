"""Transform centers and prepare for import
FILE: data_centers_transform.py
AUTHOR: David Ruvolo
CREATED: 2023-02-22
MODIFIED: 2023-02-27
PURPOSE: clean reference centers dataset
STATUS: stable
PACKAGES: **see below**
COMMENTS: NA
"""
from os import environ, path
from tqdm import tqdm
import pandas as pd
from datatable import dt, f
from dotenv import load_dotenv
from erns.utils.molgenis2 import Molgenis
from erns.utils.ror import RorClient
load_dotenv()

# start Molgenis session
db = Molgenis(environ['ERRAS_PROD_HOST'])
db.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])

ror = RorClient()

centersPD = pd.read_excel('data/ern_skin_reference_centers.xlsx')
centersDT = dt.Frame(centersPD)

# create ID
centersDT['id'] = range(0, centersDT.nrows, 1)
centersDT['id'] = dt.Frame([
    f"erras-{num}" for num in range(0, centersDT.nrows, 1)
])

# isolate ROR identifier
centersDT['code'] = dt.Frame([
    path.basename(value) if value else value
    for value in centersDT['iri'].to_list()[0]
])

centersDT['codesystem'] = 'ROR'

# retrieve center locations
rorCodes = centersDT['code'].to_list()[0]
for code in tqdm(rorCodes):
    response = ror.get_organisation_by_id(code=code)
    if response:

        address = response['addresses'][0] if response.get(
            'addresses') else None
        country = response['country'] if response.get('country') else None

        centersDT[f.code == code, 'officialName'] = response.get('name')
        centersDT[f.code == code, 'latitude'] = address.get(
            'lat') if address else None
        centersDT[f.code == code, 'longitude'] = address.get(
            'lng') if address else None
        centersDT[f.code == code, 'city'] = address.get(
            'city') if address else None
        centersDT[f.code == code, 'country'] = country.get(
            'country_name') if country else None

    del response, address, country


db.import_dt(pkg_entity='ernstats_dataproviders', data=centersDT)
