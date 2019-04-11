from datatypes import *
from glovis_data_handler import GlovisDataHandler
from airflow import AirflowException
from log_utils import log_factory
from pymongo import MongoClient 
from models.models import Car,Auction,insert_auction_car_list
from google_drive_handler import GoogleDriveHandler
from models.dao import CarAuctionDao
from models.utils import create_session
from datetime import datetime as dt
import os 


def crawl_glovis_last_page(loc,ds,**kwargs):
    airflow_run_id = kwargs.get('run_id')
    log_data = {}
    log_data['airflowRunId'] = airflow_run_id
    gdh = GlovisDataHandler()
    db_name=os.environ.get('MONGO_DB_NAME')
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    glovis_site_list = db.glovis_site_list
    logger,handler = log_factory(db_name)
    result_dict = gdh.get_last_page(loc)
    if not result_dict: 
        logger.error(CRAWL_GLOVIS_LAST_PAGE,extra=log_data)
        gdh.close()
        raise AirflowException
    if result_dict:
        last_page = result_dict['last_page']
        get_page_list = gdh.parse_page_list(loc,last_page)
        log_data.update(result_dict)
        logger.info(CRAWL_GLOVIS_LAST_PAGE,extra=log_data)
        glovis_site_list.delete_many({})
        glovis_site_list.insert_many(get_page_list)
    handler.destroy()
    client.close()
    return True 
    





def crawl_glovis_page(**kwargs):
    airflow_run_id = kwargs.get('run_id')
    log_data = {}
    log_data['airflowRunId'] = airflow_run_id
    gdh = GlovisDataHandler()
    db_name=os.environ.get('MONGO_DB_NAME')
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    glovis_site_list = db.glovis_site_list
    crawler_log_col = db.crawler_logs
    crawler_logs = list(crawler_log_col.find({
        "message":CRAWL_GLOVIS_PAGE,
        "airflowRunId":airflow_run_id,
        'level':"INFO"
    }))
    crawled_site_list = [ log['site'] for log in crawler_logs]
    site_list = list(glovis_site_list.find())
    site_list = [ site['site'] for site in site_list]
    site_list = set(site_list) - set(crawled_site_list)
    site_list = list(site_list)
    logger,handler = log_factory(db_name)
    for site in site_list:
        car_data_site_list = gdh.get_car_page_data(site)
        log_data['site'] = site
        try:
            session = create_session()
            insert_auction_car_list(car_data_site_list,session)
            session.close()
            logger.info(CRAWL_GLOVIS_PAGE,extra=log_data)
        except Exception as e:
            log_data['errorMessage'] = str(e)
            logger.error(CRAWL_GLOVIS_PAGE,extra=log_data)
    handler.destroy()
    client.close()
    return True 
    


def upload_glovis_spread(**kwargs):
    log_data = {}
    airflow_run_id = kwargs.get('run_id')
    log_data['airflowRunId'] = airflow_run_id
    db_name=os.environ.get('MONGO_DB_NAME')
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    logs = list(db.crawler_logs.find({
        "message":CRAWL_GLOVIS_LAST_PAGE,
        "airflowRunId":airflow_run_id,
        'level':"INFO"
    }))
    parent_google_id = os.environ.get("PARENT_GOOGLE_ID")
    logger,handler = log_factory(db_name)
    google_drive_id = os.environ.get("GOOGLE_DRIVE_ID")

    if logs:
        log_result = logs[0]
        auction_number = log_result['auction_number']
        auction_loc = log_result['auction_loc']
        session = create_session()
        car_auction_data_list = CarAuctionDao.get_specific_car_auction_data(session,auction_number,auction_loc)
        car_auction_stats = CarAuctionDao.car_auction_stats(session,auction_number,auction_loc)
        gdh = GoogleDriveHandler()
        try:
            nowdt_string = dt.strftime(dt.now(),"%Y%m%d%H%M%S")+".xlsx"
            file_string = "./cardata_"+nowdt_string
            data_dict={
                "car_stats":car_auction_stats,
                "total_car_data":car_auction_data_list,
            }
            columns_dict={
                'car_stats':[
                    'car_brand','car_name','car_count',
                    'average_car_price','min_car_price',
                    'average_car_kilos','min_car_kilos',
                    'max_car_kilos'
                ],
                'total_car_data':[
                    'auction_loc',	'auction_number','car_brand',
                    'car_name','car_auction_start_price','car_color',
                    'car_img_src',	'car_name','car_owner','car_reputation',
                    'car_type',	'engine_size','fuel_type','kilos','transmission',
                    'year'
                ]
            }
            gdh.upload_multisheet_excel(file_string,data_dict,google_drive_id,columns_dict)
            
        
        except:
            logger.error(UPLOAD_GOOGLE_SPREAD,extra=log_data)
            handler.destroy()
            raise AirflowException 


        
    else:
        raise AirflowException 
