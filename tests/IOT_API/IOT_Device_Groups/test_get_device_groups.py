import json

from tests.db_support import groups_dto


def test_get_device_groups_info(iot_api):
    groups = iot_api['device'].get(url_param='groups?size=15')

    db_data = groups_dto(parametrize=False)

    assert (groups['totalElements'] == len(db_data)), \
        'Fail: id: total elements api %s != %s db' % (groups['totalElements'], len(db_data))

    assert (groups['size'] == 15), 'Fail: id: returned elements api %s is 30' % groups['size']

    for grp in groups['content']:
        uuid = grp['id']
        assert uuid in db_data, 'Fail: group id: api %s != %s db' % (uuid, db_data)
        assert grp['name'] == db_data[uuid]['name'], 'Fail: group name: api %s != %s db' % (uuid, db_data)
        assert grp['domainId'] == db_data[uuid]['domain_id'], \
            'Fail: device id: %s, source id: api %s != %s db' % (uuid, grp['domain_id'], db_data[uuid]['domain_id'])


def test_get_device_groups_no_auth(iot_api):

    iot_api['device'].headers = {}

    response = iot_api['device'].get(url_param='groups', no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
