from django.shortcuts import render
from django.views.generic import TemplateView

from datetime import datetime, timedelta, timezone
import icalendar
from dateutil.rrule import *
import requests
import re
import os

def get_current_semester():
    curr_m = datetime.now().month
    curr_y = datetime.now().year
    if curr_m < 6:
        sem = "Spring"
    elif curr_m == 6 or curr_m == 7:
        sem = "Sum"
    else:
        sem = "Fall"
    return sem

# return list of dicts for each seminar
# the summary part of the event must follow this synatx
# in each dict, the keys correspond to <key>:

# Speaker:  <speaker>
# Affiliation: <affiliation>
# Title: <title>
# Abstract: <abstract>
# a <date> will be created automatically
def get_calendar_data(url):

    resp = requests.get(url)
    gcal = icalendar.Calendar.from_ical(resp.text)

    event_list = []

    for component in gcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            description = component.get('description')
            location = component.get('location')
            startdt = component.get('dtstart').dt
            enddt = component.get('dtend').dt
            exdate = component.get('exdate')
            #print(startdt, summary, description)
            event_list.append([str(startdt)[:10], str(summary), str(description)])
    event_list.sort()
    outstr = ""
    seminar_list = []

    # What is the current semester?
    sem = get_current_semester()


    for e in event_list:
        date = datetime.strptime(e[0], "%Y-%m-%d")
        summary = e[1]
        descr = e[2]

        outdict = {}

        # limit timeframe
        mon = date.month
        yr = date.year
        if yr != datetime.now().year: continue
        if sem == "Spring" and mon >= 8: continue # show spring semster Jan - Jul
        if sem == "Fall" and mon < 8: continue  # fall semester Sep - Dec

        # parse description
        #print("\n------------------", descr)

        #Speaker:<name>/n
        r = re.search("Speaker:(.*?)\n", descr)
        if r:
            #print(date.strftime("%a %b %d, %Y"))
            outdict["date"] = date.strftime("%a %b %d, %Y")
            #print(r.group(1))
            outdict["speaker"] = r.group(1)

            outstr += date.strftime("%a. %B %d, %Y") + "\n" + r.group(1) + "\n"


        r = re.search("Affiliation:(.*?)\n", descr)
        if r:
            #print(r.group(1))
            outdict["affiliation"] = r.group(1)
            outstr += r.group(1) + "\n"

        r = re.search("Title:(.*?)\n", descr)
        if r:
            #print(r.group(1))
            outdict["title"] = r.group(1)
            outstr += r.group(1) + "\n"

        r = re.search("Abstract:(.*?)\n", descr)
        if r:
            #print(repr(r.group(1)), descr)
            outdict["abstract"] = "Abstract: " + r.group(1)
            outstr += "Abstract: " + r.group(1) + "\n"

        if outdict.get("date") != None:
            seminar_list.append(outdict)

    return seminar_list


# test
if __name__ == "__main__":
    from pprint import pprint
    # my seminar google calendar
    url = "https://calendar.google.com/calendar/ical/egdnrrp6oh8325lf720rv01dno%40group.calendar.google.com/public/basic.ics"

    data = get_calendar_data(url)
    pprint(data)

class HomePageView(TemplateView):
    def get(self, request, **kwargs):

        # my seminar google calendar
        url = "https://calendar.google.com/calendar/ical/egdnrrp6oh8325lf720rv01dno%40group.calendar.google.com/public/basic.ics"

        # list of dicts, one for each event
        data = get_calendar_data(url)

        # What is the current semester?
        sem = get_current_semester()
        year = datetime.now().year

        context = {
            'data': data,
            "page_title": "GeAt Seminar Calendar " + sem +  " " + str(year)
        }
        return render(request, 'index.html', context)

