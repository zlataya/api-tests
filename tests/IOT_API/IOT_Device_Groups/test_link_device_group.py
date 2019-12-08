import pytest

from tests.db_support import devices_groups_ids


@pytest.mark.parametrize('device_id, group_id', devices_groups_ids())
def test_link_device_group(device_id, group_id, iot_api):

    # test adding device to group method
    iot_api['device'].put(url_param='%s/groups/%s' % (device_id, group_id))

    device_info = iot_api['device'].get(url_param=device_id)

    assert group_id in device_info['groupIds'], \
        'Fail: group id: %s is not linked to device id %s' % (group_id, device_id)

    # test deleting device from group method
    iot_api['device'].delete(url_param='%s/groups/%s' % (device_id, group_id))

    device_info = iot_api['device'].get(url_param=device_id)

    assert group_id not in device_info['groupIds'], \
        'Fail: group id: %s is linked to device id %s' % (group_id, device_id)
