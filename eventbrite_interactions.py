from eventbrite import Eventbrite

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
        print(f"{page} queries made!")
        return {"attendees": attendees}

    def get_all_my_eventbrite_events(self):
        my_id = eventbrite.get_user()['id']
        events = eventbrite.get_user_events(my_id)
        # events = eventbrite.event_search(**{'user.id': my_id})
        return events["events"]


eventbrite = MyEventbrite(eventbrite_key)


def eventbrite_test():
    print(eventbrite.get_user())
    a = eventbrite.get_user_events(eventbrite.get_user()["id"])
    print(eventbrite.get_user_owned_events(eventbrite.get_user()["id"]))


def get_eventbrite_event_by_id(id):
    return eventbrite.get_event(id)


def get_eventbrite_events_name_id():
    events = eventbrite.get_user_owned_events(eventbrite.get_user()["id"])
    jam_event_names = []
    for event in events["events"]:
        jam_event_names.append({"name": event["name"]["text"], "id": event["id"]})
    return jam_event_names


def get_eventbrite_attendees_for_event(event_id, changed_since=None):
    return eventbrite.get_all_event_attendees(event_id, changed_since=changed_since)


def get_most_recent_eventbrite_event():
    events = eventbrite.get_all_my_eventbrite_events()
    return events[-1]
