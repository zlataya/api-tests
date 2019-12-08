import json

from tests.db_support import geo_id_name_all


def test_get_geofences_info(iot_api):
    geos = iot_api['geofence'].get()

    # get geo id and name
    geo_ids = geo_id_name_all()

    assert (len(geo_ids) == geos['totalElements']), \
        'Fail: id: total elements api %s != %s db' % (geos['totalElements'], len(geo_ids))

    for geo in geos['content']:
        guid = geo['id']
        assert guid in geo_ids, 'Fail: poi id: api %s != %s db' % (guid, geo_ids)
        assert geo['name'] == geo_ids[guid]['name'], \
            'Fail: geofence id: %s, name: api %s != %s db' % (guid, geo['name'], geo_ids[guid]['name'])


def test_get_geofences_no_auth(iot_api):

    iot_api['geofence'].headers = {}

    response = iot_api['geofence'].get(no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
