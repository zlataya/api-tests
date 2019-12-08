import pytest
import json

from tests.db_support import groups_dto


@pytest.mark.parametrize('name', ['APITestOne', 'APITest2', 'APITestFive!',
                                  'API Test Long Group Name Eleven', 'API Test NULL'])
def test_crud_device_group(name, iot_api):

    # test create group method
    body = {'name': name}
    api_data = iot_api['device'].post(json.dumps(body), url_param='groups')

    db_data = groups_dto(parametrize=False)
    uuid = api_data['id']

    assert api_data['name'] == name, 'Fail: uuid: %s, name: api %s != %s' % (uuid, api_data['name'], name)
    assert uuid in db_data, 'Fail: group id not in DB %s' % uuid
    assert api_data['domainId'] == db_data[uuid]['domain_id'], \
        'Fail: uuid: %s, domain id: api %s != %s db' % (uuid, api_data['domainId'], db_data[uuid]['domain_id'])

    # test update group method
    body = {'name': name[:-1]}
    iot_api['device'].put(json.dumps(body), url_param='groups/%s' % uuid)

    # get the updated data for checking
    api_data = iot_api['device'].get(url_param='groups/%s' % uuid)

    assert api_data['name'] == name[:-1], \
        'Fail: uuid: %s, updated name: api %s != %s' % (uuid, api_data['name'], name[:-1])

    # test delete group method
    iot_api['device'].delete(url_param='groups/%s' % uuid)

    # try to get the deleted data for checking
    response = iot_api['device'].get(url_param='groups/%s' % uuid, no_check=True)

    db_data = groups_dto(parametrize=False)

    assert uuid not in db_data, 'Fail: deleted group id was found in DB %s' % uuid
    assert response.status_code == 404, 'Fail: deleted group id was returned by API %s' % uuid


@pytest.mark.negative
@pytest.mark.parametrize('body', [{'name': ''}, {}])
def test_create_group_with_empty_name(body, iot_api):

    # test create group method without name
    response = iot_api['device'].post(json.dumps(body), url_param='groups', no_check=True)

    status = response.status_code
    message = json.loads(response.text)['message']

    assert status == 422, 'Fail: group created with empty name: status code: %s, content: %s' % (status, response.content)
    assert message == 'You must specify device group name!', 'Fail: error message is incorrect: message: %s' % message
