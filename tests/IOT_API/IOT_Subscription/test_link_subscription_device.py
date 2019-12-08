import json
import pytest

from tests.db_support import device_rules_link, rule_devices_link


def test_link_subscription_device_all(iot_api):

    device_rule = device_rules_link(limit=2)
    uuid1, uuid2 = device_rule

    body = [{"deviceId": uuid1, "ruleIds": device_rule[uuid1]},
            {"deviceId": uuid2, "ruleIds": device_rule[uuid2]}]

    # test assign rules to devices
    iot_api['rule'].put(json.dumps(body), url_param='link/all')

    links = iot_api['rule'].post(json.dumps([uuid1, uuid2]), url_param='links')

    for link in links:
        uuid = link['deviceId']
        linked_rules = set(device_rule[uuid]).intersection(set(link['ruleIds']))
        assert linked_rules == set(device_rule[uuid]), 'Fail: uuid: %s, rules not linked: %s' % \
                                                       (uuid, set(device_rule[uuid]).difference(linked_rules))

    # test remove rules from devices
    iot_api['rule'].post(json.dumps(body), url_param='unlink/all')

    links = iot_api['rule'].post(json.dumps([uuid1, uuid2]), url_param='links')
    for link in links:
        uuid = link['deviceId']
        linked_rules = set(device_rule[uuid]).intersection(set(link['ruleIds']))
        assert len(linked_rules) == 0, 'Fail: uuid: %s, rules not unlinked: %s' % (uuid, linked_rules)


@pytest.mark.parametrize('uuid, rule_ids', device_rules_link(parametrize=True, limit=2))
def test_link_subscription_device(uuid, rule_ids, iot_api):

    body = {"deviceId": uuid, "ruleIds": rule_ids}

    # test assign rules to devices
    iot_api['rule'].put(json.dumps(body), url_param='link')

    link = iot_api['rule'].post(json.dumps([uuid]), url_param='links')

    linked_rules = set(rule_ids).intersection(set(link[0]['ruleIds']))
    assert linked_rules == set(rule_ids), 'Fail: uuid: %s, rules not linked: %s' % \
                                          (uuid, set(rule_ids).difference(linked_rules))

    # test remove rules from devices
    iot_api['rule'].post(json.dumps(body), url_param='unlink')

    link = iot_api['rule'].post(json.dumps([uuid]), url_param='links')

    linked_rules = set(rule_ids).intersection(set(link[0]['ruleIds']))
    assert len(linked_rules) == 0, 'Fail: uuid: %s, rules not unlinked: %s' % (uuid, linked_rules)


def test_unlink_device_subscription(iot_api):

    device_rule = device_rules_link(limit=5)
    uuids = list(device_rule.keys())

    body = [{"deviceId": k, "ruleIds": v} for k, v in device_rule.items()]

    # test assign rules to devices
    iot_api['rule'].put(json.dumps(body), url_param='link/all')

    links = iot_api['rule'].post(json.dumps(uuids), url_param='links')

    for link in links:
        uuid = link['deviceId']
        assert len(link['ruleIds']) != 0, 'Fail: uuid: %s, rules list is empty: %s' % (uuid, link['ruleIds'])

    # test remove all rules from devices
    iot_api['rule'].post(json.dumps(uuids), url_param='unlink/device')

    # get links for devices and check they are empty
    links = iot_api['rule'].post(json.dumps(uuids), url_param='links')
    for link in links:
        uuid = link['deviceId']
        assert len(link['ruleIds']) == 0, 'Fail: uuid: %s, rules list is not empty: %s' % (uuid, link['ruleIds'])


@pytest.mark.parametrize('rule, uuids', rule_devices_link(parametrize=True, limit=2))
def test_unlink_subscription_device(rule, uuids, iot_api):

    body = [{"deviceId": uuid, "ruleIds": [rule]} for uuid in uuids]

    # assign all devices to 'rule' rule
    iot_api['rule'].put(json.dumps(body), url_param='link/all')

    links = iot_api['rule'].post(json.dumps(uuids), url_param='links')

    for link in links:
        uuid = link['deviceId']
        assert rule in link['ruleIds'], 'Fail: uuid: %s, rule is not linked to device: %s' % (uuid, rule)

    # test remove rule from all devices
    iot_api['rule'].post(json.dumps([rule]), url_param='unlink/rule')

    # get links for devices and check they are empty
    links = iot_api['rule'].post(json.dumps(uuids), url_param='links')
    for link in links:
        uuid = link['deviceId']
        assert rule not in link['ruleIds'], 'Fail: uuid: %s, rule is linked to device: %s' % (uuid, rule)
