"""Import data into emx2 instance"""

from molgenis_emx2_pyclient import Client
import pandas as pd

URL = ""
WB = "./erns/skin/skin_emx2.xlsx"
TOKEN = ""

# import data from sheets
organisations_df = pd.read_excel(WB, sheet_name="organisations",)
organisations = organisations_df.to_dict('records')

with Client(URL, schema="ErnStats", token=TOKEN) as client:
    client.save_schema(table="Organisations", data=organisations)
