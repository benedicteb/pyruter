pyruter
=======

Jeg søkte gjennom pip og github for å se om noen hadde laget et Ruter-bibliotek
til Python og kunne ikke finne no. Siden jeg hadde lyst til å leke lagde jeg
derfor dette.

Ruter-API'et har mye funksjonalitet, og det er veldig lite som foreløpig er
dekket her.

## Installasjon

Lurt å installere for kun sin egen bruker.

```
$ python setup.py install --user
```

## Eksempler

Hent ut info om en stasjon (merk: henter kun ut første elementen av et søk, så
bruk nøyaktige strenger, f.eks. `Forskningsparken [T-bane]`):

```
>>> import ruter
>>> r = ruter.Ruter()
>>> r.get_place('Forskningsparken [T-bane]')
{u'Name': u'Forskningsparken [T-bane]', u'Zone': u'1', u'IsHub': False, u'Lines': [{u'LineColour': u'F07800', u'Transportation': 8, u'ID': 4, u'Name': u'4'}, {u'LineColour': u'F07800', u'Transportation': 8, u'ID': 5, u'Name': u'5'}], u'PlaceType': u'Stop', u'Y': 6646383, u'X': 596132, u'ShortName': u'FOP', u'ID': 3010370, u'District': u'Oslo'}
```

Søk etter stasjoner:

```
>>> r.get_places('Jernbanetorget')
[{u'Name': u'Jernbanetorget (omr\xe5de)', u'District': u'Oslo', u'Stops': [{u'Name': u'Tollboden', u'Zone': u'1', u'IsHub': False, u'Lines': [], u'PlaceType': u'Stop', u'Y': 6642616, u'X': 597882, u'ShortName': u'TOBO', u'ID': 3010005, u'District': u'Oslo'}, {u'Name': u'Oslo Sentralstasjon [tog]', u'Zone': u'1', u'IsHub': False, u'Lines': [], u'PlaceType': u'Stop', u'Y': 6642800, u'X': 598000, u'ShortName': u'OS', u'ID': 3010010, u'District': u'Oslo'}, {u'Name': u'Jernbanetorget [T-bane]', u'Zone': u'1', u'IsHub': False, u'Lines': [], u'PlaceType': u'Stop', u'Y': 6642890, u'X': 597930, u'ShortName': u'JER', u'ID': 3010011, u'District': u'Oslo'}, {u'Name': u'Jernbanetorget (B.Gunnerus g.) -->
```

Hent stasjon fra stasjonsid:

```
>>> r.get_stop(123)
{u'Name': u'Nobels gate', u'Zone': u'1', u'IsHub': False, u'Lines': [], u'PlaceType': u'Stop', u'Y': 6643393, u'X': 595020, u'ShortName': u'NOG', u'ID': 3010123, u'District': u'Oslo'}
```

Hent ut alle departures:

```
>>> r.get_departures(stop_id)
```

Den returnerer mye data. Tar også tre valgfrie argumenter `datetime`,
`transporttypes` og `linenames`.

Hent ut den neste avgangen fra en gitt stasjon, en gitt linje og i en gitt
retning. Retning `1` er mot sentrum og `2` er vestover.

```
>>> r.get_next_departure(r.get_place('Forskningsparken [T-bane]')['ID'], '5', 1)
{u'MonitoredCall': {u'VisitNumber': 8, u'DestinationDisplay': u'Ringen via Majorstuen', u'VehicleAtStop': True, u'AimedDepartureTime': u'2016-07-13T09:12:00+02:00', u'DeparturePlatformName': u'1 (Retning sentrum)', u'AimedArrivalTime': u'2016-07-13T09:12:00+02:00', u'ExpectedDepartureTime': u'2016-07-13T09:12:00+02:00', u'ExpectedArrivalTime': u'2016-07-13T09:12:00+02:00'}, u'OperatorRef': u'me', u'OriginAimedDepartureTime': u'0001-01-01T00:00:00', u'Delay': u'PT0S', u'DestinationRef': u'3012120', u'DestinationAimedArrivalTime': u'0001-01-01T00:00:00', u'PublishedLineName': u'5', u'Monitored': True, u'TrainBlockPart': {u'NumberOfBlockParts': 6}, u'VehicleMode': 4, u'LineRef': u'5', u'FramedVehicleJourneyRef': {u'DataFrameRef': u'2016-07-13', u'DatedVehicleJourneyRef': u'1934'}, u'DirectionRef': u'1', u'InCongestion': False, u'DestinationName': u'Ringen via Majorstuen', u'OriginName': u'SOG1', u'OriginRef': u'3012280', u'VehicleFeatureRef': u'', u'VehicleRef': u'83', u'BlockRef': u'510:TSH02', u'DirectionName': u'1', u'VehicleJourneyName': u'200050083'}
```

Og en praktisk metode for å hente *hvor lenge* det er til neste avgang:

```
>>> r.get_time_until_next_departure(r.get_place('Forskningsparken [T-bane]')['ID'], '5', 1)
datetime.timedelta(0, 156, 396041)
```
