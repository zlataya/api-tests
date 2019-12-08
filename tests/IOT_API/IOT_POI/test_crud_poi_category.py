import pytest
import json

from tests.db_support import poi_category_info


@pytest.mark.parametrize('name', ['APITestOne', 'APITest2', 'APITestFive!',
                                  'API Test Long Group Name Eleven', 'API Test NULL'])
def test_crud_poi_category(name, iot_api):

    # test create group method
    body = {'name': name}
    api_data = iot_api['poi'].post(json.dumps(body), url_param='categories')

    db_data = poi_category_info(param='id', limit='ALL')
    uuid = api_data['id']

    assert api_data['name'] == name, 'Fail: uuid: %s, name: api %s != %s' % (uuid, api_data['name'], name)
    assert uuid in db_data, 'Fail: category id not in DB %s' % uuid

    # test update group method
    body = {'name': name[:-1]}
    iot_api['poi'].put(json.dumps(body), url_param='categories/%s' % uuid)

    # get the updated data for checking
    api_data = iot_api['poi'].get(url_param='categories/%s' % uuid)

    assert api_data['name'] == name[:-1], \
        'Fail: uuid: %s, updated name: api %s != %s' % (uuid, api_data['name'], name[:-1])

    # test delete group method
    iot_api['poi'].delete(url_param='categories/%s' % uuid)

    # get the deleted data for checking
    response = iot_api['poi'].get(url_param='categories/%s' % uuid, no_check=True)

    db_data = poi_category_info(param='id', limit='ALL')

    assert uuid not in db_data, 'Fail: deleted category id was found in DB %s' % uuid
    assert response.status_code == 404, 'Fail: deleted category id was returned by API %s' % uuid


@pytest.mark.parametrize('body', [{'name': ''}, {}])
def test_create_poi_category_empty_name(body, iot_api):

    # test create group method without name
    response = iot_api['poi'].post(json.dumps(body), url_param='categories', no_check=True)

    status = response.status_code
    assert status == 400, 'Fail: category created with empty name: status code: %s, content: %s' % (status, response.content)

    message = json.loads(response.text)['message']
    assert message == 'You must specify category name!', 'Fail: category created with empty name: message: %s' % message
