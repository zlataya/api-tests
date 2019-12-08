import pytest
from collections import defaultdict
from datetime import timedelta, timezone
from dateutil import parser

from tests.db_support import devices_dto


@pytest.mark.parametrize('uuid, db_data', devices_dto())
def test_get_telemetry(uuid, db_data, iot_api, get_iot_data, json_template):
    template_info = json_template('GetDeviceTelemetry')

    _to = db_data['sourcetelemetryupdated']
    _from = (_to - timedelta(days=1))

    # get the data from Dynamo and compare it with API response
    telemetry_in = get_iot_data(db_data['device_id'],
                                _from.replace(tzinfo=timezone.utc).timestamp()*1000,
                                _to.replace(tzinfo=timezone.utc).timestamp()*1000)
    telemetry_out = iot_api['telemetry'].get(url_param='?deviceId=%s&from=%s&to=%s&size=100' %
                                                       (uuid, _from.isoformat() + 'Z', _to.isoformat() + 'Z'))

    assert telemetry_out['totalElements'] == len(telemetry_in), \
        'Fail: uuid: %s, number of entries: api %s != %s db' % (uuid, telemetry_out['totalElements'], len(telemetry_in))

    telemetry_out = telemetry_out['content']

    if telemetry_out:

        assert parser.parse(telemetry_out[0]['eventTimestamp'], ignoretz=True) <= _to, \
            'Fail: uuid: %s, telemetry period (max): %s > %s' % (uuid, telemetry_out[0]['eventTimestamp'], _to)
        assert parser.parse(telemetry_out[-1]['eventTimestamp'], ignoretz=True) >= _from, \
            'Fail: uuid: %s, telemetry period (min): %s < %s' % (uuid, telemetry_out[-1]['eventTimestamp'], _from)

        for data_in, data_out in zip(telemetry_in.values(), telemetry_out):
            data_in = defaultdict(lambda: 0, data_in)
            data_out = defaultdict(lambda: 0, data_out)
            assert db_data['id'] == data_out['deviceId'], \
                'Fail: uuid: %s, id: api %s != %s db' % (uuid, data_out['deviceId'], db_data['id'])

            if 'location' in data_in:
                assert list(data_in['location'].values()) == [data_out['longitude'], data_out['latitude']], \
                    'Fail: uuid: %s, location: api %s != %s db' % \
                    (uuid, [data_out['longitude'], data_out['latitude']], list(data_in['location'].values()))

            assert parser.parse(data_in['record_date']) == parser.parse(data_out['eventTimestamp']), \
                'Fail: uuid: %s, eventTimestamp: api %s != %s db' % (uuid, data_out['eventTimestamp'], data_in['record_date'])

            for k in template_info:
                assert float(data_in[k]) == float(data_out[k]), 'Fail: uuid: %s, %s: api %s != %s db' % \
                                                                (uuid, k, data_out[k], data_in[k])
