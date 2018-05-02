#!/usr/bin/env python
import json
import pytz

from datetime import datetime as dt
from dateutil.parser import parse as dparse
from pytz import reference

from requests import get

_URIBASE = 'https://reisapi.ruter.no'
_SYS_TZ = reference.LocalTimezone()


class Ruter(object):
    def __init__(self, uribase=_URIBASE):
        self.uribase = uribase
        self.location = None

    def set_location(self, location=None):
        """
        Location should be a tuple with x as the first value and y as the second
        """
        self.location = location

    def get_simple(self, api_method, search_string="", params=None):
        response = get(
            urljoin(self.uribase, api_method, search_string), params)
        verify_response(response)

        return json.loads(response.text)

    def get_validities(self):
        """
        Returns the date and time for the first and last valid search time.

        http://reisapi.ruter.no/Help/Api/GET-Meta-GetValidities
        """
        return self.get_simple('Meta/GetValidities')

    def get_hearbeat(self):
        """
        http://reisapi.ruter.no/Help/Api/GET-Heartbeat-Index
        """
        return self.get_simple('Heartbeat/Index')

    def get_street(self, street_id):
        """
        http://reisapi.ruter.no/Help/Api/GET-Street-GetStreet-id
        """
        return self.get_simple('Street/GetStreet', street_id)

    def get_trip(self, trip_id, trip_time=None):
        params = {}

        if trip_time:
            params['time'] = trip_time

        return self.get_simple('Trip/GetTrip', trip_id, params)

    def get_places(self, search_string, location=None, counties=None):
        """
        http://reisapi.ruter.no/Help/Api/GET-Place-GetPlaces-id_location
        """
        params = {}

        if location:
            params['location'] = get_location_string(location)
        elif self.location:
            params['location'] = get_location_string(self.location)

        if counties:
            params['counties'] = counties

        return self.get_simple('Place/GetPlaces', search_string, params)

    def get_place(self, search_string, location=None):
        """
        http://reisapi.ruter.no/Help/Api/GET-Place-GetPlaces-id_location
        """
        return self.get_places(search_string, location)[0]

    def get_stop(self, stop_id):
        """
        http://reisapi.ruter.no/Help/Api/GET-Place-GetStop-id
        """
        return self.get_simple('Place/GetStop', stop_id)

    def get_stops_ruter(self):
        """
        http://reisapi.ruter.no/Help/Api/GET-Place-GetStopsRuter
        """
        return self.get_simple('Place/GetStopsRuter')

    def get_travels(self, **travel_args):
        """
        http://reisapi.ruter.no/Help/Api/GET-Travel-GetTravels_fromPlace_toPlace_isafter_time_changemargin_changepunish_walkingfactor_proposals_transporttypes_maxwalkingminutes_linenames_waitReluctance_walkreluctance_waitAtBeginningFactor_showIntermediateStops_ignoreRealtimeUpdates_intermediateStops
        """
        return self.get_simple('Travel/GetTravels', '', travel_args)

    def get_travels_extension(self, **travel_args):
        """
        http://reisapi.ruter.no/Help/Api/GET-Travel-GetTravelsExtension_fromplace_toplace_isafter_time_changemargin_changepunish_walkingfactor_proposals_transporttypes_maxwalkingminutes_linenames_showIntermediatePlaces_ignoreRealtimeUpdates
        """
        return self.get_simple('Travel/GetTravelsExtension', '', travel_args)

    def get_lines(self, ruter_operated_only=False, extended=False):
        """
        http://reisapi.ruter.no/Help/Api/GET-Line-GetLines
        http://reisapi.ruter.no/Help/Api/GET-Line-GetLinesRuter_ruterOperatedOnly
        http://reisapi.ruter.no/Help/Api/GET-Line-GetLinesRuterExtended_ruterOperatedOnly
        """
        if ruter_operated_only:
            if extended:
                url = 'Line/GetLinesRuter/Extended'
            else:
                url = 'Line/GetLinesRuter'
            return self.get_simple(url, '', {'ruterOperatedOnly': True})
        else:
            return self.get_simple('Line/GetLines')

    def get_lines_by_stop_id(self, stop_id):
        """
        http://reisapi.ruter.no/Help/Api/GET-Line-GetLinesByStopID-id
        """
        return self.get_simple('Line/GetLinesByStopID', stop_id)

    def get_data_by_line_id(self, line_id):
        """
        http://reisapi.ruter.no/Help/Api/GET-Line-GetDataByLineID-id
        """
        return self.get_simple('Line/GetDataByLineID', line_id)

    def get_stops_by_line_id(self, line_id):
        """
        http://reisapi.ruter.no/Help/Api/GET-Line-GetStopsByLineID-id
        """
        return self.get_simple('Line/GetStopsByLineID', line_id)

    def get_departures(self,
                       stop_id,
                       datetime=None,
                       transporttypes=None,
                       linenames=None):
        """
        http://reisapi.ruter.no/Help/Api/GET-StopVisit-GetDepartures-id_datetime_transporttypes_linenames
        """
        params = {}

        if datetime:
            params['datetime'] = datetime

        if transporttypes:
            params['transporttypes'] = transporttypes

        if linenames:
            params['linenames'] = linenames

        return self.get_simple('StopVisit/GetDepartures', stop_id, params)

    def get_next_departure(self, stop_id, linename, direction):
        """
        direction: 1 is towards city center, 2 is west
        """
        all_departures = self.get_departures(stop_id, linenames=linename)
        all_departures = [
            d for d in all_departures
            if d['MonitoredVehicleJourney']['DirectionName'] == str(direction)
        ]

        next_departure = min(
            all_departures,
            key=
            lambda elm: elm['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
        )

        return next_departure['MonitoredVehicleJourney']

    def get_time_until_next_departure(self, stop_id, linename, direction):
        departure = self.get_next_departure(
            stop_id, linename=linename, direction=direction)

        departure_dt =\
            localize(dparse(departure['MonitoredCall']['ExpectedArrivalTime']))

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


def get_location_string(location):
    """
    Get coordinates as a string compatible with the Ruter API
    """
    if location:
        return f"(x={location[0]},y={location[1]})"
    else:
        return None
