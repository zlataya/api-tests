import json
import pytest
from shapely.geometry import Point, Polygon

from tests.db_support import devices_info, vendors_info, groups_stat, locations_info, devices_count


@pytest.mark.parametrize('sn', devices_info('serial_number'))
def test_search_devices_with_sn(sn, iot_api):

    body = {'serialNumber': sn, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == 1), 'Fail: total elements api %s != %s db' % (len(devices), 1)
    device = devices[0]
    assert device['serialNumber'] == sn, 'Fail: SN: api %s != %s db' % (device['serialNumber'], sn)


@pytest.mark.parametrize('sn', devices_info('left(serial_number, 4)'))
def test_search_devices_with_part_sn(sn, iot_api):

    body = {'serialNumber': sn, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    db_count = devices_count('serial_number', sn)
    assert (len(devices) == db_count), \
        'Fail: id: default number of devices returned api %s = %s db' % (len(devices), db_count)

    for dvc in devices:
        assert sn in dvc['serialNumber'], 'Fail: SN: api %s != %s db' % (dvc['serialNumber'], sn)


@pytest.mark.parametrize('sid', devices_info('source_id'))
def test_search_devices_with_source_id(sid, iot_api):

    body = {'sourceId': sid, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == 1), 'Fail: total elements api %s != %s db' % (len(devices), 1)
    device = devices[0]
    assert device['sourceId'] == sid, 'Fail: source id: api %s != %s db' % (device['serialNumber'], sid)


@pytest.mark.parametrize('sid', devices_info('left(source_id, 3)'))
def test_search_devices_with_part_source_id(sid, iot_api):

    body = {'sourceId': sid, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    db_count = devices_count('source_id', sid)
    assert (len(devices) == db_count), \
        'Fail: default number of devices returned api %s = %s db' % (len(devices), db_count)

    for dvc in devices:
        assert sid in dvc['sourceId'], 'Fail: source id: api %s != %s db' % (dvc['sourceId'], sid)


@pytest.mark.parametrize('imei', devices_info('imei'))
def test_search_devices_with_imei(imei, iot_api):

    body = {'imei': imei, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == 1), 'Fail: total elements api %s != %s db' % (len(devices), 1)
    device = devices[0]
    assert device['imei'] == imei, 'Fail: imei: api %s != %s db' % (device['imei'], imei)


@pytest.mark.parametrize('imei', devices_info('left(imei, 4)'))
def test_search_devices_with_part_imei(imei, iot_api):

    body = {'imei': imei, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    db_count = devices_count('imei', imei)
    assert len(devices) == db_count, \
        'Fail: default number of devices returned api %s = %s db' % (len(devices), db_count)

    for dvc in devices:
        assert imei in dvc['imei'], 'Fail: imei: api %s != %s db' % (dvc['imei'], imei)


@pytest.mark.parametrize('body_name, db_name, js_name', [('sourceIds', 'source_id', 'sourceId'),
                                                         ('serialNumbers', 'serial_number', 'serialNumber'),
                                                         ('imeiList', 'imei', 'imei')])
def test_search_devices(iot_api, body_name, db_name, js_name):

    search_list = devices_info(db_name)
    body = {body_name: search_list, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == len(search_list)), 'Fail: total elements api %s != %s db' % (len(devices), len(search_list))

    for dvc in devices:
        assert dvc[js_name] in search_list, 'Fail: %s is not found: api %s' % (js_name, dvc[js_name])


@pytest.mark.parametrize('vendor_id, vendor_name, count', vendors_info())
def test_search_devices_with_vendor(vendor_id, vendor_name, count, iot_api):

    body = {'vendor': vendor_name.replace(' ', ''), 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == count), 'Fail: id: total devices found api %s != %s db' % (len(devices), count)

    for dvc in devices:
        assert dvc['vendor']['name'] == vendor_name, \
            'Fail: Found vendor name is not equal to search value: %s = api %s' % (vendor_name, dvc['vendor']['name'])
        assert dvc['vendor']['id'] == vendor_id, \
            'Fail: Found vendor id is not equal to search value: %s = api %s' % (vendor_id, dvc['vendor']['id'])


def test_search_devices_vendors(iot_api):

    search_list = [row[0] for row in vendors_info()[:3]]
    db_count = devices_count('vendor_id', search_list, active_flag=0)
    body = {'vendors': search_list}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all?size=100')

    assert (len(devices) == db_count), \
        'Fail: number of devices returned api %s != %s db' % (len(devices), db_count)

    for dvc in devices:
        assert dvc['vendor']['id'] in search_list, 'Fail: vendor is not found: api %s' % dvc['vendor']['id']


@pytest.mark.parametrize('group_id, count', groups_stat())
def test_search_devices_with_group(group_id, count, iot_api):

    body = {'groupId': group_id, 'active': True}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == count), \
        'Fail: id: total devices found api %s != %s db' % (len(devices), count)

    for dvc in devices:
        assert group_id in dvc['groupIds'], \
            'Fail: Found groups is not equal to search value: %s = api %s' % (group_id, dvc['groupIds'])


def test_search_devices_groups(iot_api):

    search_list = [row[0] for row in groups_stat()[:5]]
    db_count = devices_count('device_group_id', search_list, active_flag=0)

    body = {'groupIds': search_list}
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all?size=100')

    assert (len(devices) == db_count), 'Fail: id: total devices found api %s !=  %s' % (len(devices), db_count)

    for dvc in devices:
        assert any(group in dvc['groupIds'] for group in search_list), 'Fail: group is not found: api %s' % dvc['groupIds']


@pytest.mark.parametrize('coordinates, sn, sid', locations_info())
def test_search_device_with_location(coordinates, sn, sid, iot_api):
    lon, lat = json.loads(coordinates)['coordinates']

    k = 0.000001
    body = {
        "location": {
            "type": "Polygon",
            "coordinates": [[
                [lon - k, lat - k], [lon + k, lat - k], [lon + k, lat + k], [lon - k, lat + k], [lon - k, lat - k]
            ]]
        },
        'active': True
    }
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    assert (len(devices) == 1), 'Fail: id: total elements api %s != %s db' % (len(devices), 1)
    device = devices[0]
    assert device['sourceId'] == sid, 'Fail: SN: api %s != %s db' % (device['sourceId'], sid)
    assert device['serialNumber'] == sn, 'Fail: SN: api %s != %s db' % (device['serialNumber'], sid)
    assert device['coordinates']['coordinates'] == [lon, lat], 'Fail: lon, lat: api %s != %s db' % \
                                                               (device['coordinates']['coordinates'], [lon, lat])


@pytest.mark.parametrize('i_lon, i_lat', [list(map(int, json.loads(coordinates)['coordinates']))
                                          for coordinates in devices_info('st_asgeojson(coordinates)')])
def test_search_devices_with_location(i_lon, i_lat, iot_api):
    k = 0.5
    polygon = [[i_lon, i_lat], [i_lon + k, i_lat], [i_lon + k, i_lat + k], [i_lon, i_lat + k], [i_lon, i_lat]]
    body = {
        "location": {
            "type": "Polygon",
            "coordinates": [polygon]
        }
    }
    devices = iot_api['device'].post(json.dumps(body), url_param='search/all')

    p_shape = Polygon(polygon)

    db_count = devices_count(None, p_shape, active_flag=0)

    assert (len(devices) == db_count), \
        'Fail: id: default number of devices returned api %s = %s db' % (len(devices), db_count)

    for dvc in devices:
        p = Point(dvc['coordinates']['coordinates'])
        assert p.within(p_shape), 'Fail: device %s: lon, lat %s not within %s' % (dvc['id'], p, p_shape)
