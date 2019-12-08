from tests.db_support import poi_groups_dto


def test_get_poi_groups_info(iot_api):
    groups = iot_api['poi'].get(url_param='groups')

    db_data = poi_groups_dto(parametrize=False)

    assert (len(groups) == len(db_data)), \
        'Fail: id: total elements api %s != %s db' % (len(groups), len(db_data))

    for grp in groups:
        uuid = grp['id']
        assert uuid in db_data, 'Fail: group id: api %s != %s db' % (uuid, db_data)
        assert grp['name'] == db_data[uuid]['name'], 'Fail: group name: api %s != %s db' % (uuid, db_data)
