import pytest

from tests.db_support import poi_category_info


@pytest.mark.parametrize('db_data', poi_category_info(param='row_to_json(cat)'))
def test_get_device_info(db_data, iot_api):

    api_data = iot_api['poi'].get(url_param='categories/%s' % db_data['id'])

    assert (db_data['id'] == api_data['id']), \
        'Fail: uuid: %s, id: api %s != %s db' % (db_data['id'], api_data['id'], db_data['id'])

    assert (db_data['name'] == api_data['name']), \
        'Fail: uuid: %s, name: api %s != %s db' % (db_data['id'], api_data['name'], db_data['name'])


@pytest.mark.parametrize('db_data', poi_category_info(param='row_to_json(cat)'))
def test_get_device_no_auth(db_data, iot_api):

    iot_api['poi'].headers = {}
    response = iot_api['poi'].get(url_param='categories/%s' % db_data['id'], no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: uuid %s status %s, message %s' % \
                                          (db_data['id'], response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac80337-659a-1ee3-8165-9fef0d610000', 404)])
def test_get_device_incorrect_url(iot_api, param, result):

    response = iot_api['poi'].get(url_param=param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)
