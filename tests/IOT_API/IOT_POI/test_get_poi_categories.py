import json

from tests.db_support import poi_category_info


def test_get_poi_categories_info(iot_api):
    categories = iot_api['poi'].get(url_param='categories?sort=name&size=100')

    db_data = poi_category_info(param='row_to_json(cat)', limit=100)

    assert (categories['totalElements'] == len(db_data)), \
        'Fail: id: total elements api %s != %s db' % (categories['totalElements'], len(db_data))

    for api_cat, db_cat in zip(categories['content'], db_data):
        assert api_cat['id'] == db_cat['id'], 'Fail: category id: api %s != %s db' % (api_cat['id'], db_cat['id'])
        assert api_cat['name'] == db_cat['name'], 'Fail: group name: api %s != %s db' % (api_cat['name'], db_cat['name'])


def test_get_poi_categories_no_auth(iot_api):

    iot_api['poi'].headers = {}

    response = iot_api['poi'].get(url_param='categories?sort=name&size=100', no_check=True)

    assert (response.status_code == 403), 'Fail: request should not be sent: status %s, message %s' % \
                                          (response.status_code, response.content)

    message = json.loads(response.content)['error']
    assert message == 'Full authentication is required to access this resource', \
        'Fail: response message is not correct: status %s, message %s' % (response.status_code, message)
