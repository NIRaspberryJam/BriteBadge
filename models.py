from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
engine = create_engine('sqlite:///britebadge.db?check_same_thread=False')


class Configuration(Base):
    __tablename__ = "configuration"
    config_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    config_key = Column(String(50), nullable=False, unique=True)
    config_value = Column(String(50), nullable=False)


class PrintQueue(Base):
    __tablename__ = "print_queue"
    queue_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(70), nullable=False)
    order_id = Column(Integer, nullable=False)
    attendee_id = Column(ForeignKey('attendees.attendee_id'), nullable=False)
    ticket_name = Column(String(50), nullable=False)
    printed = Column(Boolean, nullable=False)


class Attendee(Base):
    __tablename__ = "attendees"
    event_name = ""
    ticket_name = ""
    attendee_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    order_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    first_name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    status = Column(String(20))
    badges_printed = relationship("PrintQueue", foreign_keys=PrintQueue.attendee_id)


Base.metadata.create_all(engine)
