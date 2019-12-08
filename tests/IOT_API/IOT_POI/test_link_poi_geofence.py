import pytest

from tests.db_support import poi_geo_ids


@pytest.mark.parametrize('poi_id, geo_id', poi_geo_ids())
def test_link_poi_geofence(poi_id, geo_id, iot_api):

    # test adding poi to geofence method
    poi_info = iot_api['poi'].put(url_param='%s/geofences/%s' % (poi_id, geo_id))

    assert geo_id in [geo['id'] for geo in poi_info['geofences']], 'Fail: geofence is not linked: api %s' % geo_id

    # test deleting poi from group method
    iot_api['poi'].delete(url_param='%s/geofences/%s' % (poi_id, geo_id))

    poi_info = iot_api['poi'].get(url_param=poi_id)

    assert geo_id not in [geo['id'] for geo in poi_info['geofences']], 'Fail: geofence is not unlinked: api %s' % geo_id
