import pytest
from collections import defaultdict
from shapely import wkb
from shapely.geometry import shape

from tests.db_support import geofence_dto


@pytest.mark.parametrize('geo_id', geofence_dto(parametrize=False, limit=5))
def test_get_geo_structure(geo_id, iot_api, json_template):

    geo_info = iot_api['geofence'].get(url_param=geo_id)
    template_info = json_template('GetGeofence')

    for key, val in geo_info.items():
        assert key in template_info, 'Fail: geofence structure: geo_id = %s: required structure = %s, missing key = %s' % \
                                     (geo_id, template_info, key)

        assert isinstance(val, type(geo_info[key])), 'Fail: geofence type: geo_id %s: required type %s, actual type %s' % \
                                                     (geo_id, val, geo_info[key])


@pytest.mark.parametrize('geo_id, db_data', geofence_dto(limit=5))
def test_get_geo_info(geo_id, db_data, iot_api):

    api_data = defaultdict(lambda: None, iot_api['geofence'].get(url_param=geo_id))

    assert db_data['id'] == api_data['id'], \
        'Fail: geo_id: %s, id: api %s != %s db' % (geo_id, api_data['id'], db_data['id'])

    assert db_data['name'] == api_data['name'], \
        'Fail: geo_id: %s, name: api %s != %s db' % (geo_id, api_data['name'], db_data['name'])

    assert db_data['type'] == api_data['type'], \
        'Fail: geo_id: %s, type: api %s != %s db' % (geo_id, api_data['type'], db_data['type'])

    assert db_data['description'] == api_data['description'], \
        'Fail: geo_id: %s, description: api %s != %s db' % (geo_id, api_data['description'], db_data['description'])

    # convert DB hex geometry and api json geometry to shapely object
    db_shape = wkb.loads(db_data['geometrydata'], hex=True)
    api_shape = shape(api_data['geometryData'])
    assert api_shape.equals(db_shape), 'Fail: geo_id: %s, geometry: api %s != %s db' % (geo_id, api_shape, db_shape)


@pytest.mark.parametrize('geo_id', geofence_dto(parametrize=False, limit=3))
def test_get_geofence_no_auth(geo_id, iot_api):

    iot_api['geofence'].headers = {}
    response = iot_api['geofence'].get(url_param=geo_id, no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: geo_id %s status %s, message %s' % \
                                          (geo_id, response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac83c05-64b2-16e7-8164-b26cc0af0010', 404)])
def test_get_geofence_incorrect_url(iot_api, param, result):

    response = iot_api['geofence'].get(url_param=param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)

