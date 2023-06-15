# ///////////////////////////////////////////////////////////////////////////////
# FILE: database_setup.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-15
# MODIFIED: 2023-06-15
# PURPOSE: initialise data
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from erns.utils.molgenis2 import Molgenis
from erns.utils.utils import flattenDataset
from datatable import dt, f, as_type
from dotenv import load_dotenv
from os import environ
load_dotenv()

ernskin = Molgenis(environ['ERRAS_PROD_HOST'])
ernskin.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])

# ///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Create empty records

# init components reference dataset
componentsDT = dt.Frame([
  {
    'name': 'age',
    'label': 'Age at ...',
    'description': 'Age at ...',
    'type': 'column chart'
  },
  {
    'name': 'enrolment',
    'label': 'Enrolment by thematic disease group',
    'description': 'Number of patients per disease group (see erras_diseasegroup)',
    'type': 'table'
  },
  {
    'name': 'sex',
    'label': 'Sex at birth',
    'description': 'Number of patients by reported sex at birth',
    'type': 'pie chart'
  }
])

ernskin.importDatatableAsCsv('stats_components', componentsDT)

# ~ 1a ~
# create disease groups
groupsDT = dt.Frame(
    flattenDataset(
        data=ernskin.get('erras_diseasegroup'),
        columnPatterns='id|value'
    )
)[:, {'id': f.id, 'label': f.value}]

groupsDT['value'] = 0
groupsDT[:, dt.update(id=as_type(f.id, dt.Type.int32))]
groupsDT['valueOrder'] = groupsDT[:, f.id-1]
groupsDT['id'] = groupsDT[:, 'enrollment-' + f.id]
groupsDT['component'] = 'enrolment'

ernskin.importDatatableAsCsv('stats_stats', groupsDT)


# ~ 1b ~
# set age groups as defined by the project guidelines
ageDT = dt.Frame([
    {'label': 'Newborn', 'description': '0-3 months'},
    {'label': 'Infant', 'description': '3-12 months'},
    {'label': 'Todler', 'description': '1-5 years'},
    {'label': 'Kids', 'description': '5-13 years'},
    {'label': 'Teenagers', 'description': '13-18 years'},
    {'label': 'Adults group 1', 'description': '18-40 years'},
    {'label': 'Adults group 2', 'description': '40-60 years'},
    {'label': 'Elderly persons', 'description': '60+'},
])

ageDT[['id', 'valueOrder']] = range(0, ageDT.nrows)
ageDT['value'] = 0
ageDT['id'] = ageDT[:, 'age-group-' + f.id]
ageDT['component'] = 'age'

ernskin.importDatatableAsCsv('stats_stats', ageDT)

# ~ 1c ~
# create sexAtBirth categories based on project guidelines

sexDT = dt.Frame(ernskin.get('erras_codebook1_sex'))[:, {'label': f.value_en}]
sexDT['id'] = dt.Frame([
    f"sex-{value.lower()}"
    for value in sexDT['label'].to_list()[0]
])

sexDT['value'] = 0
sexDT['valueOrder'] = range(0, sexDT.nrows)
sexDT['component'] = 'sex'

ernskin.importDatatableAsCsv('stats_stats',sexDT)
