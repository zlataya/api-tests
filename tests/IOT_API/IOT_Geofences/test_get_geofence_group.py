import pytest

from tests.db_support import geofence_groups_dto


@pytest.mark.parametrize('uuid, db_data', geofence_groups_dto())
def test_get_geofence_group_info(uuid, db_data, iot_api):

    api_data = iot_api['geofence'].get(url_param='groups/%s' % uuid)

    assert (db_data['id'] == api_data['id']), \
        'Fail: uuid: %s, id: api %s != %s db' % (uuid, api_data['id'], db_data['id'])
    assert (db_data['name'] == api_data['name']), \
        'Fail: uuid: %s, name: api %s != %s db' % (uuid, api_data['name'], db_data['name'])
