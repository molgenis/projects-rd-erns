"""Read Organisations xlsx and write data to json"""

import json
import pandas as pd

if __name__ == '__main__':
    data = pd.read_excel(
        'erns/cranio/cranio_emx2.xlsx',
        sheet_name='organisations'
    )

    with open('erns/cranio/cranio_organisations.json', 'w', encoding='utf-8') as file:
        data_selection = data[['name', 'schemaName']].to_dict('records')
        json.dump(data_selection, file, ensure_ascii=False, indent=4)
        file.close()
