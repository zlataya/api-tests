import boto3
from boto3.dynamodb.conditions import Key

from framework.configread import ReadConfig


class DbDynamo(object):

    # this class is for working with Dynamo DB
    def __init__(self, config_name=None):

        self.config = config_name
        db_connection = self.read_db_configuration()

        self.table_telemetry = db_connection['table.telemetry']
        self.table_position = db_connection['table.position']

        self.connection = self.db_connect()
        self.iot_telemetry = self.connection.Table(self.table_telemetry)
        self.iot_metadata = self.connection.Table(self.table_position)

    def read_db_configuration(self):
        env_config = ReadConfig(self.config)
        db_connection = env_config.section('DynamoDB')

        return db_connection

    def db_connect(self):
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

        return dynamodb

    def db_query(self, uuid, dynamo_from, dynamo_to, table='telemetry'):
        """
        :param uuid: device id in DynamoDb
        :param dynamo_from: timestamp for 'from' date
        :param dynamo_to: timestamp for 'to' date
        :param table: table name (actual for Mecomo testing only)
        :return:
        """
        _from, _to = round(dynamo_from), round(dynamo_to)
        if table == 'position':
            entry = self.iot_metadata.query(KeyConditionExpression=Key('event_type').eq('mecomo_last_postion'))
            return entry['Items'][0]
        else:
            entry = self.iot_telemetry.query(
                KeyConditionExpression=Key('device_id').eq(uuid) & Key('record_date').between(_from, _to))

        return entry['Items']
