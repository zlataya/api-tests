import pytest
from collections import defaultdict
from dateutil import parser

from tests.db_support import devices_vendor_info, devices_dto


@pytest.mark.parametrize('profile_id, data', devices_dto())
def test_get_device_structure(data, profile_id, iot_api, json_template):

    device_info = iot_api['device'].get(url_param=profile_id)
    template_info = json_template('GetDevice%s' % data['vendor'][1])

    for key, val in device_info.items():
        assert key in template_info, \
            'Fail: structure failure: profile_id = %s: required structure = %s, missing key = %s' % \
            (profile_id, template_info, key)

        assert isinstance(val, type(device_info[key])), \
            'Fail: type failure: profile_id %s: required type %s, actual type %s' % \
            (profile_id, val, device_info[key])


@pytest.mark.parametrize('profile_id, db_data', devices_dto())
def test_get_device_info(profile_id, db_data, iot_api):

    api_data = defaultdict(lambda: None, iot_api['device'].get(url_param=profile_id))

    assert (db_data['id'] == api_data['id']), \
        'Fail: profile_id: %s, id: api %s != %s db' % (profile_id, api_data['id'], db_data['profile_id'])

    assert (db_data['sourceid'] == api_data['sourceId']), \
        'Fail: profile_id: %s, source id: api %s != %s db' % (profile_id, api_data['sourceId'], db_data['sourceid'])

    assert (db_data['imei'] == api_data['imei']), \
        'Fail: profile_id: %s, imei: api %s != %s db' % (profile_id, api_data['imei'], db_data['imei'])

    assert (db_data['vendor'][0] == api_data['vendor']['id']), \
        'Fail: profile_id: %s, vendor id: api %s != %s db' % (profile_id, api_data['vendor']['id'], db_data['vendor'][0])

    if db_data['vendor'][1] == 'Device':
        assert ('Drive App' == api_data['vendor']['name']), \
            'Fail: profile_id: %s, vendor name: api %s != %s db' % (
            profile_id, api_data['vendor']['name'], db_data['vendor'][1])
    else:
        assert (db_data['vendor'][1].lower() == api_data['vendor']['name'].lower()), \
            'Fail: profile_id: %s, vendor name: api %s != %s db' % (
            profile_id, api_data['vendor']['name'], db_data['vendor'][1])

    assert (db_data['created'].replace(microsecond=0) == parser.parse(api_data['created'], ignoretz=True)), \
        'Fail: profile_id: %s, created time: api %s != %s db' % (profile_id, api_data['created'], db_data['created'])

    assert (db_data['updated'].replace(microsecond=0) == parser.parse(api_data['updated'], ignoretz=True)), \
        'Fail: profile_id: %s, updated time: api %s != %s db' % (profile_id, api_data['updated'], db_data['updated'])

    # if telemetryupdated/sourcetelemetryupdated is none, it will be asserted as it is
    if api_data['telemetryUpdated']:

        assert (db_data['telemetryupdated'] == parser.parse(api_data['telemetryUpdated'], ignoretz=True)), \
            'Fail: profile_id: %s, telemetry updated time: api %s != %s db' % (
                profile_id, api_data['telemetryUpdated'], db_data['telemetryupdated'])

        assert (db_data['sourcetelemetryupdated'] == parser.parse(api_data['sourceTelemetryUpdated'], ignoretz=True)), \
            'Fail: profile_id: %s, source telemetry updated time: api %s != %s db' % (
                profile_id, api_data['sourceTelemetryUpdated'], db_data['sourcetelemetryupdated'])
    else:

        assert db_data['telemetryupdated'] == api_data['telemetryUpdated'], \
            'Fail: profile_id: %s, telemetry updated time: api %s != %s db' % (
                profile_id, api_data['telemetryUpdated'], db_data['telemetryupdated'])

        assert db_data['sourcetelemetryupdated'] == api_data['sourceTelemetryUpdated'], \
            'Fail: profile_id: %s, source telemetry updated time: api %s != %s db' % (
                profile_id, api_data['sourceTelemetryUpdated'], db_data['sourcetelemetryupdated'])


@pytest.mark.parametrize('profile_id, db_data', devices_vendor_info('zillion'))
def test_get_zillion_info(profile_id, db_data, iot_api):

    device_info = defaultdict(lambda: None, iot_api['device'].get(url_param=profile_id))

    assert (db_data['profile_id'] == device_info['id']), \
        'Fail: profile_id: %s, id: api %s != %s db' % (profile_id, device_info['id'], db_data['profile_id'])

    assert (db_data['client_id'] == device_info['clientId']), 'Fail: profile_id: %s, client id: api %s != %s db' % (
            profile_id, device_info['clientId'], db_data['client_id'])

    assert (db_data['client_name'] == device_info['clientName']), 'Fail: profile_id: %s, client name: api %s != %s db' % (
            profile_id, device_info['clientName'], db_data['client_name'])

    assert (db_data['name'] == device_info['name']), 'Fail: profile_id: %s, name: api %s != %s db' % (
            profile_id, device_info['name'], db_data['name'])

    assert (db_data['tag'] == device_info['tag']), 'Fail: profile_id: %s, tag: api %s != %s db' % (
            profile_id, device_info['tag'], db_data['tag'])

    assert (db_data['wake_interval'] == device_info['wakeInterval']), 'Fail: profile_id: %s, wake interval: api %s != %s db' % (
            profile_id, device_info['wakeInterval'], db_data['wake_interval'])

    assert (db_data['type_id'] == device_info['typeId']), 'Fail: profile_id: %s, type id: api %s != %s db' % (
            profile_id, device_info['typeId'], db_data['type_id'])


@pytest.mark.parametrize('profile_id, db_data', devices_vendor_info('mecomo'))
def test_get_mecomo_info(profile_id, db_data, iot_api):

    device_info = defaultdict(lambda: None, iot_api['device'].get(url_param=profile_id))

    assert db_data['profile_id'] == device_info['id'], \
        'Fail: profile_id: %s, id: api %s != %s db' % (profile_id, device_info['id'], db_data['profile_id'])

    assert db_data['gps_id'] == device_info['gpsId'], \
        'Fail: profile_id: %s, gps id: api %s != %s db' % (profile_id, device_info['gpsId'], db_data['gps_id'])

    assert (db_data['msi_sdn'] == device_info['msisdn']), \
        'Fail: profile_id: %s, msi sdn %s != %s db' % (profile_id, device_info['msisdn'], db_data['msi_sdn'])

    assert db_data['name'] == device_info['name'], \
        'Fail: profile_id: %s, name: api %s != %s db' % (profile_id, device_info['name'], db_data['name'])

    assert db_data['network_operator'] == device_info['networkOperator'], \
        'Fail: profile_id: %s, network operator: api %s != %s db' % (profile_id, device_info['provider'], db_data['provider'])

    assert db_data['object_id'] == device_info['objectId'], \
        'Fail: profile_id: %s, object id: api %s != %s db' % (profile_id, device_info['objectId'], db_data['object_id'])

    assert db_data['object_name'] == device_info['objectName'], \
        'Fail: profile_id: %s, object name: api %s != %s db' % (profile_id, device_info['objectName'], db_data['object_name'])

    assert db_data['provider'] == device_info['provider'], \
        'Fail: profile_id: %s, provider: api %s != %s db' % (profile_id, device_info['provider'], db_data['provider'])

    assert db_data['provider_name'] == device_info['providerName'], \
        'Fail: profile_id: %s, provider name: api %s != %s db' % \
        (profile_id, device_info['providerName'], db_data['provider_name'])

    assert db_data['reg_date'] == parser.parse(device_info['regDate'], ignoretz=True), \
        'Fail: profile_id: %s, reg date: api %s != %s db' % (profile_id, device_info['regDate'], db_data['reg_date'])

    assert db_data['sim_card'] == device_info['simCard'], \
        'Fail: profile_id: %s, sim card: api %s != %s db' % (profile_id, device_info['simCard'], db_data['sim_card'])


@pytest.mark.parametrize('profile_id, data', devices_vendor_info('kirsen'))
def test_get_kirsen_info(profile_id, data, iot_api):

    device_info = defaultdict(lambda: None, iot_api['device'].get(url_param=profile_id))

    assert (data['profile_id'] == device_info['id']), \
        'Fail: profile_id: %s, id: api %s != %s db' % (profile_id, device_info['id'], data['profile_id'])

    assert (data['vendor_name'] == device_info['kirsenName']), 'Fail: profile_id: %s, vendor name: api %s != %s db' % (
            profile_id, device_info['kirsenName'], data['vendor_name'])

    assert (data['client_name'] == device_info['description']), 'Fail: profile_id: %s, client name: api %s != %s db' % (
            profile_id, device_info['description'], data['client_name'])

    assert (data['container'] == device_info['container']), 'Fail: profile_id: %s, name: api %s != %s db' % (
            profile_id, device_info['container'], data['container'])

    assert (data['temp_min'] == device_info['tempMin']), 'Fail: profile_id: %s, temp min: api %s != %s db' % (
            profile_id, device_info['tempMin'], data['temp_min'])

    assert (data['temp_max'] == device_info['tempMax']), 'Fail: profile_id: %s, temp max: api %s != %s db' % (
            profile_id, device_info['tempMax'], data['temp_max'])

    assert (data['temp_mode'] == device_info['tempMode']), 'Fail: profile_id: %s, temp mode: api %s != %s db' % (
            profile_id, device_info['tempMode'], data['temp_mode'])

    assert (data['tilt_max'] == device_info['tiltMax']), 'Fail: profile_id: %s, tilt max: api %s != %s db' % (
            profile_id, device_info['tiltMax'], data['tilt_max'])

    assert (data['tilt_mode'] == device_info['tiltMode']), 'Fail: profile_id: %s, tilt mode: api %s != %s db' % (
            profile_id, device_info['tiltMode'], data['tilt_mode'])

    assert (data['vibration_max'] == device_info['vibrationMax']), 'Fail: profile_id: %s, vibration max: api %s != %s db' % (
            profile_id, device_info['vibrationMax'], data['vibration_max'])

    assert (data['vibration_mode'] == device_info['vibrationMode']), 'Fail: profile_id: %s, vibration mode: api %s != %s db' % (
            profile_id, device_info['vibrationMode'], data['vibration_mode'])

    assert (data['shock_max'] == device_info['shockMax']), 'Fail: profile_id: %s, shock max: api %s != %s db' % (
            profile_id, device_info['shockMax'], data['shock_max'])

    assert (data['shock_mode'] == device_info['shockMode']), 'Fail: profile_id: %s, shock mode: api %s != %s db' % (
            profile_id, device_info['shockMode'], data['shock_mode'])

    assert (data['communication_period'] == device_info['communicationPeriod']), 'Fail: profile_id: %s, communication period: api %s != %s db' % (
            profile_id, device_info['communicationPeriod'], data['communication_period'])

    assert (data['gps_period'] == device_info['gpsPeriod']), 'Fail: profile_id: %s, gps period: api %s != %s db' % (
            profile_id, device_info['gpsPeriod'], data['gps_period'])

    assert (data['gps_timeout'] == device_info['gpsTimeout']), 'Fail: profile_id: %s, gps timeout: api %s != %s db' % (
            profile_id, device_info['gpsTimeout'], data['gps_timeout'])

    assert (data['temperature_period'] == device_info['temperaturePeriod']), 'Fail: profile_id: %s, temperature period: api %s != %s db' % (
            profile_id, device_info['temperaturePeriod'], data['temperature_period'])

    assert (data['accel_period'] == device_info['accelPeriod']), 'Fail: profile_id: %s, accel period: api %s != %s db' % (
            profile_id, device_info['accelPeriod'], data['accel_period'])

    assert (data['hardware'] == device_info['hardware']), 'Fail: profile_id: %s, hardware: api %s != %s db' % (
            profile_id, device_info['hardware'], data['hardware'])

    assert (data['firmware'] == device_info['firmware']), 'Fail: profile_id: %s, wake interval: api %s != %s db' % (
            profile_id, device_info['firmware'], data['firmware'])

    assert (data['alerts'] == device_info['alerts']), 'Fail: profile_id: %s, alerts: api %s != %s db' % (
            profile_id, device_info['alerts'], data['alerts'])

    assert (data['command'] == device_info['command']), 'Fail: profile_id: %s, command: api %s != %s db' % (
            profile_id, device_info['command'], data['command'])

    assert (data['demo_mode'] == device_info['demoMode']), 'Fail: profile_id: %s, demo mode: api %s != %s db' % (
            profile_id, device_info['demoMode'], data['demo_mode'])

    assert (data['forced_mode'] == device_info['forcedMode']), 'Fail: profile_id: %s, forced mode: api %s != %s db' % (
            profile_id, device_info['forcedMode'], data['forced_mode'])

    assert (data['train_mode'] == device_info['trainMode']), 'Fail: profile_id: %s, train mode: api %s != %s db' % (
            profile_id, device_info['trainMode'], data['train_mode'])


@pytest.mark.parametrize('profile_id, db_data', devices_vendor_info('onasset'))
def test_get_mecomo_info(profile_id, db_data, iot_api):

    device_info = defaultdict(lambda: None, iot_api['device'].get(url_param=profile_id))

    assert db_data['profile_id'] == device_info['id'], \
        'Fail: profile_id: %s, id: api %s != %s db' % (profile_id, device_info['id'], db_data['profile_id'])

    assert (db_data['name'] == device_info['name']), 'Fail: profile_id: %s, name: api %s != %s db' % (
            profile_id, device_info['name'], db_data['name'])


@pytest.mark.parametrize('profile_id, db_data', devices_dto())
def test_get_device_no_auth(profile_id, db_data, iot_api):

    iot_api['device'].headers = {}
    response = iot_api['device'].get(url_param=profile_id, no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: profile_id %s status %s, message %s' % \
                                          (profile_id, response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac83b0c-644d-1825-8164-4d223abf094d', 404)])
def test_get_device_incorrect_url(iot_api, param, result):

    response = iot_api['device'].get(url_param=param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)
