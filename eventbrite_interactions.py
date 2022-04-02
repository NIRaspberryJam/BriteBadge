from eventbrite import Eventbrite
import datetime

from secrets.config import eventbrite_key


class MyEventbrite(Eventbrite):
    # From https://github.com/eventbrite/eventbrite-sdk-python/issues/18
    # For getting all attendees
    def get_event_attendees(self, event_id, status=None,
                            changed_since=None, page=1):
        """
        Returns a paginated response with a key of attendees, containing a
        list of attendee.

        GET /events/:id/attendees/
        """
        data = {}
        if status:  # TODO - check the types of valid status
            data['status'] = status
        if changed_since:
            data['changed_since'] = changed_since.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['page'] = page
        return self.get("/events/{0}/attendees/".format(event_id), data=data)

    def get_all_event_attendees(self, event_id, status=None,
                                changed_since=None):
        """
        Returns a full list of attendees.

        TODO: figure out how to use the 'continuation' field properly
        """
        page = 1
        attendees = []
        while True:
            r = self.get_event_attendees(event_id, status, changed_since, page=page)
            if 'attendees' not in r:
                break
            attendees.extend(r['attendees'])
            if r['pagination']['page_count'] <= page:
                break
            page += 1
        print("{} queries made!".format(page))
        return {"attendees": attendees}


    def get_all_my_eventbrite_events(self):
        events = get_eventbrite_events_name_id()
        return events


eventbrite = MyEventbrite(eventbrite_key)


def _get_event_datetime(event):
    return datetime.datetime.strptime(event["start"]["local"].replace("T", " "), '%Y-%m-%d %H:%M:%S')

def eventbrite_test():
    print(eventbrite.get_user())
    a = eventbrite.get_user_events(eventbrite.get_user()["id"])
    print(eventbrite.get_user_owned_events(eventbrite.get_user()["id"]))


def get_eventbrite_event_by_id(id):
    return eventbrite.get_event(id)


def get_eventbrite_events_name_id():
    if not eventbrite_key:
        return []
    organisations = eventbrite.get("/users/me/organizations/")["organizations"]
    if organisations:
        eventbrite_organisation = organisations[0]
    else:
        return {}


    events = eventbrite.get(f"/organizations/{eventbrite_organisation['id']}/events/", data={"page_size":200})
    return events["events"]


def get_eventbrite_attendees_for_event(event_id, changed_since=None):
    return eventbrite.get_all_event_attendees(event_id, changed_since=changed_since)


def get_most_recent_eventbrite_event():
    events = eventbrite.get_all_my_eventbrite_events()
    if events:
        newest_event = events[0]
        for event in events:
            if _get_event_datetime(newest_event) < _get_event_datetime(event):
                newest_event = event
        return newest_event
    return None
