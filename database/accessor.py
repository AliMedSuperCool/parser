from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import settings

engine = create_engine(settings.db_url)
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session