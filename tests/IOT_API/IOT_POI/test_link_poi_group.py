import pytest

from tests.db_support import poi_groups_dto


@pytest.mark.parametrize('group_id, poi_id', poi_groups_dto(ids=True))
def test_link_poi_group(group_id, poi_id, iot_api):

    # test adding poi to group method
    poi_info = iot_api['poi'].put(url_param='%s/groups/%s' % (poi_id, group_id))

    assert group_id in poi_info['groupIds'], \
        'Fail: group id: %s is not linked to poi id %s' % (group_id, poi_id)

    # test deleting poi from group method
    poi_info = iot_api['poi'].delete(url_param='%s/groups/%s' % (poi_id, group_id))

    assert group_id not in poi_info['groupIds'], \
        'Fail: group id: %s is linked to poi id %s' % (group_id, poi_id)
