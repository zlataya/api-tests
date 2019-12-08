from tests.db_support import geofence_groups_dto


def test_get_geofence_groups_info(iot_api):
    groups = iot_api['geofence'].get(url_param='groups')

    db_data = geofence_groups_dto(parametrize=False)

    assert (groups['totalElements'] == len(db_data)), \
        'Fail: id: total elements api %s != %s db' % (groups['totalElements'], len(db_data))

    for grp in groups['content']:
        uuid = grp['id']
        assert uuid in db_data, 'Fail: group id: api %s != %s db' % (uuid, db_data)
        assert grp['name'] == db_data[uuid]['name'], 'Fail: group name: api %s != %s db' % (uuid, db_data)
