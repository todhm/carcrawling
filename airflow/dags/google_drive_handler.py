import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload
import gspread
import pandas as pd
from datetime import datetime as dt
import re
import os


class GoogleDriveHandler(object):

    def __init__(self):
        store = file.Storage('/usr/local/airflow/dags/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            scope = 'https://www.googleapis.com/auth/drive'
            flow = client.flow_from_clientsecrets(
                '/usr/local/airflow/dags/credentials.json', scope)
            creds = tools.run_flow(flow, store)
        self.service = build('drive', 'v3', http=creds.authorize(Http()))
        

    def upload_excelfile_with_path(self,file_path,df,company_folder_id):
        excel_file_name = file_path[2:]
        df.to_excel(file_path, index=False)
        file_metadata = {
            'name': excel_file_name,
            'parents': [company_folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }

        media = MediaFileUpload(file_path,
                                mimetype='text/xlsx',
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media, fields='id').execute()
        try:
            os.remove(file_path)
            spread_id = file.get('id')
            return spread_id
        except Exception as e:
            print(str(e))

    def upload_multisheet_excel(self,file_path,data_dict,company_folder_id,columns_dict=None):
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

        for key in data_dict:
            df = pd.DataFrame(data_dict[key])
            if columns_dict:
                df = df[columns_dict[key]]
            df.to_excel(writer, sheet_name=key)
            

        writer.save()
        excel_file_name = file_path[2:]
        
        file_metadata = {
            'name': excel_file_name,
            'parents': [company_folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }

        media = MediaFileUpload(file_path,
                                mimetype='text/xlsx',
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media, fields='id').execute()
        try:
            os.remove(file_path)
            spread_id = file.get('id')
            return spread_id
        except Exception as e:
            print(str(e))
            return False 


    def upload_data(self, data_list,filename):
        folder_id = '1t7nLxB2rVV_2DaWlIbrNtUDuNNjmFQAV'
        file_path = './' + file_name + ".xlsx"
        spread_id = self.upload_excelfile_with_path(file_path,df,company_folder_id)

        return spread_id


if __name__ == "__main__":

    print(123)
