import pytest
import json
import random
from shapely.geometry import Polygon, Point
from shapely.ops import transform


@pytest.mark.parametrize('name, k',
                         [('APITestOne_polygon', 20), ('APITest2_polygon', 100),
                          ('APITestFive!_polygon', 1000), ('API Test Long point of interests Name Eleven Polygon', 1),
                          ('API Test NULL Polygon', 0.5)])
def test_crud_geofence_polygon(name, k, iot_api):
    i_lon = random.randint(50, 60)
    i_lat = random.randint(30, 50)

    polygon = [[i_lon, i_lat], [i_lon + k, i_lat], [i_lon + k, i_lat + k], [i_lon, i_lat + k], [i_lon, i_lat]]

    # test create geofence method
    body = {'name': name,
            "type": 0,
            "geometryData":
                {
                    "type": "Polygon",
                    "coordinates": [polygon]
                }
            }
    api_data = iot_api['geofence'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, geofence name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['type'] == 'POLYGON', 'Fail: uuid: %s, type: api %s != POLYGON' % (uuid, api_data['type'])
    assert api_data['geometryData'] == body['geometryData'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                                                             (uuid, api_data['geometryData']['coordinates'], [polygon])
    assert Polygon(api_data['geometryData']['coordinates'][0]).type == 'Polygon', \
        'Fail: uuid: %s, geofence shape: api %s != Polygon' % (uuid, Polygon(api_data['geometryData']['coordinates'][0]).type)

    # test update geofence method
    new_name = '%s_%s' % (name, random.random())
    new_polygon = transform(lambda x, y: [x + 20.0, y + 20.0], Polygon(polygon)).exterior.coords[:]
    body = {'name': new_name,
            "type": 0,
            "geometryData":
                {
                    "type": "Polygon",
                    "coordinates": [new_polygon]
                }
            }
    api_data = iot_api['geofence'].put(json.dumps(body), url_param=uuid)

    uuid = api_data['id']
    assert api_data['name'] == new_name, 'Fail: uuid: %s, new name: api %s != %s' % (uuid, api_data['name'], new_name)
    assert Polygon(api_data['geometryData']['coordinates'][0]).type == 'Polygon', \
        'Fail: uuid: %s, new shape: api %s != Polygon' % (uuid, Polygon(api_data['geometryData']['coordinates']).type)
    assert Polygon(api_data['geometryData']['coordinates'][0]).equals(Polygon(new_polygon)), \
        'Fail: uuid: %s, new coordinates: api %s != %s db' % (uuid, api_data['geometryData']['coordinates'], [new_polygon])

    # test delete geofence method
    iot_api['geofence'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['geofence'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted geofence id was returned by API %s' % uuid


@pytest.mark.parametrize('g_type, name, geo_type, coords, radius, message',
                         [(0, 'APITestOne', 'Point', Point(15, 30).buffer(10).exterior.coords[:], None, "Incorrect geometryData type"),
                          (0, 'APITestOne', 'Polygon', Point(15, 30).buffer(10).exterior.coords[:-1], None, "Incorrect geometryData type"),
                          (0, 'APITestOne', 'Polygon', Point(15, 30).buffer(10).exterior.coords[:], 10, "Polygon mustn't have radius"),
                          (1, 'APITestOne', 'Polygon', Point(15, 30).buffer(10).exterior.coords[:], None, "Geometry must be of type Point")])
def test_crud_geofence_polygon_negative(g_type, name, geo_type, coords, radius, message, iot_api):

    # test create group method
    body = {'name': name,
            "type": g_type,
            "geometryData":
                {
                    "type": geo_type,
                    "coordinates": [coords]
                },
            "radius": radius
            }
    response = iot_api['geofence'].post(json.dumps(body), no_check=True)

    status = response.status_code
    assert status in [400, 422], 'Fail: geofence created with incorrect body: status code: %s, content: %s' % (status, response.text)
    assert len(response.text) > 0, 'Fail: response content is empty: content: %s' % response

    api_response = json.loads(response.text)
    assert 'message' in api_response, 'Fail: empty message in response: %s' % api_response
    assert api_response['message'] == message, 'Fail: notification message is incorrect: api %s != %s ' % (api_response['message'], message)


@pytest.mark.parametrize('name, radius',
                         [('APITestOne_circle', 20), ('APITest2_circle', 100),
                          ('APITestFive!_circle', 1000), ('API Test Long point of interests Name Eleven Circle', 1.0),
                          ('API Test NULL Circle', 1.1)])
def test_crud_geofence_circle(name, radius, iot_api):
    i_lon = random.randint(50, 60)
    i_lat = random.randint(30, 50)

    point = [i_lon, i_lat]

    # test create group method
    body = {'name': name,
            "type": 1,
            "geometryData":
                {
                    "type": "Point",
                    "coordinates": point
                },
            "radius": radius
            }
    api_data = iot_api['geofence'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, geofence name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['type'] == 'CIRCLE', 'Fail: uuid: %s, type: api %s != CIRCLE' % (uuid, api_data['type'])
    assert api_data['geometryData'] == body['geometryData'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                                                             (uuid, api_data['geometryData']['coordinates'], point)
    assert api_data['radius'] == radius, 'Fail: uuid: %s, geofence radius: api %s != %s' % (uuid, api_data['radius'], radius)

    # test update geofence method
    new_name = '%s_%s' % (name, random.random())
    new_point = random.choices(range(100), k=2)
    new_radius = radius + 1
    body = {'name': new_name,
            "type": 1,
            "geometryData":
                {
                    "type": "Point",
                    "coordinates": new_point
                },
            "radius": new_radius
            }
    api_data = iot_api['geofence'].put(json.dumps(body), url_param=uuid)

    uuid = api_data['id']
    assert api_data['name'] == new_name, 'Fail: uuid: %s, new name: api %s != %s' % (uuid, api_data['name'], new_name)
    assert api_data['type'] == 'CIRCLE', 'Fail: uuid: %s, type: api %s != CIRCLE' % (uuid, api_data['type'])
    assert api_data['geometryData'] == body['geometryData'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                                                             (uuid, api_data['geometryData']['coordinates'], new_point)
    assert api_data['radius'] == new_radius, 'Fail: uuid: %s, geofence radius: api %s != %s' % (uuid, api_data['radius'], new_radius)

    # test delete geofence method
    iot_api['geofence'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['geofence'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted geofence id was returned by API %s' % uuid


@pytest.mark.parametrize('g_type, name, geo_type, coords, radius, message',
                         [(1, 'APITestOne', 'Polygon', [15, 30], 1, "Geometry must be of type Point"),
                          (1, 'APITestOne', 'Point', [Point(15, 30).buffer(10).exterior.coords[:]], 1, "Geometry coordinates for Circle should be in format [lat, lon]"),
                          (1, 'APITestOne', 'Point', [15, 30], None, "Radius must be greater than 1"),
                          (1, 'APITestOne', 'Point', [15, 30], 0.9, "Radius must be greater than 1"),
                          (0, 'APITestOne', 'Point', [15, 30], 1.0, "Geometry must be of type Polygon")])
def test_crud_geofence_circle_negative(g_type, name, geo_type, coords, radius, message, iot_api):

    # test create group method
    body = {'name': name,
            "type": g_type,
            "geometryData":
                {
                    "type": geo_type,
                    "coordinates": coords
                },
            "radius": radius
            }
    response = iot_api['geofence'].post(json.dumps(body), no_check=True)

    status = response.status_code
    assert status in [400, 422], 'Fail: geofence created with incorrect body: status code: %s, content: %s' % (status, response.text)
    assert len(response.text) > 0, 'Fail: response content is empty: content: %s' % response

    api_response = json.loads(response.text)
    assert 'message' in api_response, 'Fail: empty message in response: %s' % api_response
    assert api_response['message'] == message, 'Fail: notification message is incorrect: api %s != %s ' % (api_response['message'], message)


@pytest.mark.parametrize('name, k, radius',
                         [('APITestOne_polyline', 0.1, 20), ('APITest2_polyline', 1, 10000),
                          ('APITestFive!_polyline', 180, 1000),
                          ('API Test Long point of interests Name Eleven Polyline', 200, 1.0),
                          ('API Test NULL Polyline', 300, 1.1)])
def test_crud_geofence_polyline(name, radius, k, iot_api):
    i_lon = random.randint(50, 60)
    i_lat = random.randint(30, 50)

    polyline = [[i_lon, i_lat], [i_lon + k, i_lat], [i_lon + 2*k, i_lat], [i_lon + 3*k, i_lat], [i_lon + 4*k, i_lat]]

    # test create group method
    body = {'name': name,
            "type": 2,
            "geometryData":
                {
                    "type": "LineString",
                    "coordinates": polyline
                },
            "radius": radius
            }
    api_data = iot_api['geofence'].post(json.dumps(body))

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, geofence name: api %s != %s' % (uuid, api_data['name'], name)
    assert api_data['type'] == 'LINE', 'Fail: uuid: %s, type: api %s != LINE' % (uuid, api_data['type'])
    assert api_data['geometryData'] == body['geometryData'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                                                             (uuid, api_data['geometryData']['coordinates'], polyline)
    assert api_data['radius'] == radius, 'Fail: uuid: %s, geofence radius: api %s != %s' % (uuid, api_data['radius'], radius)

    # test update geofence method
    new_name = '%s_%s' % (name, random.random())
    new_polyline = [[10, 15], [11, 15], [12, 15]]
    new_radius = radius + 1
    body = {'name': new_name,
            "type": 2,
            "geometryData":
                {
                    "type": "LineString",
                    "coordinates": new_polyline
                },
            "radius": new_radius
            }
    api_data = iot_api['geofence'].put(json.dumps(body), url_param=uuid)

    uuid = api_data['id']
    assert api_data['name'] == new_name, 'Fail: uuid: %s, new name: api %s != %s' % (uuid, api_data['name'], new_name)
    assert api_data['type'] == 'LINE', 'Fail: uuid: %s, type: api %s != CIRCLE' % (uuid, api_data['type'])
    assert api_data['geometryData'] == body['geometryData'], 'Fail: uuid: %s, coordinates: api %s != %s db' % \
                                                             (uuid, api_data['geometryData']['coordinates'], new_polyline)
    assert api_data['radius'] == new_radius, 'Fail: uuid: %s, geofence radius: api %s != %s' % (uuid, api_data['radius'], new_radius)

    # test delete geofence method
    iot_api['geofence'].delete(url_param=uuid)

    # try to get the deleted data for checking
    response = iot_api['geofence'].get(url_param=uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted geofence id was returned by API %s' % uuid


@pytest.mark.parametrize('g_type, name, geo_type, coords, radius, message',
                         [(2, 'APITestOne', 'Polygon', [[10, 15], [10, 20], [20, 30]], 1, "Geometry type should be LineString"),
                          (2, 'APITestOne', 'LineString', [[10, 15], [10, 20], [20, 30], [10, 15]], 1, "Geometry type should be Polygon"),
                          (2, 'APITestOne', 'LineString', [[10, 15], [10, 20], [20, 30]], None, "Radius must be greater than 1"),
                          (2, 'APITestOne', 'LineString', [[10, 15], [10, 20], [20, 30]], 0.9, "Radius must be greater than 1"),
                          (0, 'APITestOne', 'LineString', [[10, 15], [10, 20], [20, 30]], 1.0, "Geometry must be of type Polygon")])
def test_crud_geofence_polyline_negative(g_type, name, geo_type, coords, radius, message, iot_api):

    # test create group method
    body = {'name': name,
            "type": g_type,
            "geometryData":
                {
                    "type": geo_type,
                    "coordinates": coords
                },
            "radius": radius
            }
    response = iot_api['geofence'].post(json.dumps(body), no_check=True)

    status = response.status_code
    assert status in [400, 422], 'Fail: geofence created with incorrect body: status code: %s, content: %s' % (status, response.text)
    assert len(response.text) > 0, 'Fail: response content is empty: content: %s' % response

    api_response = json.loads(response.text)
    assert 'message' in api_response, 'Fail: empty message in response: %s' % api_response
    assert api_response['message'] == message, 'Fail: notification message is incorrect: api %s != %s ' % (api_response['message'], message)


@pytest.mark.parametrize('g_type, name, geo_type, coords, radius, message',
                         [(0, '',   'Polygon', Point(15, 30).buffer(10).exterior.coords[:], None, "Geofence name cannot be blank"),
                          (0, None, 'Polygon', Point(15, 30).buffer(10).exterior.coords[:], None, "Geofence name cannot be blank"),
                          (0, 'APITestOne', '', Point(15, 30).buffer(10).exterior.coords[:], None, "Geofence type cannot be blank"),
                          (0, 'APITestOne', None, Point(15, 30).buffer(10).exterior.coords[:], None, "Geofence type cannot be blank"),
                          (3, 'APITestOne', 'Polygon', Point(15, 30).buffer(10).exterior.coords[:], None, "Geofence type cannot be blank"),
                          (None, 'APITestOne', 'Polygon', Point(15, 30).buffer(10).exterior.coords[:], None, "Geometry type must be provided"),
                          (0, 'APITestOne', 'Polygon', [], None, "Geofence coordinates must be provided"),
                          (0, 'APITestOne', 'Polygon', None, None, "Geofence coordinates must be provided"),
                          (2, 'APITestOne', 'Polyline', Point(15, 30).buffer(10).exterior.coords[:-1], '', "Geofence radius cannot be blank"),
                          (2, 'APITestOne', 'Polyline', Point(15, 30).buffer(10).exterior.coords[:-1], None, "Geofence radius cannot be blank")])
def test_crud_geofence_negative(g_type, name, geo_type, coords, radius, message, iot_api):

    # test create group method with negative scenarios
    temp = {'name': name,
            "type": g_type,
            "geometryData":
                {
                    "type": geo_type,
                    "coordinates": [coords]
                },
            "radius": radius}

    body = {k: v for k, v in temp.items() if v is not None}
    response = iot_api['geofence'].post(json.dumps(body), no_check=True)

    status = response.status_code

    assert status in [400, 422], 'Fail: geofence created with incorrect body: status code: %s, content: %s' % (status, response)
    assert len(response.text) > 0, 'Fail: response content is empty: content: %s' % response

    api_response = json.loads(response.text)

    assert 'message' in api_response, 'Fail: empty message in response: %s' % api_response
    assert api_response['message'] == message, 'Fail: notification message is incorrect: api %s != %s ' % (api_response['message'], message)
