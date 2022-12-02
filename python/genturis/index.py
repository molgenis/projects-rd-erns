#///////////////////////////////////////////////////////////////////////////////
# FILE: index.py
# AUTHOR: David Ruvolo
# CREATED: 2022-12-02
# MODIFIED: 2022-12-02
# PURPOSE: misc script for genturis-registry
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from python.utils.molgenis2 import Molgenis
from dotenv import load_dotenv
from os import environ
import pandas as pd
from datatable import dt
load_dotenv()

genturisPROD = Molgenis(environ['GENTURIS_PROD_HOST'])
genturisPROD.login(environ['GENTURIS_PROD_USR'], environ['GENTURIS_PROD_PWD'])

genturisACC = Molgenis(environ['GENTURIS_ACC_HOST'])
genturisACC.login(environ['GENTURIS_ACC_USR'], environ['GENTURIS_ACC_PWD'])

# ~ 0 ~
# Import data providers xlsx

dataproviders = dt.Frame(pd.read_excel('data/ern_genturis_dataproviders.xlsx'))

genturisPROD.delete('ernstats_dataproviders')
genturisACC.delete('ernstats_dataproviders')

genturisPROD.importDatatableAsCsv('ernstats_dataproviders', dataproviders)
genturisACC.importDatatableAsCsv('ernstats_dataproviders', dataproviders)

genturisPROD.logout()
genturisACC.logout()