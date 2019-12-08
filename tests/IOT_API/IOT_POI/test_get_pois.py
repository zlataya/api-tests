import json

from tests.db_support import poi_category_ids


def test_get_pois_info(iot_api):
    pois = iot_api['poi'].get()

    # get poi and category ids
    poi_ids = poi_category_ids()

    assert (len(poi_ids) == pois['totalElements']), \
        'Fail: id: total elements api %s != %s db' % (pois['totalElements'], len(poi_ids))

    for poi in pois['content']:
        guid = poi['id']
        assert guid in poi_ids, 'Fail: poi id: api %s != %s db' % (guid, poi_ids)
        assert poi['category']['id'] == poi_ids[guid]['category_id'], \
            'Fail: poi id: %s, category id: api %s != %s db' % (guid, poi['category']['id'], poi_ids[guid]['category_id'])


def test_get_pois_no_auth(iot_api):

    iot_api['poi'].headers = {}

    response = iot_api['poi'].get(no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
