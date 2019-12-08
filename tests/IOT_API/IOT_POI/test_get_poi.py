import pytest
from collections import defaultdict

from tests.db_support import poi_dto


@pytest.mark.parametrize('poi_id', poi_dto())
def test_get_poi_structure(poi_id, iot_api, json_template):

    poi_info = iot_api['poi'].get(url_param=poi_id)
    template_info = json_template('GetPOI')

    for key, val in poi_info.items():
        assert key in template_info, 'Fail: poi structure: poi_id = %s: required structure = %s, missing key = %s' % \
                                     (poi_id, template_info, key)

        assert isinstance(val, type(poi_info[key])), 'Fail: poi type: poi_id %s: required type %s, actual type %s' % \
                                                     (poi_id, val, poi_info[key])


@pytest.mark.parametrize('poi_id, db_data', poi_dto(parametrize=True))
def test_get_poi_info(poi_id, db_data, iot_api):

    api_data = defaultdict(lambda: None, iot_api['poi'].get(url_param=poi_id))

    assert (db_data['id'] == api_data['id']), \
        'Fail: poi_id: %s, id: api %s != %s db' % (poi_id, api_data['id'], db_data['poi_id'])

    assert (db_data['category_id'] == api_data['category']['id']), \
        'Fail: poi_id: %s, category id: api %s != %s db' % (poi_id, api_data['category']['id'], db_data['category_id'])

    assert (db_data['category'] == api_data['category']['name']), \
        'Fail: poi_id: %s, category id: api %s != %s db' % (poi_id, api_data['category']['name'], db_data['category'])

    assert (db_data['name'] == api_data['name']), \
        'Fail: poi_id: %s, poi name: api %s != %s db' % (poi_id, api_data['name'], db_data['name'])

    assert (db_data['description'] == api_data['description']), \
        'Fail: poi_id: %s, description: api %s != %s db' % (poi_id, api_data['description'], db_data['description'])

    if db_data['address']:
        assert (db_data['address']['line_1'] == api_data['address']['line1']), \
            'Fail: poi_id: %s, address line1: api %s != %s db' % (poi_id, api_data['address']['line1'], db_data['address']['line_1'])
        assert (db_data['address']['line_2'] == api_data['address']['line2']), \
            'Fail: poi_id: %s, address line2: api %s != %s db' % (poi_id, api_data['address']['line2'], db_data['address']['line_2'])
        assert (db_data['address']['postal_code'] == api_data['address']['postalCode']), \
            'Fail: poi_id: %s, address postalCode: api %s != %s db' % (poi_id, api_data['address']['postalCode'], db_data['address']['postal_code'])
        assert (db_data['address']['city'] == api_data['address']['city']), \
            'Fail: poi_id: %s, address city: api %s != %s db' % (poi_id, api_data['address']['city'], db_data['address']['city'])
        assert (db_data['address']['county'] == api_data['address']['county']), \
            'Fail: poi_id: %s, address county: api %s != %s db' % (poi_id, api_data['address']['county'], db_data['address']['county'])
        assert (db_data['address']['state'] == api_data['address']['state']), \
            'Fail: poi_id: %s, address state: api %s != %s db' % (poi_id, api_data['address']['state'], db_data['address']['state'])
        assert (db_data['address']['country_code'] == api_data['address']['countryCode']), \
            'Fail: poi_id: %s, address state: api %s != %s db' % (poi_id, api_data['address']['countryCode'], db_data['address']['country_code'])
    else:
        assert (db_data['address'] == api_data['address']), \
            'Fail: poi_id: %s, address: api %s != %s db' % (poi_id, api_data['address'], db_data['address'])

    assert (db_data['coordinates'] == api_data['coordinates']), \
        'Fail: poi_id: %s, coordinates: api %s != %s db' % (poi_id, api_data['coordinates'], db_data['coordinates'])

    if db_data['geofences']:
        assert (len(db_data['geofences']) == len(api_data['geofences'])), \
            'Fail: poi_id: %s, count of geofences: api %s != %s db' % (poi_id, len(api_data['geofences']), len(db_data['geofences']))
        for geo_db_id, geo_api in zip(db_data['geofences'], api_data['geofences']) :
            assert (geo_api['id'] == geo_db_id), \
                'Fail: poi_id: %s, geofence id: api %s != %s db' % (poi_id, geo_api['id'], geo_db_id)
    else:
        assert (db_data['geofences'] == api_data['geofences']), \
            'Fail: poi_id: %s, geofences: api %s != %s db' % (poi_id, api_data['geofences'], db_data['geofences'])


@pytest.mark.parametrize('poi_id', poi_dto())
def test_get_poi_no_auth(poi_id, iot_api):

    iot_api['poi'].headers = {}
    response = iot_api['poi'].get(url_param=poi_id, no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: poi_id %s status %s, message %s' % \
                                          (poi_id, response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac83c05-64b2-16e7-8164-b26cc0af0010', 404)])
def test_get_poi_incorrect_url(iot_api, param, result):

    response = iot_api['poi'].get(url_param=param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)

