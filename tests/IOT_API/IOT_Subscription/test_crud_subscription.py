import pytest
import json
import random


@pytest.fixture(scope='function')
def geo_id(iot_api):
    # create geofence
    body = {'name': 'APITesting_Events',
            "type": 0,
            "geometryData":
                {
                    "type": "Polygon",
                    "coordinates": [[[10, 20], [11, 20], [11, 21], [10, 21], [10, 20]]]
                }
            }
    geofence = iot_api['geofence'].post(json.dumps(body))

    yield geofence['id']

    # test delete geofence method
    iot_api['geofence'].delete(url_param=geofence['id'])


@pytest.mark.parametrize('name', ['APITestOne', 'APITest2', 'APITestFive!',
                                  'API Test Long point of interests Name Eleven', 'API Test NULL Polygon'])
def test_crud_telemetry_rule(name, iot_api):

    # test create rule method
    body = {'name': name,
            "telemetrySubscription": {"enabled": True}}

    api_data = iot_api['rule'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, rule name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['telemetrySubscription']['enabled'] is True, 'Fail: uuid: %s, subscription is enabled: %s' % \
                                                                 (uuid, api_data['telemetrySubscription']['enabled'])

    # test update rule method
    new_name = '%s_%s' % (name, random.random())
    body = api_data.copy()
    body['name'] = new_name
    body['telemetrySubscription']['enabled'] = False
    api_data = iot_api['rule'].put(json.dumps({"rule": body}), url_param=uuid)

    uuid = api_data['id']
    assert api_data['name'] == new_name, 'Fail: uuid: %s, rule name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['telemetrySubscription']['enabled'] is False, 'Fail: uuid: %s, subscription is disabled: %s' % \
                                                                  (uuid, api_data['telemetrySubscription']['enabled'])

    # test delete rule method
    iot_api['rule'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['rule'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted rule id was returned by API %s' % uuid


@pytest.mark.parametrize('name, event_type', [('APITestOne_geoEvent', 'in'),
                                              ('APITest2_geoEvent', 'out'),
                                              ('APITestFive!_geoEvent', 'both')])
def test_crud_geo_rule(name, event_type, geo_id, iot_api):

    # test create rule method
    body = {'name': name,
            "geofenceRules": [
                {
                    "geofenceId": geo_id,
                    "ruleType": event_type
                }
            ]}

    api_data = iot_api['rule'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, rule name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['geofenceRules'][0]['geofenceId'] == geo_id, \
        'Fail: uuid: %s, geofence is added to rule: api %s != %s input' % (uuid, api_data['geofenceRules'][0]['geofenceId'], geo_id)
    assert api_data['geofenceRules'][0]['ruleType'] == event_type, \
        'Fail: uuid: %s, rule type is correct: api %s != %s input' % (uuid, api_data['telemetrySubscription']['enabled'], event_type)
    assert api_data['telemetrySubscription'] is None, 'Fail: uuid: %s, telemetry subscription is not specified: %s' % \
                                                      (uuid, api_data['telemetrySubscription'])

    # test update rule method
    new_name = '%s_%s' % (name, random.random())
    body = api_data.copy()
    body['name'] = new_name
    body['description'] = 'GeoRule'
    body['telemetrySubscription'] = {"enabled": True}
    body['geofenceRules'][0]['ruleType'] = "both"
    api_data = iot_api['rule'].put(json.dumps({"rule": body}), url_param=uuid)

    uuid = api_data['id']
    assert api_data['name'] == new_name, 'Fail: uuid: %s, rule name: api %s != %s' % (uuid, api_data['name'], new_name)
    assert api_data['description'] == 'GeoRule', 'Fail: uuid: %s, rule description: api %s != GeoRule' % \
                                                 (uuid, api_data['description'])
    assert api_data['telemetrySubscription']['enabled'] is True, 'Fail: uuid: %s, subscription is disabled: %s' % \
                                                                 (uuid, api_data['telemetrySubscription']['enabled'])
    assert api_data['geofenceRules'][0]['ruleType'] == 'both', \
        'Fail: uuid: %s, rule type is correct: api %s != both' % (uuid, api_data['telemetrySubscription']['enabled'])

    # test delete rule method
    iot_api['rule'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['rule'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted rule id was returned by API %s' % uuid


@pytest.mark.negative
@pytest.mark.parametrize('name, geo_val, event_type, enabled, msg',
                         [('',   'valid', 'both', True, 'Rule Name cannot be an empty string'),
                          (None, True, 'both', True, 'Rule Name cannot be an empty string'),
                          ('APITestOne', '', 'both', True, 'GeofenceId should be populated'),
                          ('APITestOne', None, 'both', True, 'GeofenceId should be populated'),
                          ('APITestOne', 'valid', '', True, 'ruleType should be populated'),
                          ('APITestOne', 'valid', None, True, 'ruleType should be populated'),
                          ('APITestOne', 'valid', 'Both', True, 'ruleType can be only in, out or both'),
                          ('APITestOne', 'valid', 'both', '', 'enabled value missing in telemetrySubscription object'),
                          ('APITestOne', 'valid', 'both', None, 'enabled value missing in telemetrySubscription object')])
def test_crud_rule_negative(name, geo_val, event_type, enabled, msg, geo_id, iot_api):

    geofence = [geo_val, geo_id][geo_val == 'valid']
    temp = {'name': name,
            "geofenceRules": [
                {
                    "geofenceId": geofence,
                    "ruleType": event_type
                }
            ],
            "telemetrySubscription": {"enabled": enabled}}

    body = {k: v for k, v in temp.items() if v is not None}
    response = iot_api['rule'].post(json.dumps(body), no_check=True)

    status = response.status_code

    assert status in [400, 422], 'Fail: rule created with incorrect body: status code: %s, content: %s' % (status, response)
    assert len(response.text) > 0, 'Fail: response content is empty: content: %s' % response

    api_response = json.loads(response.text)

    assert 'message' in api_response, 'Fail: empty message in response: %s' % api_response
    assert api_response['message'] == msg, 'Fail: notification message is incorrect: api %s != %s ' % (api_response['message'], msg)
