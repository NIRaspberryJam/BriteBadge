import json
import sys
import time

import requests
from flask import Flask, render_template, redirect, request

import database
import eventbrite_interactions
import models
from secrets.config import delay_between_eventbrite_queries, eventbrite_event_id

import threading
import badge

import secrets.config as config

app = Flask(__name__)
chosen_event = eventbrite_interactions.get_most_recent_eventbrite_event()

flask_db_session = database.setup_db_connection()


class BackgroundPrinter(threading.Thread):

    def __init__(self, day_password, event_name):
        super().__init__()
        self.day_password = day_password
        self.event_name = event_name

        self.db_session = database.setup_db_connection()

    def run(self):
        while True:
            try:
                queue_item = database.get_next_print_queue_item(self.db_session)
                if queue_item:
                    print("PRINTING BADGE FOR {}".format(queue_item.name))
                    badge.create_label_image(queue_item.name, queue_item.order_id, self.day_password, self.event_name, queue_item.attendee.ticket_name, use_nijis=config.use_nijis, nijis_url=config.nijis_base_url)
                    database.mark_queue_item_as_printed(self.db_session, queue_item)
                else:
                    time.sleep(0.5)
            except Exception as e:
                print("---------------")
                print("EXCEPTION!?!?!?")
                print(e)
                print("---------------")
                time.sleep(3)


class EventbriteWatcher(threading.Thread):
    
    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id
        self.db_session = database.setup_db_connection()
    
    
    def run(self):
        while True:
            try:
                self.update()
            except Exception as e:
                print("---------------")
                print("EXCEPTION!?!?!?")
                print(e)
                print("---------------")


    def update(self):
        start_update = time.time()
        print("Checking for updates")
        attendees = []
        raw_attendees = eventbrite_interactions.get_eventbrite_attendees_for_event(event_id, changed_since=database.get_last_check_time(self.db_session))["attendees"]
        for attendee in raw_attendees:
            new_attendee = (models.Attendee(attendee_id=int(attendee["id"]), order_id=int(attendee["order_id"]), event_id=int(event_id)
                                            , first_name=attendee["profile"]["first_name"], surname=attendee["profile"]["last_name"],
                                            status=attendee["status"], ticket_name=attendee["ticket_class_name"]))
            new_attendee.event_name = chosen_event
            attendees.append(new_attendee)
        current_attendees = database.get_current_attendees(self.db_session, event_id)
        database.compare_attendees(self.db_session, current_attendees, attendees)
        print("Checking for updates from Eventbrite took {} seconds.".format(time.time() - start_update))

        # To be removed eventually when Javascript is making the queries to this endpoint
        time.sleep(int(delay_between_eventbrite_queries))


def get_day_password():
    if config.use_nijis:
        data = { "token": config.nijis_api_key,}
        res = requests.post('{}/api/get_jam_day_password'.format(config.nijis_base_url), json=json.dumps(data))
        if res:
            return res.json()["jam_day_password"]
        print("Unable to get Jam day password...")
        sys.exit(1)
    return None


@app.route("/")
def home():
    attendees = database.get_current_attendees(flask_db_session, event_id)
    return render_template("index.html", attendees=attendees, event_name=event["name"]["text"])


@app.route("/print_queue")
def print_queue():
    return render_template("print_queue.html")


@app.route("/get_print_queue_ajax", methods=['GET', 'POST'])
def get_print_queue():
    queue = database.get_print_queue(flask_db_session)
    to_send = ([dict(queue_id=q.queue_id, name=q.name, order_id=q.order_id, attendee_id=q.attendee_id, printed=q.printed) for q in queue])
    return json.dumps(to_send)


@app.route("/add_badge_to_queue", methods=['GET', 'POST'])
def add_badge_to_queue():
    attendee_id = request.form["attendee_id"]
    database.add_to_print_queue(flask_db_session, attendee_id)
    return ""


@app.route("/clear_print_queue")
def clear_print_queue():
    database.clear_print_queue(flask_db_session)
    return redirect("/print_queue")


if __name__ == '__main__':
    if eventbrite_event_id: # Manual eventbrite id
        event = eventbrite_interactions.get_eventbrite_event_by_id(eventbrite_event_id)
    else:
        event = eventbrite_interactions.get_most_recent_eventbrite_event()

    if event:
        print("Setting up for {} event...".format(event["name"]["text"]))
        event_id = event["id"]

        background_printer = BackgroundPrinter(day_password=get_day_password(), event_name=event["name"]["text"])
        background_printer.daemon = True
        background_printer.start()

        eventbrite_watcher = EventbriteWatcher(event)
        eventbrite_watcher.daemon = True
        eventbrite_watcher.start()
        app.run()
    else:
        print("Error - Unable to find any Eventbrite events on that account...")
