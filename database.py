import datetime
from typing import List

import pytz
from sqlalchemy.orm import sessionmaker

import badge
from models import *


def setup_db_connection():
    thread_engine = create_engine('sqlite:///britebadge.db?check_same_thread=False')
    Base.metadata.bind = thread_engine
    DBParent = sessionmaker(bind=thread_engine)
    db_session = DBParent()
    return db_session


def get_current_attendees(db_session, event_id) -> List[Attendee]:
    attendees = db_session.query(Attendee).filter(Attendee.event_id == int(event_id)).all()
    return sorted(attendees, key=lambda x: x.surname, reverse=False)


def get_last_check_time(db_session):
    last_checked_time = db_session.query(Configuration).filter(Configuration.config_key == "last_checked_time").first()
    f = '%Y-%m-%d %H:%M:%S%z'
    if last_checked_time:
        to_return = datetime.datetime.strptime(last_checked_time.config_value, f)
        last_checked_time.config_value = datetime.datetime.now(pytz.utc).strftime(f)
        db_session.commit()
        return to_return
    else:
        current_time = datetime.datetime.now(pytz.utc)
        t = Configuration(config_key="last_checked_time", config_value=current_time.strftime(f))
        db_session.add(t)
        db_session.commit()
        return datetime.datetime.now(pytz.utc) - datetime.timedelta(days=360)


def compare_attendees(db_session, current_attendees: List[Attendee], new_attendees: List[Attendee]):
    for new_attendee in new_attendees:
        for current_attendee in current_attendees:
            if new_attendee.attendee_id == current_attendee.attendee_id:
                if current_attendee.status != new_attendee.status:
                    print("Updated {} from {} to {}".format(current_attendee.first_name, current_attendee.status, new_attendee.status))
                    current_attendee.status = new_attendee.status

                    if new_attendee.status == "Checked In":
                        print("Printing label for {} {}".format(new_attendee.first_name, new_attendee.surname))
                        db_session.add(PrintQueue(name="{} {}".format(new_attendee.first_name, new_attendee.surname), order_id=current_attendee.order_id, attendee_id=new_attendee.attendee_id, printed=False))

                        db_session.commit()

                break
        else:
            db_session.add(new_attendee)
    db_session.commit()


def get_next_print_queue_item(db_session) -> PrintQueue:
    queue_item = db_session.query(PrintQueue).filter(PrintQueue.printed == False).first()
    return queue_item


def mark_queue_item_as_printed(db_session, queue_item:PrintQueue):
    queue_item.printed = True
    db_session.commit()


def get_print_queue(db_session) -> List[PrintQueue]:
    queue = db_session.query(PrintQueue).all()
    return sorted(queue, key=lambda x: x.queue_id, reverse=True)


def clear_print_queue(db_session):
    db_session.query(PrintQueue).delete()
    db_session.commit()


def add_to_print_queue(db_session, attendee_id):
    attendee = db_session.query(Attendee).filter(Attendee.attendee_id == int(attendee_id)).first()
    db_session.add(PrintQueue(name="{} {}".format(attendee.first_name, attendee.surname), order_id=attendee.order_id, attendee_id=attendee.attendee_id, printed=False))
    db_session.commit()