import json

from tests.db_support import devices_ids


def test_get_devices_info(iot_api):
    devices = iot_api['device'].get()

    # get profile ids and source ids
    ids_sids = devices_ids()

    assert (len(ids_sids) == devices['totalElements']), \
        'Fail: id: total elements api %s != %s db' % (devices['totalElements'], len(ids_sids))

    for dvc in devices['content']:
        guid = dvc['id']
        assert guid in ids_sids, 'Fail: device id: api %s != %s db' % (guid, ids_sids)
        assert dvc['sourceId'] == ids_sids[guid]['source_id'], \
            'Fail: device id: %s, source id: api %s != %s db' % (guid, dvc['source_id'], ids_sids[guid]['source_id'])


def test_get_devices_no_auth(iot_api):

    iot_api['device'].headers = {}

    response = iot_api['device'].get(no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
