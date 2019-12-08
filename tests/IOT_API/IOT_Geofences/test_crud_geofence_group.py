import pytest
import json
import random


@pytest.mark.parametrize('name', ['APITestOne', 'APITest2', 'APITestFive!',
                                  'API Test Long Group Name Eleven', 'API Test NULL'])
def test_crud_geofence_group(name, iot_api):

    # test create group method
    body = {'name': name}
    api_data = iot_api['geofence'].post(json.dumps(body), url_param='groups')

    uuid = api_data['id']
    assert api_data['name'] == name, 'Fail: uuid: %s, name: api %s != %s' % (uuid, api_data['name'], name)

    # test update group method
    new_name = '%s_%s' % (name, random.random())
    body = {'name': new_name}
    api_data = iot_api['geofence'].put(json.dumps(body), url_param='groups/%s' % uuid)

    assert api_data['name'] == new_name, \
        'Fail: uuid: %s, updated name: api %s != %s' % (uuid, api_data['name'], new_name)

    # test delete group method
    iot_api['geofence'].delete(url_param='groups/%s' % uuid)

    # try to get the deleted data for checking
    response = iot_api['geofence'].get(url_param='groups/%s' % uuid, no_check=True)

    assert response.status_code == 404, 'Fail: deleted group id was returned by API %s' % uuid


@pytest.mark.parametrize('body', [{'name': ''}, {}])
def test_create_geofence_group_with_empty_name(body, iot_api):

    # test create group method without name
    response = iot_api['geofence'].post(json.dumps(body), url_param='groups', no_check=True)

    status = response.status_code
    assert status == 422, 'Fail: group created with empty name: status code: %s, content: %s' % (status, response.text)

    message = json.loads(response.text)['message']
    assert message == "Field 'name': Geofence Group name must not be blank", 'Fail: message is not correct: %s' % message
