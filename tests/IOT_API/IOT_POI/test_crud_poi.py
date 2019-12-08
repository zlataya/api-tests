import pytest
import json
import random
from collections import defaultdict

from tests.db_support import poi_category_info


@pytest.mark.parametrize('cat_id, name',
                         [(n, c) for n, c in
                          zip(poi_category_info('id'), ['APITestOne', 'APITest2', 'APITestFive!',
                                                        'API Test Long point of interests Name Eleven', 'API Test NULL'])])
def test_crud_poi(name, cat_id, iot_api):

    lon = round(37 + random.random(), 5)
    lat = round(55 + random.random(), 5)

    # test create POI method
    body = {'name': name,
            "category": {"id": cat_id},
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [lon, lat]

                }
            }
    api_data = iot_api['poi'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, poi name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['category']['id'] == cat_id, 'Fail: uuid: %s, category id: api %s != %s' % \
                                                 (uuid, api_data['category']['id'], cat_id)
    assert api_data['coordinates']['coordinates'] == [lon, lat], \
        'Fail: uuid: %s, poi coordinates: api %s != %s db' % (uuid, api_data['coordinates']['coordinates'], [lon, lat])

    # test update poi method
    new_name = '%s_%s' % (name, random.random())
    new_category = poi_category_info('id', limit=11)[-1]
    body = {'name': new_name,
            "category": {"id": new_category},
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [37, 55]

                }
            }
    api_data = iot_api['poi'].put(json.dumps(body), url_param=uuid)

    assert api_data['name'] == new_name, \
        'Fail: uuid: %s, updated name: api %s != %s' % (uuid, api_data['name'], new_name)
    assert api_data['category']['id'] == new_category, \
        'Fail: uuid: %s, category id: api %s != %s db' % (uuid, api_data['category']['id'], new_category)
    assert api_data['coordinates']['coordinates'] == [37, 55], \
        'Fail: uuid: %s, poi coordinates: api %s != %s db' % (uuid, api_data['coordinates']['coordinates'], [37, 55])

    # test delete poi method
    iot_api['poi'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['poi'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted POI id was returned by API %s' % uuid


@pytest.mark.parametrize('address', [defaultdict(lambda: None, {"city": "Glendale", "countryCode": "US"}),
                                     {"line1": "5901 W Behrend Dr",
                                      "line2": "Apt 2103",
                                      "postalCode": "85308",
                                      "city": "Glendale",
                                      "county": "N/A",
                                      "state": "AZ",
                                      "countryCode": "US"}])
def test_crud_poi_all_parameters(iot_api, address):

    # test create POI method
    body = {'name': 'TEST POI',
            "category": {"id": poi_category_info('id', limit=1)[0]},
            "description": "Testing POI",
            "address": address,
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [round(37 + random.random(), 5), round(55 + random.random(), 5)]

                }
            }
    api_data = iot_api['poi'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['description'] == 'Testing POI', \
        'Fail: uuid: %s, poi description: api %s != %s' % (uuid, api_data['description'], 'Testing POI')
    for key, api_val in api_data['address'].items():
        assert api_val == address[key], \
            'Fail: uuid: %s, poi address %s: api %s != %s' % (uuid, key, api_val, address[key])

    # test update poi method
    body = {"address": {"city": "Moscow",
                        "countryCode": "RU"},
            "description": "Testing POI updated"}
    api_data = iot_api['poi'].put(json.dumps(body), url_param=uuid)

    assert api_data['address']['city'] == 'Moscow', \
        'Fail: uuid: %s, updated city: api %s != %s' % (uuid, api_data['address']['city'], 'Moscow')
    assert api_data['address']['countryCode'] == 'RU', \
        'Fail: uuid: %s, updated countryCode: api %s != %s' % (uuid, api_data['address']['countryCode'], 'RU')
    assert api_data['description'] == 'Testing POI updated', \
        'Fail: uuid: %s, updated description: api %s != %s' % (uuid, api_data['description'], 'Testing POI updated')

    # test delete POI method
    iot_api['poi'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['poi'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted POI id was returned by API %s' % uuid


@pytest.mark.parametrize('address', [{"city": "Chicago", "state": 'IL'}, {"state": 'IL', "countryCode": "US"},
                                     {"city": '', "countryCode": 'US'}, {"city": "Glendale", "countryCode": ''},
                                     {"city": "Glendale", "countryCode": "USA"},
                                     {"city": "Glendale", "countryCode": "AA"}])
def test_create_poi_with_part_address(iot_api, address):

    # test create POI method
    body = {'name': 'TEST POI',
            "category": {"id": poi_category_info('id', limit=1)[0]},
            "description": "Testing POI",
            "address": address,
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [round(37 + random.random(), 5), round(55 + random.random(), 5)]

                }
            }
    response = iot_api['poi'].post(json.dumps(body), no_check=True)
    status = response.status_code

    assert status == 422, 'Fail: poi created with incorrect address: status code: %s, content: %s' % (status, response.content)

    message = json.loads(response.text)['message']
    assert message != 'The name already exists', 'Fail: poi created with empty name: message: %s, content: %s' % (status, message)


@pytest.mark.parametrize('name_flag', ['empty', 'absent'])
def test_create_poi_with_empty_name(iot_api, name_flag):

    # test create POI method
    body = {"category": {"id": poi_category_info('id', limit=1)[0]},
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [round(37 + random.random(), 5), round(55 + random.random(), 5)]

                }
            }
    if name_flag == 'empty':
        body['name'] = ''
    response = iot_api['poi'].post(json.dumps(body), no_check=True)
    status = response.status_code
    message = response.text

    assert status == 400, 'Fail: poi created with empty name: status code: %s, content: %s' % (status, message)
    assert len(message) > 0, 'Fail: poi created with empty name: message: %s, content: %s' % (status, message)


@pytest.mark.parametrize('category_flag', ['empty', 'absent'])
def test_create_poi_with_empty_category(iot_api, category_flag):

    # test create POI method
    body = {'name': 'TEST POI',
            "coordinates":
                {
                    "type": "Point",
                    "coordinates": [round(37 + random.random(), 5), round(55 + random.random(), 5)]

                }
            }
    if category_flag == 'empty':
        body['category'] = {}
    response = iot_api['poi'].post(json.dumps(body), no_check=True)
    status = response.status_code
    message = response.text

    assert status == 400, 'Fail: poi created with no category: status code: %s, content: %s' % (status, message)
    assert len(message) > 0, 'Fail: poi created with no category: empty message: %s, content: %s' % (status, message)


@pytest.mark.parametrize('coordinates_flag', ['empty', 'absent'])
def test_create_poi_with_empty_coordinates(iot_api, coordinates_flag):

    # test create POI method
    body = {'name': 'TEST POI',
            "category": {"id": poi_category_info('id', limit=1)[0]},
            }
    if coordinates_flag == 'empty':
        body['coordinates'] = {}
    response = iot_api['poi'].post(json.dumps(body), no_check=True)
    status = response.status_code
    message = response.text

    assert status == 400, 'Fail: poi created with no coordinates: status code: %s, content: %s' % (status, message)
    assert len(message) > 0, 'Fail: poi created with no coordinates: empty message: %s, content: %s' % (status, message)