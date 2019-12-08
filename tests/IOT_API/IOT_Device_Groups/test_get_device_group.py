import pytest
from collections import defaultdict

from tests.db_support import groups_dto


@pytest.mark.parametrize('uuid, db_data', groups_dto(limit=5))
def test_get_device_group_info(uuid, db_data, iot_api):

    api_data = defaultdict(lambda: None, iot_api['device'].get(url_param='groups/%s' % uuid))

    assert (db_data['id'] == api_data['id']), \
        'Fail: uuid: %s, id: api %s != %s db' % (uuid, api_data['id'], db_data['id'])

    assert (db_data['name'] == api_data['name']), \
        'Fail: uuid: %s, name: api %s != %s db' % (uuid, api_data['name'], db_data['name'])

    assert (db_data['domain_id'] == api_data['domainId']), \
        'Fail: uuid: %s, domain id: api %s != %s db' % (uuid, api_data['domainId'], db_data['domain_id'])


@pytest.mark.parametrize('uuid', groups_dto(parametrize=False, limit=3))
def test_get_device_group_no_auth(uuid, iot_api):

    iot_api['device'].headers = {}
    response = iot_api['device'].get(url_param='groups/%s' % uuid, no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: uuid %s status %s, message %s' % \
                                          (uuid, response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac80337-6581-1625-8165-860491680030', 404)])
def test_get_device_group_incorrect_url(iot_api, param, result):

    response = iot_api['device'].get(url_param='groups/%s' % param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)
