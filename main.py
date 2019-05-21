import time

import requests
from flask import Flask, render_template

import database
import eventbrite_interactions
import models
from secrets.config import delay_between_eventbrite_queries, eventbrite_event_id

app = Flask(__name__)
chosen_event = eventbrite_interactions.get_most_recent_eventbrite_event()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/update")
def update(event_id):
    start_update = time.time()
    print("Checking for updates")
    attendees = []
    raw_attendees = eventbrite_interactions.get_eventbrite_attendees_for_event(event_id, changed_since=database.get_last_check_time())["attendees"]
    for attendee in raw_attendees:
        new_attendee = (models.Attendee(attendee_id=int(attendee["id"]), order_id=int(attendee["order_id"]), event_id=int(attendee["order_id"])
                                        , first_name=attendee["profile"]["first_name"], surname=attendee["profile"]["last_name"],
                                        status=attendee["status"]))
        new_attendee.event_name = chosen_event
        new_attendee.ticket_name = attendee["ticket_class_name"]
        attendees.append(new_attendee)
    current_attendees = database.get_current_attendees()
    database.compare_attendees(current_attendees, attendees)
    print("Checking for updates from Eventbrite took {} seconds.".format(time.time() - start_update))

    # To be removed eventually when Javascript is making the queries to this endpoint
    time.sleep(int(delay_between_eventbrite_queries))
    #requests.get("http://127.0.0.1:5000/update")
    return "Done"


if __name__ == '__main__':
    if eventbrite_event_id: # Manual eventbrite id
        event = eventbrite_interactions.get_eventbrite_event_by_id(eventbrite_event_id)
    else:
        event = eventbrite_interactions.get_most_recent_eventbrite_event()
        
    if event:
        print("Setting up for {} event...".format(event["name"]["text"]))
        event_id = event["id"]
        while True:
            try:
                update(event_id)
            except Exception as e:
                print("---------------")
                print("EXCEPTION!?!?!?")
                print(e)
                print("---------------")
                
        app.run()
    print("Error - Unable to find any Eventbrite events on that account...")
