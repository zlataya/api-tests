import json
import pytest

from framework.request import Request
from tests.conftest import env_config


def pytest_report_header():
    return "%s: IOT API testing..." % env_config.option('Environment', 'platform').upper()


@pytest.fixture()
def iot_api():

    api_connection = env_config.section('IOT API AUTH')

    api_spec_connection = env_config.section('IOT API DEV') if env_config.option('Environment', 'platform') == 'dev' \
        else env_config.section('IOT API FAT')

    def get_token():
        auth_api = Request(api_connection['auth_url'], headers={'content-type': 'application/x-www-form-urlencoded'})

        body = {'client_id': api_connection['client_id'],
                'grant_type': api_connection['grant_type'],
                'username': api_connection['username'],
                'password': api_connection['password']}

        return auth_api.post(body)['access_token']

    headers = {'Authorization': 'Bearer %s' % get_token(),
               'content-type': 'application/json'}

    apis = dict()

    apis['device'] = Request(api_spec_connection['device_api_url'], headers=headers)
    apis['geofence'] = Request(api_spec_connection['geofence_api_url'], headers=headers)
    apis['poi'] = Request(api_spec_connection['poi_api_url'], headers=headers)
    apis['telemetry'] = Request(api_spec_connection['telemetry_api_url'], headers=headers)
    apis['threshold'] = Request(api_spec_connection['threshold_api_url'], headers=headers)
    apis['geo_event'] = Request(api_spec_connection['geo_event_api_url'], headers=headers)
    apis['rule'] = Request(api_spec_connection['rule_api_url'], headers=headers)
    apis['device_cda'] = Request(api_spec_connection['device_base'], headers=headers)

    return apis


@pytest.fixture()
def json_template():

    def load_json(file_name):
        with open('JSON/%s_template.json' % file_name, 'r') as jfile:
            return json.load(jfile)
    return load_json
