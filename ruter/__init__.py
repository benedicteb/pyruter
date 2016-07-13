#!/usr/bin/env python
import json
import urllib
import pytz

from datetime import datetime as dt
from datetime import timedelta
from dateutil.parser import parse as dparse
from pytz import timezone, reference

from requests import get

_URIBASE = 'https://reisapi.ruter.no'
_SYS_TZ = reference.LocalTimezone()

class Ruter(object):
    def __init__(self, uribase=_URIBASE):
        self.uribase = uribase

    def get_place(self, search_string):
        return self.get_places(search_string)[0]

    def get_places(self, search_string):
        response = get(urljoin(self.uribase, 'Place/GetPlaces', search_string))
        verify_response(response)

        return json.loads(response.text)

    def get_stop(self, stop_id):
        response = get(urljoin(self.uribase, 'Place/GetStop', stop_id))
        verify_response(response)

        return json.loads(response.text)

    def get_departures(self, stop_id, datetime=None, transporttypes=None,
            linenames=None):
        params = {}

        if datetime:
            params['datetime'] = datetime
        if transporttypes:
            params['transporttypes'] = transporttypes
        if linenames:
            params['linenames'] = linenames

        url = urljoin(self.uribase, 'StopVisit/GetDepartures', stop_id)

        if len(params.keys()) > 0:
            url += '?' + urllib.urlencode(params)

        response = get(url)
        verify_response(response)

        return json.loads(response.text)

    def get_next_departure(self, stop_id, linename, direction):
        """
        direction: 1 is towards city center, 2 is west
        """
        all_departures = self.get_departures(stop_id, linenames=linename)
        all_departures = [d for d in all_departures if
            d['MonitoredVehicleJourney']['DirectionName'] == str(direction)]

        next_departure = min(all_departures, key=lambda elm:
            elm['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime'])

        return next_departure['MonitoredVehicleJourney']

    def get_time_until_next_departure(self, stop_id, linename, direction):
        departure = self.get_next_departure(stop_id, linename=linename,
                direction=direction)

        departure_dt =\
            localize(dparse(departure['MonitoredCall']['ExpectedArrivalTime']))
        now = tz_now()

        return localize(departure_dt) - tz_now()

def verify_response(response):
    if not str(response.status_code).startswith('2'):
        raise Exception('%s: %s' % (response.code, response.text))

    try:
        json.loads(response.text)
    except Exception as e:
        raise Exception('Unable to parse json\n  %s' % str(e))

def urljoin(*args):
    uri = ''

    for arg in args:
        if not uri.endswith('/') and uri != '':
            uri += '/'

        uri += str(arg)

    return uri

def tz_now():
    return pytz.utc.localize(dt.utcnow()).astimezone(_SYS_TZ)

def localize(timestamp):
    return timestamp.astimezone(_SYS_TZ)
