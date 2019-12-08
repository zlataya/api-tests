import json
import pytest

from tests.db_support import subscriptions_info


@pytest.mark.parametrize('name, cnt', subscriptions_info(param='name', limit='10'))
def test_search_subscription_with_name(name, cnt, iot_api):

    body = {'name': name}
    rules = iot_api['rule'].post(json.dumps(body), url_param='search')

    assert len(rules) == cnt, 'Fail: number of rules: api %s != %s db' % (len(rules), cnt)

    for rule in rules:
        assert name.lower() in rule['name'].lower(), 'Fail: name: api %s != %s db' % (rule['name'], name)


