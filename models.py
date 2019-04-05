from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///britebadge.db?check_same_thread=False')


class Attendee(Base):
    __tablename__ = "attendees"
    attendee_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    order_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    first_name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    status = Column(String(20))


class Configuration(Base):
    __tablename__ = "configuration"
    config_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    config_key = Column(String(50), nullable=False, unique=True)
    config_value = Column(String(50), nullable=False)


Base.metadata.create_all(engine)
