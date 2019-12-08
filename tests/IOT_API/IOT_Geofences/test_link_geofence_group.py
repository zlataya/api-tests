import pytest

from tests.db_support import geofence_groups_dto


@pytest.mark.parametrize('group_id, geo_id', geofence_groups_dto(ids=True))
def test_link_geofence_group(group_id, geo_id, iot_api):

    # test adding geofence to group method
    iot_api['geofence'].put(url_param='%s/groups/%s/' % (geo_id, group_id))
    geo_info = iot_api['geofence'].get(url_param=geo_id)

    assert group_id in geo_info['groupIds'], \
        'Fail: group id: %s is not linked to geofence id %s' % (group_id, geo_id)

    # test deleting geofence from group method
    iot_api['geofence'].delete(url_param='%s/groups/%s/' % (geo_id, group_id))
    geo_info = iot_api['geofence'].get(url_param=geo_id)

    assert group_id not in geo_info['groupIds'], \
        'Fail: group id: %s is linked to geofence id %s' % (group_id, geo_id)
