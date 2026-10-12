from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


db_url = 'postgresql://pranav.baradkar:123456789@localhost:5432/postgres'
engine = create_engine(url = db_url)
session = sessionmaker(autocommit=False,autoflush=False, bind=engine)