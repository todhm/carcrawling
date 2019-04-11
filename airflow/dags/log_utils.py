import os 
import logging 
from log4mongo.handlers import BufferedMongoHandler


def log_factory(db_name):
    mongo_host = os.environ.get('MONGO_URI')
    handler = BufferedMongoHandler(
        host=mongo_host,
        database_name=db_name,
        collection='crawler_logs',
        buffer_early_flush_level=logging.ERROR
    )
    logger = logging.getLogger()
    log = logging.getLogger('cardataLogger')
    log.setLevel(logging.DEBUG)
    log.handlers = []
    log.addHandler(handler)
    return log,handler
