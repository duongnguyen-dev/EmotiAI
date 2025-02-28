from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv
load_dotenv()
# Define the PostgreSQL database URL
DATABASE_URL = f'postgresql+psycopg2://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@127.0.0.1:5437/goemotion'

# Create an engine
engine = create_engine(DATABASE_URL)

# Define a base class for declarative class definitions
Base = declarative_base()

# Define a class mapped to the 'my_table' table
class MyTable(Base):
    __tablename__ = 'train'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    label = Column(ARRAY(Integer))
    # Add other columns as needed

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Query the database
results = session.query(MyTable).all()

# Process the results
for instance in results[:10]:
    print(instance)

# Close the session
session.close()
