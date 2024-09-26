"""Manage the GENTURIS script
FILE: index.py
AUTHOR: David Ruvolo
CREATED: 2022-12-02
MODIFIED: 2024-07-09
PURPOSE: misc script for genturis-registry
STATUS: stable
PACKAGES: **see below**
COMMENTS: NA
"""

from os import environ, system
import pandas as pd
from datatable import dt
from dotenv import load_dotenv
from erns.utils.molgenis2 import Molgenis
load_dotenv()

genturis_prod = Molgenis(environ['GENTURIS_PROD_HOST'])
genturis_prod.login(environ['GENTURIS_PROD_USR'], environ['GENTURIS_PROD_PWD'])

genturis_acc = Molgenis(environ['GENTURIS_ACC_HOST'])
genturis_acc.login(environ['GENTURIS_ACC_USR'], environ['GENTURIS_ACC_PWD'])

# ///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Manage data providers

# ~ 1a ~
# import new data into prod and acc
dataproviders_df = pd.read_excel('data/ern_genturis_dataproviders.xlsx')
dataproviders = dt.Frame(dataproviders_df)

genturis_prod.delete('ernstats_dataproviders')
genturis_acc.delete('ernstats_dataproviders')

genturis_prod.import_dt('ernstats_dataproviders', dataproviders)
genturis_acc.import_dt('ernstats_dataproviders', dataproviders)

# ~ 1b ~
# Alternatively, transfer datasets between servers

providers = dt.Frame(genturis_prod.get('ernstats_dataproviders'))
del providers['_href']

genturis_acc.import_dt('ernstats_dataproviders', providers)

# move stats dataset between servers
stats = dt.Frame(genturis_prod.get('ernstats_stats'))
del stats['_href']

genturis_acc.delete('ernstats_stats')
genturis_acc.import_dt('ernstats_stats', stats)

# ///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Import files to display on the landing pages

# import into prod and acc
prod_response = genturis_prod.import_file(file='ERN_GENTURIS_User_Manual.pdf')
acc_response = genturis_acc.import_file(file='ERN_GENTURIS_User_Manual.pdf')

# build command: give the role "annonymous" permission to view the file
prod_file_id = prod_response.json()['id']
acc_file_id = acc_response.json()['id']

prod_cmd = f"mcmd give anonymous read --package sys_FileMeta --entity {prod_file_id}"
acc_cmd = f"mcmd give anonymous read --package sys_FileMeta --entity {acc_file_id}"

prod_host = environ['GENTURIS_PROD_HOST'].replace('api', '')
acc_host = environ['GENTURIS_ACC_HOST'].replace('api', '')

# set host and run command in prod and acc
system(f'mcmd config set host {prod_host}')
system(prod_cmd)

system(f'mcmd config set host {acc_host}')
system(acc_cmd)


genturis_prod.logout()
genturis_acc.logout()
