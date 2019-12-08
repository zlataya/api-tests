import json
import pytest

from tests.db_support import groups_info


@pytest.mark.parametrize('name', groups_info('name'))
def test_search_device_groups_with_name(name, iot_api):

    body = {'name': name}
    groups = iot_api['device'].post(json.dumps(body), url_param='groups/search')

    assert (groups['totalElements'] == 1), \
        'Fail: id: total elements api %s != %s db' % (groups['totalElements'], 1)
    group = groups['content'][0]
    assert group['name'] == name, 'Fail: name: api %s != %s db' % (group['name'], name)


@pytest.mark.parametrize('uuid', groups_info('id', limit=10))
def test_search_device_groups_with_id(uuid, iot_api):

    body = {'id': uuid}
    groups = iot_api['device'].post(json.dumps(body), url_param='groups/search')

    assert (groups['totalElements'] == 1), \
        'Fail: id: total elements api %s != %s db' % (groups['totalElements'], 1)
    group = groups['content'][0]
    assert group['id'] == uuid, 'Fail: group id: api %s != %s db' % (group['id'], uuid)

