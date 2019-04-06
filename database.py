import datetime
from typing import List

import pytz
from sqlalchemy.orm import sessionmaker

import badge
from models import *
from secrets.config import jam_password

Base.metadata.bind = engine
DBParent = sessionmaker(bind=engine)
db_session = DBParent()


def get_current_attendees():
    attendees = db_session.query(Attendee).all()
    return attendees


def get_last_check_time():
    last_checked_time = db_session.query(Configuration).filter(Configuration.config_key == "last_checked_time").first()
    f = '%Y-%m-%d %H:%M:%S%z'
    if last_checked_time:
        return datetime.datetime.strptime(last_checked_time.config_value, f)
    else:
        current_time = datetime.datetime.now(pytz.utc)
        t = Configuration(config_key="last_checked_time", config_value=current_time.strftime(f))
        db_session.add(t)
        db_session.commit()
        return get_last_check_time()


def compare_attendees(current_attendees: List[Attendee], new_attendees: List[Attendee]):
    for new_attendee in new_attendees:
        for current_attendee in current_attendees:
            if new_attendee.attendee_id == current_attendee.attendee_id:
                if current_attendee.status != new_attendee.status:
                    print("Updated {} from {} to {}".format(current_attendee.first_name, current_attendee.status, new_attendee.status))
                    current_attendee.status = new_attendee.status

                    if new_attendee.status == "Checked In":
                        print("Printing label for {} {}".format(new_attendee.first_name, new_attendee.surname))
                        badge.create_label_image("{} {}".format(new_attendee.first_name, new_attendee.surname), current_attendee.order_id, jam_password, new_attendee.event_name["name"]["text"], new_attendee.ticket_name)
                        db_session.commit()

                break
        else:
            db_session.add(new_attendee)
    db_session.commit()
