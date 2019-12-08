import pytest
from collections import defaultdict
from datetime import timedelta, datetime
from dateutil import parser

from tests.db_support import devices_with_events


@pytest.mark.parametrize('uuid, db_data', devices_with_events(event_type='geo', days_to_collect=10))
def test_get_geo_events(uuid, db_data, iot_api):
    _to = parser.parse(str(datetime.utcnow().date()))
    _from = (_to - timedelta(days=10))

    api_events = iot_api['geo_event'].get(url_param='?deviceId=%s&from=%s&to=%s&size=100' %
                                                    (uuid, _from.isoformat() + 'Z', _to.isoformat() + 'Z'))

    assert api_events['totalElements'] == len(db_data), \
        'Fail: uuid: %s, number of entries: api %s != %s db' % (uuid, api_events['totalElements'], len(db_data))

    api_events = api_events['content']

    if api_events:

        assert parser.parse(api_events[-1]['eventTimestamp'], ignoretz=True) <= _to, \
            'Fail: uuid: %s, telemetry period: api %s <= %s db' % (uuid, api_events[-1]['eventTimestamp'], _to)
        assert parser.parse(api_events[0]['eventTimestamp'], ignoretz=True) >= _from, \
            'Fail: uuid: %s, telemetry period: api %s >= %s db' % (uuid, api_events[0]['eventTimestamp'], _from)

        for event in api_events:
            eid = event['eventId']
            db_event = defaultdict(lambda: None, db_data[eid])
            event = defaultdict(lambda: None, event)
            assert eid == db_event['event_id'], 'Fail: uuid: %s, event id: api %s != %s db' % (uuid, eid, db_data[eid])

            if db_event['criteria_type'] == 'geofence_in':
                assert event['eventType'] == 'IN', 'Fail: uuid: %s, geo type: api %s != IN' % (
                    uuid, event['telemetryType'])
            else:
                assert event['eventType'] == 'OUT', 'Fail: uuid: %s, telemetry type: api %s != OUT' % (
                    uuid, event['telemetryType'])

            assert event['value'] == db_event['value'], \
                'Fail: uuid: %s, telemetry value: api %s != %s db' % (uuid, event['value'], db_event['value'])
            assert event['deviceId'] == uuid, \
                'Fail: uuid: %s, device id: api %s != %s db' % (uuid, event['deviceId'], uuid)
            assert event['coordinates'] == db_event['coordinates'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                (uuid, event['coordinates']['coordinates'], db_event['coordinates'])
            assert parser.parse(event['eventTimestamp'], ignoretz=True) == db_event['record_date'].replace(microsecond=0), \
                'Fail: uuid: %s, event time: api %s != %s db' % (uuid, event['eventTimestamp'], db_event['record_date'])
