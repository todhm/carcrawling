from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os 



def create_session():
    url = os.environ.get("POSTGRES_SERVICE_URL")
    some_engine = create_engine(url)

    # create a configured "Session" class
    Session = sessionmaker(bind=some_engine)

    # create a Session
    session = Session()
    return session 