import pytest
from collections import defaultdict

from tests.db_support import subscription_dto


@pytest.mark.parametrize('rule_id', subscription_dto(parametrize=False, limit=5))
def test_get_subscription_structure(rule_id, iot_api, json_template):

    rule_info = iot_api['rule'].get(url_param=rule_id)
    template_info = json_template('GetRule')

    for key, val in rule_info.items():
        assert key in template_info, 'Fail: rule structure: rule_id = %s: required structure = %s, missing key = %s' % \
                                     (rule_id, template_info, key)

        assert isinstance(val, type(rule_info[key])), 'Fail: rule type: rule_id %s: required type %s, actual type %s' % \
                                                      (rule_id, val, rule_info[key])


@pytest.mark.parametrize('rule_id, db_data', subscription_dto(parametrize=True, limit=10))
def test_get_poi_info(rule_id, db_data, iot_api):

    api_data = defaultdict(lambda: None, iot_api['rule'].get(url_param=rule_id))

    assert (db_data['rule_id'] == api_data['id']), \
        'Fail: rule_id: %s, id: api %s != %s db' % (rule_id, api_data['id'], db_data['rule_id'])

    assert (db_data['name'] == api_data['name']), \
        'Fail: rule_id: %s, name: api %s != %s db' % (rule_id, api_data['name'], db_data['name'])

    assert (db_data['description'] == api_data['description']), \
        'Fail: rule_id: %s, description: api %s != %s db' % (rule_id, api_data['description'], db_data['description'])


@pytest.mark.parametrize('rule_id', subscription_dto(parametrize=False, limit=5))
def test_get_device_no_auth(rule_id, iot_api):

    iot_api['rule'].headers = {}
    response = iot_api['rule'].get(url_param=rule_id, no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: rule_id %s status %s, message %s' % \
                                          (rule_id, response.status_code, response.content)


@pytest.mark.parametrize('param, result', [('1', 400), ('0ac83c05-64b2-16e7-8164-b26cc0af0010', 404)])
def test_get_device_incorrect_url(iot_api, param, result):

    response = iot_api['rule'].get(url_param=param, no_check=True)

    assert (response.status_code == result), 'Fail: request should not be sent: status %s, message %s' % (
            response.status_code, response.content)

