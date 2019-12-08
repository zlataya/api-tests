from datetime import datetime
import pytest
from py.xml import html

from framework.configread import ReadConfig
from framework.dbdynamo import DbDynamo

env_config = ReadConfig()


@pytest.mark.optionalhook
def html_results_table_row(report, cells):
    cells.insert(2, html.td(report.description))
    cells.insert(1, html.td(datetime.utcnow(), class_='col-time'))
    cells.pop()


@pytest.mark.hookwrapper
def runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)


@pytest.fixture
def expect(request):
    def do_expect(expr, msg=''):
        if not expr:
            _log_failure(request.node, msg)

    return do_expect


def _log_failure(node, msg=''):
    # format entry
    msg = '%s' % msg if msg else ''
    # add entry
    if not hasattr(node, '_failed_expect'):
        node._failed_expect = []
    node._failed_expect.append(msg)


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    report = __multicall__.execute()
    if (call.when == "call") and hasattr(item, '_failed_expect'):
        report.outcome = "failed"
        summary = 'Failed Test Steps:%s' % len(item._failed_expect)
        item._failed_expect.append(summary)
        report.longrepr = '\n'.join(item._failed_expect)
    return report

    
@pytest.fixture()
def get_iot_data():

    dnm_db = DbDynamo()

    def get_data(uuid, dynamo_from, dynamo_to, table='telemetry'):
        """
        :param uuid: device uuid from PostgreDB
        :param dynamo_from: start date in timestamp format
        :param dynamo_to: end date in timestamp format
        :param table: only for Mecomo, can be 'position' or 'telemetry'
        :return: dictionary with record_date as a key
        """
        entries = dnm_db.db_query(uuid, dynamo_from, dynamo_to, table=table)
        
        if table == 'position':
            return entries
        
        # for mecomo data positionId is a key
        if entries and entries[0]['src'] == 'mecomo':
            telemetry_dict = {str(row['positionId']): row for row in entries}
        else:
            telemetry_dict = {datetime.fromtimestamp(row['record_date']/1000): row for row in entries}
        return telemetry_dict

    return get_data
    

