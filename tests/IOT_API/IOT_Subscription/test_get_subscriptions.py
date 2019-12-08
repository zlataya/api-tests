import json

from tests.db_support import subscriptions_ids_name


def test_get_subscriptions(iot_api):
    api_rules = iot_api['rule'].get()

    # get profile ids and source ids
    db_rules = subscriptions_ids_name(parametrize=False)

    assert (len(db_rules) == api_rules['totalElements']), \
        'Fail: id: total elements api %s != %s db' % (api_rules['totalElements'], len(db_rules))

    assert (api_rules['size'] == 10), \
        'Fail: id: returned elements api %s != %s db' % (api_rules['size'], 10)

    for rule in api_rules['content']:
        guid = rule['id']
        assert guid in db_rules, 'Fail: rule id: api %s != %s db' % (guid, db_rules)
        assert rule['name'] == db_rules[guid]['name'], \
            'Fail: rule id: %s, rule name: api %s != %s db' % (guid, rule['name'], db_rules[guid]['name'])


def test_get_subscriptions_no_auth(iot_api):

    iot_api['rule'].headers = {}

    response = iot_api['rule'].get(no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
