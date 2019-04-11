import os 
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, Car,Auction,insert_auction_car_list
from models.dao import CarAuctionDao
from glovis_data_handler import GlovisDataHandler
from google_drive_handler import GoogleDriveHandler
from google_spread_handler import GoogleSpreadHandler
from datetime import datetime as dt
from unittest import  mock
import contextlib
from sqlalchemy import MetaData

test_url = os.environ.get("POSTGRES_SERVICE_TEST_URL")
car_data_list = [
            {
                'car_brand':'현대',
                'auction_id':1,
                'car_name':"소나타",
                'year':2017, 
                'transmission':'자동', 
                'fuel_type':'디젤',
                'engine_size':1999, 
                'kilos':0, 
                'car_color':'blue', 
                'car_img_src':'hello.jpg', 
                'car_loc':'시화', 
                'auction_car_id':350, 
                'car_type':'법인', 
                'car_owner':'법인', 
                'car_reputation':'A/5', 
                'car_auction_start_price':15000000
            },
            {
                'car_brand':'현대',
                'auction_id':1,
                'car_name':"소나타",
                'year':2017, 
                'transmission':'자동', 
                'fuel_type':'디젤',
                'engine_size':1999, 
                'kilos':0, 
                'car_color':'blue', 
                'car_img_src':'hello.jpg', 
                'car_loc':'시화', 
                'auction_car_id':351, 
                'car_type':'법인', 
                'car_owner':'법인', 
                'car_reputation':'A/5', 
                'car_auction_start_price':18000000
            }
]

class TestGdh(unittest.TestCase):
    def setUp(self):
        self.gdh = GlovisDataHandler()

    def test_get_last_page_info(self):
        last_dict = self.gdh.get_last_page(loc='bundang')
        self.assertTrue('auction_number'in last_dict.keys())
        self.assertTrue('last_page'in last_dict.keys())
        self.assertTrue('auction_loc'in last_dict.keys())

    def tearDown(self):
        self.gdh.close()
        

class TestQuery(unittest.TestCase):


    def setUp(self):

        self.engine = create_engine(test_url)
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()
        
    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)



    def test_get_cardao_stats(self):
        auction_loc = car_data_list[0]['car_loc']
        auction_number = car_data_list[0]['auction_id']
        insert_auction_car_list(car_data_list,self.session)
        car_data_stats = CarAuctionDao.car_auction_stats(self.session,auction_number,auction_loc)
        self.assertEqual(car_data_stats[0]['car_count'] ,2)
        self.assertEqual(car_data_stats[0]['average_car_price'] ,16500000)
        self.assertEqual(car_data_stats[0]['max_car_price'] ,18000000)
        self.assertEqual(car_data_stats[0]['min_car_price'] ,15000000)
        self.assertEqual(car_data_stats[0]['average_car_kilos'] ,0)


    def test_get_carauction_list(self):
        auction_loc = car_data_list[0]['car_loc']
        auction_number = car_data_list[0]['auction_id']
        insert_auction_car_list(car_data_list,self.session)
        car_auction_data_list = CarAuctionDao.get_specific_car_auction_data(self.session,auction_number,auction_loc)
        self.assertEqual(len(car_auction_data_list),2)


    def test_upsert_cars(self):
        insert_auction_car_list(car_data_list,self.session)
        insert_auction_car_list(car_data_list,self.session)
        car_list = self.session.query(Car).all()
        auction_list = self.session.query(Auction).all()
        self.assertEqual(len(car_list),2)
        self.assertEqual(len(auction_list),1)
        self.assertEqual(auction_list[0].auction_loc,'시화')







    def test_insert_all(self):
        insert_auction_car_list(car_data_list,self.session)
        car_list = self.session.query(Car).all()
        auction_list = self.session.query(Auction).all()
        self.assertEqual(len(car_list),2)
        self.assertEqual(len(auction_list),1)
        self.assertEqual(auction_list[0].auction_loc,'시화')



class TestDriveHandler(unittest.TestCase):

    def setUp(self):
        file_metadata = {
            'name': 'test_folder',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        self.gdh = GoogleDriveHandler()
        self.service = self.gdh.service
        test_folder = self.gdh.service.files().create(
            body=file_metadata, fields='id').execute()
        self.folder_id = test_folder.get('id')
        
        self.gsh = GoogleSpreadHandler()


    def test_upload_excelfile(self):
        nowdt_string = dt.strftime(dt.now(),"%Y%m%d%H%M%S")+".xlsx"
        file_string = "./cardata_"+nowdt_string
        data={
            "sample_car_data1":car_data_list,
            "sample_car_second":car_data_list,
        }
        key_columns = {
            "sample_car_data1":['car_brand','auction_id','car_name'],
            "sample_car_second":['car_brand','auction_id','car_name'],
        }
        spread_id = self.gdh.upload_multisheet_excel(file_string,data,self.folder_id)
        spread_data = self.gsh.get_upload_file(spread_id)
        worksheet_list = spread_data.worksheets()
        self.assertEqual(len(worksheet_list),len(data.keys()))
        for worksheet_obj in worksheet_list:
            self.assertTrue(worksheet_obj.title in data.keys())
        


        

    

    def tearDown(self):
        self.service.files().delete(fileId=self.folder_id).execute()


if __name__=="__main__":
    unittest.main()