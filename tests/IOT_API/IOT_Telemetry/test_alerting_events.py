from datetime import datetime, timedelta
from dateutil import parser
import pytest

from tests.db_support import psg_db


def device_rule(dt):
    sql_device = """SELECT
                      dvc_prf.id as profile_id,
                      rules.name as rule_name
                    FROM iot_platform.iot_device_profile dvc_prf
                      JOIN iot_platform.iot_objects_to_alerting_rules_link link ON link.object_id = dvc_prf.id
                      JOIN iot_platform.iot_alerting_rule rules ON rules.id = link.rule_id
                    WHERE dvc_prf.active_to > '%s 00:00:00.000000' and link.deleted is false 
                    and rules.deleted is false and link.updated < '%s 00:00:00.000000';""" % (dt, dt)

    ids = psg_db(sql=sql_device)

    ids_dict = [(row['profile_id'], row['rule_name']) for row in ids]

    return ids_dict


def threshold_rule(rule_name, profile_id):
    sql_threshold = """SELECT
                      crt.min_value,
                      crt.max_value,
                      crt_type.telemetry_type as sensor
                    FROM iot_platform.iot_device dvc
                      JOIN iot_platform.iot_device_profile dvc_prf ON dvc.id = dvc_prf.device_id
                      JOIN iot_platform.iot_objects_to_alerting_rules_link link ON link.object_id = dvc_prf.id
                      JOIN iot_platform.iot_alerting_rule rules ON rules.id = link.rule_id
                      JOIN iot_platform.iot_threshold_criteria crt ON crt.rule_id = rules.id AND crt.deleted is FALSE
                      AND crt.geofence_criteria_id ISNULL 
                      JOIN iot_platform.iot_threshold_criteria_type_dict crt_type ON crt.criteria_type_id = crt_type.id
                    WHERE rules.name = '%s' AND link.deleted is false AND dvc_prf.id = '%s';""" % (profile_id, rule_name)

    sensors = psg_db(sql=sql_threshold)

    sensor_dict = {row['sensor']: row for row in sensors}

    return sensor_dict


def device_events(profile_id, from_time):
    sql_event = """SELECT
                      events.record_date,
                      events.criteria_type as sensor,
                      events.telemetry_value as value
                    FROM iot_platform.iot_alerting_event events
                    WHERE profile_id = '%s' AND event_time > '%s'""" % (profile_id, from_time)
    events = psg_db(sql=sql_event)
    events_dict = dict()
    for row in events:
        if row['sensor'] in events_dict:
            events_dict[row['sensor']].update({row['record_date']: row})
        else:
            events_dict[row['sensor']] = {row['record_date']: row}

    return events_dict


@pytest.mark.parametrize('check_date', [str((datetime.now() - timedelta(days=0)).date())])
@pytest.mark.parametrize('uuid, rule_name', device_rule((datetime.now() - timedelta(days=0)).date()))
def test_device_sensors(iot_api, uuid, check_date, rule_name, expect):
    from_date = parser.parse(check_date)
    device_sensors = iot_api['device_cda'].get(url_param='telemetry/sensor?deviceId=%s&from=%sZ&to=%sZ' %
                                                         (uuid, from_date.isoformat(),
                                                          (datetime.utcnow() - timedelta(minutes=5)).isoformat()))
    rule_data = threshold_rule(uuid, rule_name)
    db_events = device_events(uuid, from_date)

    # verify only if there are TM data for device received
    if device_sensors:
        for sensor, limits in rule_data.items():
            for tm_event in device_sensors[sensor]:

                if sensor == 'battery':
                    tm_event['value'] = float(tm_event['value'])

                if tm_event['value'] and (tm_event['value'] < limits['min_value'] or tm_event['value'] > limits['max_value']):

                    # get the ISO format time when telemetry was received
                    event_time = datetime.utcfromtimestamp(tm_event['time'] / 1000)

                    if sensor in db_events:
                            if event_time in db_events[sensor]:
                                expect(db_events[sensor][event_time]['value'] == str(tm_event['value']),
                                       'Fail: uuid: %s, rule: %s: event value: api %s != %s db' %
                                       (uuid, rule_name, db_events[sensor][event_time]['value'], tm_event['value']))
                            else:
                                expect(event_time in db_events[sensor],
                                       'Fail: uuid: %s, rule: %s: missing event: value %s, time %s, criteria: %s' %
                                       (uuid, rule_name, tm_event['value'], event_time, limits))
                    else:
                        expect(sensor in db_events,
                               'Fail: uuid: %s, rule: %s: no sensor data: value %s, time %s, criteria: %s' %
                               (uuid, rule_name, tm_event['value'], event_time, limits))
