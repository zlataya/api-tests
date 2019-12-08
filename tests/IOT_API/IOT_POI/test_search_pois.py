import json
import pytest
from shapely.geometry import Point, Polygon

from tests.db_support import poi_info, poi_category_info, poi_address_info, geo_ids_with_poi


@pytest.mark.parametrize('name', poi_info('name'))
def test_search_pois_with_name(name, iot_api):

    body = {'name': name}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    for poi in pois['content']:
        assert poi['name'] == name, 'Fail: name: api %s != %s db' % (poi['name'], name)


@pytest.mark.parametrize('name', poi_info('left(name, 5)'))
def test_search_pois_with_part_name(name, iot_api):

    body = {'name': name}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    for poi in pois['content']:
        assert name.lower() in poi['name'].lower(), 'Fail: part name: api %s != %s' % (poi['name'], name)


@pytest.mark.parametrize('description', poi_info('description'))
def test_search_pois_with_description(description, iot_api):

    body = {'description': description}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    for poi in pois['content']:
        assert poi['description'] == description, 'Fail: description: api %s != %s db' % (poi['description'], description)


@pytest.mark.parametrize('description', poi_info('left(description, 5)'))
def test_search_pois_with_part_description(description, iot_api):

    body = {'description': description}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    for poi in pois['content']:
        assert description.lower() in poi['description'].lower(), 'Fail: part name: api %s != %s' % \
                                                                  (poi['description'], description)


def test_search_categories(iot_api):

    search_list = poi_category_info('name', limit=3)
    body = {'categories': search_list}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search?size=30')

    assert (pois['size'] == 30), \
        'Fail: id: number of devices returned api %s != 30' % pois['size']

    for poi in pois['content']:
        assert poi['category']['name'] in search_list, 'Fail: category is not found: api %s' % poi['category']['name']


@pytest.mark.parametrize('i_lon, i_lat', [list(map(int, json.loads(coordinates)['coordinates']))
                                          for coordinates in poi_info('st_asgeojson(coordinates)')])
def test_search_pois_with_location(i_lon, i_lat, iot_api):
    k = 1
    polygon = [[i_lon, i_lat], [i_lon + k, i_lat], [i_lon + k, i_lat + k], [i_lon, i_lat + k], [i_lon, i_lat]]
    body = {
        "location": {
            "type": "Polygon",
            "coordinates": [polygon]
        }
    }
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    p_shape = Polygon(polygon)

    assert (pois['size'] != 0), \
        'Fail: id: number of pois returned api %s is not 0' % pois['size']

    assert (pois['size'] <= 20), \
        'Fail: id: default number of devices returned api %s less or equal to 20' % pois['size']

    for poi in pois['content']:
        p = Point(poi['coordinates']['coordinates'])
        assert p.within(p_shape), 'Fail: device %s: lon, lat %s not within %s' % (poi['id'], p, p_shape)


@pytest.mark.parametrize('body_param, js_param, search_val',
                         [('addressLine1', 'line1', poi_address_info('left(line_1, 5)')),
                          ('addressLine2', 'line2', poi_address_info('left(line_2, 5)')),
                          ('addressPostalCode', 'postalCode', poi_address_info('left(postal_code, 5)')),
                          ('addressCity', 'city', poi_address_info('left(city, 5)')),
                          ('addressState', 'state', poi_address_info('left(state, 5)')),
                          ('addressCounty', 'county', poi_address_info('left(county, 5)')),
                          ('addressCountryCode', 'countryCode', poi_address_info('left(country_code, 5)'))])
def test_search_pois_with_part_address(body_param, js_param, search_val, iot_api):

    body = {body_param: search_val}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    assert len(pois) != 0, 'Fail: the list of elements is not empty api %s' % len(pois)

    for poi in pois['content']:
        assert search_val in poi['address'][js_param], 'Fail: part address:%s api %s != %s' % \
                                                                  (js_param, poi['address'][js_param], search_val)


def test_search_poi_geofences(iot_api):

    search_list = geo_ids_with_poi()
    body = {'geofences': search_list}
    pois = iot_api['poi'].post(json.dumps(body), url_param='search')

    assert len(pois) != 0, 'Fail: the list of elements is not empty api %s' % len(pois)

    for poi in pois['content']:
        assert any(g_id in [geo['id'] for geo in poi['geofences']] for g_id in search_list), \
            'Fail: group is not found: api %s' % poi['geofences']
