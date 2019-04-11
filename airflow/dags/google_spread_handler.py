import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import gspread
import pandas as pd 


class GoogleSpreadHandler(object):

    def __init__(self):
        store = file.Storage('/usr/local/airflow/dags/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            scope = 'https://www.googleapis.com/auth/drive'
            flow = client.flow_from_clientsecrets('/usr/local/airflow/dags/credentials.json',scope)
            creds = tools.run_flow(flow, store)
        self.client = gspread.authorize(creds)

    def get_dataframe(self,spread_id):
        spread = self.client.open_by_key(spread_id)
        worksheet = spread.get_worksheet(0)
        df = pd.DataFrame(worksheet.get_all_records())
        return df

    def get_upload_file(self,spread_id):
        spread = self.client.open_by_key(spread_id)
        return spread 

