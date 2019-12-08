import json
import pytest

from tests.db_support import poi_groups_info


@pytest.mark.parametrize('name', poi_groups_info('name'))
def test_search_device_groups_with_name(name, iot_api):

    body = {'name': name}
    groups = iot_api['poi'].post(json.dumps(body), url_param='groups/search')

    assert (groups['totalElements'] == 1), \
        'Fail: id: total elements api %s != %s db' % (groups['totalElements'], 1)
    group = groups['content'][0]
    assert group['name'] == name, 'Fail: name: api %s != %s db' % (group['name'], name)


