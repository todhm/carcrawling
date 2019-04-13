from airflow import DAG,settings
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pprint
import time 
import pendulum
from dag_utils import crawl_glovis_last_page,crawl_glovis_page,upload_glovis_spread
import re 

local_tz = pendulum.timezone("Asia/Seoul")
thisYear = datetime.now().year 
thisMonth = datetime.now().month -1 
thisDate = datetime.now().day
loc_list = ['bundang','siwha','yangsan']
def create_dag(loc):
    default_args = {
        'owner': 'fidel',
        'depends_on_past': False,
        'start_date': datetime(thisYear, thisMonth, thisDate, hour=11,minute=30,tzinfo=local_tz),
        'schedule_interval':'0 11 * * *',
        'email': ['fidel@crunchprice.com'],
        'email_on_failure': True,
        'email_on_retry': True,
        'retries': 2,
        'retry_delay': timedelta(seconds=10),
        'provide_context':True
    }

    dag_name = 'crawl_auction_' +loc
    if loc =="siwha":
        dag = DAG(dag_name,schedule_interval=default_args['schedule_interval'],dagrun_timeout=timedelta(hours=1),default_args=default_args,concurrency=8, catchup=False)
    else:
        dag = DAG(dag_name,schedule_interval=None,dagrun_timeout=timedelta(hours=1),default_args=default_args,concurrency=8, catchup=False)


    crp = PythonOperator(
        task_id='crawl_glovis_last_page',
        python_callable=crawl_glovis_last_page,
        dag=dag,
        op_kwargs={
            'loc':loc 
        }
    )

    cgp = PythonOperator(
        task_id='crawl_glovis_page',
        python_callable=crawl_glovis_page,
        dag=dag
    )

    upload_glovis_spread_task = PythonOperator(
        task_id='upload_glovis_spread',
        python_callable=upload_glovis_spread,
        dag=dag
    )

    cgp.set_upstream(crp)
    upload_glovis_spread_task.set_upstream(cgp)
    return dag 

for loc in loc_list:
    dag_name = 'crawl_auction_' +loc
    globals()[dag_name] = create_dag(loc)