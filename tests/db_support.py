import json

from collections import defaultdict
from framework.dbpostgres import DbPostgres


def psg_db(sql):
    connector = DbPostgres()

    db_info = connector.safe_execute(sql)

    del connector

    return db_info


def devices_mc_dto():
    devices_id_info = psg_db(sql=
                             """SELECT
                                 dvc.source_id device_id,
                                 dvc_m.name device_name,
                                 dvc_m.reg_date,
                                 dvc.serial_number,
                                 dvc_m.gps_id,
                                 dvc_m.provider,
                                 dvc_m.provider_name,
                                 dvc_m.msisdn,
                                 dvc_m.sim_card,
                                 dvc_m.network_operator
                                 from iot_platform.iot_device_mecomo dvc_m
                               JOIN iot_platform.iot_device dvc on dvc.id = dvc_m.id
                               ORDER BY source_id"""
                             )

    db_devices = [(row['device_id'], {key: str(val) for key, val in row.items()}) for row in devices_id_info]

    return db_devices


def devices_object():
    devices_id_object = psg_db(sql="""SELECT
                                 dvc.source_id device_id,
                                 dvc_m.object_id,
                                 dvc_m.object_name
                               FROM iot_platform.iot_device_mecomo dvc_m
                               JOIN iot_platform.iot_device dvc on dvc.id = dvc_m.id
                               ORDER BY name""")

    db_objects = [(row['device_id'], {key: str(val) for key, val in row.items()}) for row in devices_id_object]

    return db_objects


def devices_dto():
    device_info = psg_db(sql=
                         """WITH all_data AS (
                                 SELECT
                                   dvc_prf.id                         as id,
                                   dvc.id                             as device_id,
                                   dvc.imei,
                                   dvc.source_id                      as sourceId,
                                   ARRAY[CAST(dvc.vendor_id AS VARCHAR(64)), initcap(dvc.type)] as vendor,
                                   dvc.serial_number                  as serialNumber,
                                   dvc.created                        as created,
                                   dvc.updated                        as updated,
                                   dvc.telemetry_updated              as telemetryUpdated,
                                   dvc.source_telemetry_updated       as sourceTelemetryUpdated,
                                   row_number()
                                   OVER (
                                     PARTITION BY dvc.type
                                     ORDER BY dvc.updated DESC)           AS rank
                                 FROM iot_platform.iot_device dvc
                                   JOIN iot_platform.iot_device_profile dvc_prf ON dvc_prf.device_id = dvc.id AND dvc_prf.active_to > now()
                                   LEFT JOIN iot_platform.iot_device_profile_to_group_link prf_grp ON prf_grp.device_profile_id = dvc_prf.id
                                   LEFT JOIN iot_platform.iot_device_group grp ON grp.id = prf_grp.device_group_id
                                 WHERE dvc.source_telemetry_updated IS NOT NULL AND dvc.source_telemetry_updated > dvc_prf.active_from)
                             SELECT *
                             FROM all_data
                             WHERE rank < 7""")

    db_device = [(row['id'], defaultdict(lambda: None, {key: val for key, val in row.items() if val})) for row in device_info]

    return db_device


def devices_info(param, limit=5):
    device_info = psg_db(sql="""SELECT DISTINCT %s as val 
                                FROM iot_platform.iot_device 
                                WHERE %s IS NOT NULL AND 
                                coalesce(telemetry_updated, updated) > date_trunc('day',current_date) - interval '1 year'
                                LIMIT %s;"""
                         % (param, param, limit))

    db_device = [row['val'] for row in device_info]

    return db_device


def devices_vendor_info(vendor):
    device_info = psg_db(sql="""SELECT
                                  dvc_prf.id as profile_id,
                                  dvc_ven.*
                                FROM iot_platform.iot_device_%s dvc_ven
                                JOIN iot_platform.iot_device_profile dvc_prf ON dvc_prf.device_id = dvc_ven.id AND dvc_prf.active_to > now()
                                JOIN iot_platform.iot_device dvc ON dvc.id = dvc_ven.id
                                ORDER BY dvc.created DESC LIMIT 5;"""
                             % vendor)

    db_device = [(row['profile_id'], defaultdict(lambda: None, {key: val for key, val in row.items()})) for row in device_info]

    return db_device


def devices_ids():
    device_info = psg_db(sql=
                         """SELECT
                               dvc_prf.id  profile_id,
                               dvc.id device_id,
                               dvc.source_id
                            FROM iot_platform.iot_device dvc
                               JOIN iot_platform.iot_device_profile dvc_prf ON dvc_prf.device_id = dvc.id
                            WHERE coalesce(dvc.telemetry_updated, dvc.updated) > date_trunc('day',current_date) - interval '1 year';""")

    db_device = {row['profile_id']: row for row in device_info}

    return db_device


def iot_telemetry(vendor):
    telemetry_info = psg_db(sql=
                            """SELECT
                                dvc.id uuid,
                                dvc.source_id device_id,
                                st_asgeojson(dvc.coordinates, 5) coordinates,
                                dvc.source_telemetry_updated
                              FROM iot_platform.iot_device dvc
                              WHERE type='%s' and dvc.coordinates is not null
                              ORDER BY dvc.source_id;""" % vendor)
    db_telemetry = [(row['device_id'],
                     {key: json.loads(val)['coordinates'] if key == 'coordinates' else val for key, val in row.items()})
                    for row in telemetry_info]
    return db_telemetry


def vendors_info():
    vendor_info = psg_db(sql="""SELECT
                                  vendor.id,
                                  vendor.name,
                                  count(dvc.id)
                                FROM iot_platform.iot_vendor vendor
                                  LEFT JOIN iot_platform.iot_device dvc
                                    ON dvc.vendor_id = vendor.id
                                       AND coalesce(dvc.telemetry_updated, dvc.updated) > date_trunc('day',current_date) - interval '1 year'
                                WHERE vendor.name IN ('Kirsen', 'Zillion', 'Mecomo', 'OnAsset', 'Drive App')
                                GROUP BY vendor.id;""")

    db_vendors = [(row['id'], row['name'], row['count']) for row in vendor_info]

    return db_vendors


def groups_stat():
    group_info = psg_db(sql="""SELECT
                                 groups.id,
                                 COUNT(link.device_profile_id)
                               FROM iot_platform.iot_device_group groups
                                 JOIN iot_platform.iot_device_profile_to_group_link link ON groups.id = link.device_group_id
                                 JOIN iot_platform.iot_device_profile prf ON prf.id = link.device_profile_id AND prf.active_to > now()
                                 JOIN iot_platform.iot_device dvc ON prf.device_id = dvc.id
                               WHERE coalesce(dvc.telemetry_updated, dvc.updated) > date_trunc('day',current_date) - interval '1 year'
                               GROUP BY groups.id""")

    db_groups = [(row['id'], row['count']) for row in group_info]

    return db_groups


def groups_dto(parametrize=True, limit='ALL'):
    group_info = psg_db(sql="""SELECT * FROM iot_platform.iot_device_group dvc_grp LIMIT %s;""" % limit)

    if parametrize:
        db_group = [(row['id'], row) for row in group_info]
    else:
        db_group = {row['id']: row for row in group_info}

    return db_group


def groups_info(param, limit=5):
    group_info = psg_db(sql="""SELECT 
                                  DISTINCT MAX(CAST(%s as VARCHAR(36))) as val  
                                FROM iot_platform.iot_device_group
                                GROUP BY name
                                HAVING count(id) < 2 
                                LIMIT %s;""" % (param, limit))

    db_group = [row['val'] for row in group_info]

    return db_group


def devices_groups_ids():
    device_group_id = psg_db(sql=
                             """SELECT DISTINCT
                                  dvc_prf.id device_id,
                                  dvc_grp.id group_id
                                FROM iot_platform.iot_device_profile dvc_prf, iot_platform.iot_device_group dvc_grp
                                WHERE dvc_prf.active_to > now() AND (dvc_prf.id, dvc_grp.id) NOT IN (
                                  SELECT
                                    device_profile_id,
                                    device_group_id
                                  FROM iot_platform.iot_device_profile_to_group_link link
                                ) LIMIT 5;""")

    db_device_group = [(row['device_id'], row['group_id']) for row in device_group_id]

    return db_device_group


def locations_info():
    location_info = psg_db(sql="""SELECT *
                                    FROM (

                                           SELECT
                                             st_asgeojson(dvc.coordinates)    as coordinates,
                                             serial_number,
                                             source_id,
                                             COUNT(source_id)
                                             OVER (
                                               PARTITION BY dvc.coordinates ) as duplicates
                                           FROM iot_platform.iot_device dvc
                                           WHERE dvc.coordinates IS NOT NULL AND 
                                           coalesce(dvc.telemetry_updated, dvc.updated) > now() - interval '1 year'
                                           ORDER BY source_telemetry_updated DESC) with_duplicated
                                    WHERE duplicates = 1
                                    LIMIT 5;""")

    db_locations = [(row['coordinates'], row['serial_number'], row['source_id']) for row in location_info]

    return db_locations


def devices_count(param, value, active_flag=1):

    if type(value) == str:
        device_info = psg_db(sql="""SELECT COUNT(*)
                                    FROM iot_platform.iot_device dvc
                                      JOIN iot_platform.iot_device_profile dvc_prf ON dvc.id = dvc_prf.device_id 
                                      AND (dvc_prf.active_to > now()) is not %s
                                    WHERE dvc.%s iLIKE '%%%s%%' AND coalesce(dvc.telemetry_updated, dvc.updated) > 
                                    date_trunc('day', current_date) - interval '1 year';"""
                                 % (['NULL', False, True][active_flag], param, value))
    elif type(value) == list:
        device_info = psg_db(sql="""SELECT COUNT(DISTINCT dvc_prf.id) FROM iot_platform.iot_device dvc 
                                        JOIN iot_platform.iot_device_profile dvc_prf ON dvc.id = dvc_prf.device_id AND
                                        (dvc_prf.active_to > now()) is not %s
                                        LEFT JOIN iot_platform.iot_device_profile_to_group_link link 
                                        ON link.device_profile_id = dvc_prf.id
                                        WHERE %s IN %s 
                                        AND coalesce(dvc.telemetry_updated, dvc.updated) > 
                                        date_trunc('day', current_date) - interval '1 year';"""
                                 % (['NULL', False, True][active_flag], param, tuple(value)))
    else:
        device_info = psg_db(sql="""SELECT COUNT(*)
                                    FROM (
                                           SELECT
                                             st_asgeojson(coordinates),
                                             st_within(coalesce(dvc_prf.historical_coordinates, dvc.coordinates), '%s') as flag
                                           FROM iot_platform.iot_device dvc
                                           JOIN iot_platform.iot_device_profile dvc_prf ON dvc.id = dvc_prf.device_id 
                                                AND (dvc_prf.active_to > now()) is not %s
                                           WHERE coordinates IS not null 
                                           AND coalesce(dvc.telemetry_updated, dvc.updated) > 
                                           date_trunc('day', current_date) - interval '1 year'
                                           ) within_data
                                    WHERE within_data.flag is TRUE;""" % (value, ['NULL', False, True][active_flag]))

    return device_info[0]['count']


def poi_dto(parametrize=False, limit=5):
    pois_dto = psg_db(sql=
                      """WITH poi_dto AS (
                            SELECT
                              poi.id,
                              poi.name                          as name,
                              poi_type.id                       as category_id,
                              poi_type.name                     as category,
                              poi.description,
                              st_asgeojson(poi.coordinates)     as coordinates,
                              (SELECT row_to_json(poi_adr)
                               FROM iot_platform.iot_poi_address poi_adr
                               WHERE poi.id = poi_adr.id)       as address,
                              to_json(array_remove(array_agg(geo.id) OVER (PARTITION BY poi.id, poi_type.id), NULL)) as geofences
                            FROM iot_platform.iot_poi poi
                              JOIN iot_platform.iot_poi_category poi_type ON poi_type.id = poi.category_id
                              LEFT JOIN iot_platform.iot_poi_to_geofence_link link ON link.poi_id = poi.id
                              LEFT JOIN iot_platform.iot_geofence geo ON geo.id = link.geofence_id
                            WHERE poi.deleted IS FALSE AND poi_type.deleted IS FALSE)
                        (SELECT poi_dto.*
                         FROM poi_dto
                         WHERE address is not null
                         LIMIT %s)
                        UNION ALL
                        (SELECT poi_dto.*
                         FROM poi_dto
                         WHERE geofences -> 0 is not null
                         LIMIT %s)
                        UNION ALL
                        (SELECT poi_dto.*
                         FROM poi_dto
                         WHERE geofences -> 0 is null and address ->> 'city' is null
                         LIMIT %s);"""
                      % (limit, limit, limit))

    if parametrize:
        db_poi = [(row['id'], defaultdict(lambda: None,
                                          {key: json.loads(val) if key == 'coordinates' and val else val for
                                           key, val in row.items()}))
                  for row in pois_dto]
    else:
        db_poi = {
            row['id']: {key: json.loads(val) if key == 'coordinates' and val else val for key, val in
                        row.items()} for row in pois_dto}
    return db_poi


def poi_info(param, limit=5):
    pois_info = psg_db(sql="""SELECT DISTINCT %s as val
                              FROM iot_platform.iot_poi poi
                              WHERE poi.deleted IS FALSE AND %s IS NOT NULL 
                              LIMIT %s;""" % (param, param, limit))

    db_poi = [row['val'] for row in pois_info]

    return db_poi


def poi_category_ids():
    pois_info = psg_db(sql="""SELECT poi.id, 
                                     poi_type.id as category_id, 
                                     poi_type.name as category
                                FROM iot_platform.iot_poi poi
                                JOIN iot_platform.iot_poi_category poi_type ON poi_type.id = poi.category_id
                                WHERE poi.deleted IS FALSE;""")

    db_poi_cat = {row['id']: row for row in pois_info}

    return db_poi_cat


def poi_category_info(param, limit=5):
    category_info = psg_db(sql="""SELECT %s as val 
                                FROM iot_platform.iot_poi_category cat
                                WHERE cat.deleted IS FALSE
                                ORDER BY cat.name
                                LIMIT %s;""" % (param, limit))

    db_category = [row['val'] for row in category_info]

    return db_category


def poi_address_info(param, only_one=True):
    address_info = psg_db(sql="""SELECT
                                    DISTINCT %s as addr_field
                                  FROM iot_platform.iot_poi_address address
                                    JOIN iot_platform.iot_poi poi ON address.id = poi.id
                                  WHERE %s is NOT NULL AND poi.deleted IS FALSE;""" % (param, param))
    if only_one:
        db_address = address_info[0]['addr_field']
    else:
        db_address = [row['addr_field'] for row in address_info]

    return db_address


def geo_ids_with_poi(limit=5):
    geo_ids = psg_db(sql="""SELECT link.geofence_id
                            FROM iot_platform.iot_poi poi
                              JOIN iot_platform.iot_poi_to_geofence_link link ON poi.id = link.poi_id
                            WHERE poi.deleted IS FALSE
                            LIMIT %s;""" % limit)

    db_geo = [row['geofence_id'] for row in geo_ids]

    return db_geo


def poi_groups_info(param, limit=5):
    group_info = psg_db(sql="""SELECT 
                                  DISTINCT MAX(CAST(%s as VARCHAR(36))) as val  
                                FROM iot_platform.iot_poi_group
                                GROUP BY name
                                HAVING count(id) < 2 
                                LIMIT %s;""" % (param, limit))

    db_group = [row['val'] for row in group_info]

    return db_group


def poi_groups_dto(parametrize=True, limit='ALL', ids=False):
    group_info = psg_db(sql="""WITH poi_group_sample AS (
                                    SELECT
                                      row_number() OVER () as rownum,
                                      groups.id,
                                      groups.name
                                    FROM iot_platform.iot_poi_group groups
                                LIMIT %s)
                                SELECT
                                  poi_group_sample.*,
                                  (SELECT id
                                   FROM iot_platform.iot_poi
                                    WHERE deleted is FALSE
                                   OFFSET poi_group_sample.rownum
                                   LIMIT 1) poi_id
                                FROM poi_group_sample;""" % limit)

    if ids:
        db_group = [(row['id'], row['poi_id']) for row in group_info]
    elif parametrize:
        db_group = [(row['id'], row) for row in group_info]
    else:
        db_group = {row['id']: row for row in group_info}

    return db_group


def poi_geo_ids():
    poi_geo_id = psg_db(sql=
                        """SELECT DISTINCT
                             poi.id poi_id,
                             geo.id geo_id
                           FROM iot_platform.iot_poi poi, iot_platform.iot_geofence geo
                           WHERE poi.deleted is FALSE AND geo.deleted is FALSE AND geo.geofence_owner_id is NULL AND
                                  (poi.id, geo.id) NOT IN (
                                    SELECT
                                      poi_id,
                                      geofence_id
                                    FROM iot_platform.iot_poi_to_geofence_link link
                                    --do not touch LiNes data
                                  ) AND geo.domain_id != '492e754e-c1cf-4b5e-8530-a31e61bbd202'
                           LIMIT 5;""")

    db_poi_geo = [(row['poi_id'], row['geo_id']) for row in poi_geo_id]

    return db_poi_geo


def geo_id_name_all():
    geo_info = psg_db(sql="""SELECT
                              geo.id,
                              geo.name
                            FROM iot_platform.iot_geofence geo
                            WHERE geo.geofence_owner_id is NULL AND geo.deleted is FALSE;""")

    geo_info = {row['id']: row for row in geo_info}

    return geo_info


def geofence_dto(parametrize=True, limit='ALL'):
    geofce_info = psg_db(sql="""SELECT DISTINCT
                                  geo.id,
                                  geo.name,
                                  geo_type.name                   as type,
                                  geo.description,
                                  geo.geometry as geometrydata
                                FROM iot_platform.iot_geofence geo
                                  JOIN iot_platform.iot_geofence_type geo_type ON geo.geofence_type_id = geo_type.id
                                WHERE geo.geofence_owner_id is NULL AND geo.deleted is FALSE and geo.name is not NULL
                                ORDER BY description NULLS LAST
                                LIMIT %s;""" % limit)

    if parametrize:
        db_geo = [(row['id'], defaultdict(lambda: None, {key: val for key, val in row.items() if val}))
                  for row in geofce_info]
    else:
        db_geo = {row['id']: row for row in geofce_info}

    return db_geo


def geofence_groups_dto(parametrize=True, ids=False):
    group_info = psg_db(sql="""WITH geo_group_sample AS (
                                SELECT
                                  row_number()
                                  OVER () as rownum,
                                  groups.id,
                                  groups.name
                                FROM iot_platform.iot_geofence_group groups
                                LIMIT ALL)
                            SELECT
                              geo_group_sample.*,
                              (SELECT id
                               FROM iot_platform.iot_geofence geo
                               WHERE geo.deleted is FALSE AND geo.geofence_owner_id is NULL
                                     AND id NOT IN (SELECT geofence_id
                                                    FROM iot_platform.iot_geofence_to_group_link)
                               OFFSET geo_group_sample.rownum
                               LIMIT 1) geo_id
                            FROM geo_group_sample;""")

    if ids:
        db_group = [(row['id'], row['geo_id']) for row in group_info]
    elif parametrize:
        db_group = [(row['id'], row) for row in group_info]
    else:
        db_group = {row['id']: row for row in group_info}

    return db_group


def devices_with_events(event_type='geo', limit='ALL', days_to_collect=1):
    geo_check = ['ISNULL', 'NOTNULL'][event_type == 'geo']
    events_info = psg_db(sql="""SELECT
                                  events.id as event_id,
                                  events.record_date,
                                  events.criteria_type,
                                  events.telemetry_value as value,
                                  st_asgeojson(events.coordinates) as coordinates,
                                  dvc_prf.id as device_id,
                                  geo_crt.geofence_id
                                FROM iot_platform.iot_alerting_event events
                                  JOIN iot_platform.iot_device_profile dvc_prf ON dvc_prf.id = events.profile_id
                                  JOIN iot_platform.iot_objects_to_alerting_rules_link obj_alr
                                    ON obj_alr.object_id = dvc_prf.id and obj_alr.deleted is false
                                  LEFT JOIN iot_platform.iot_geofence_criteria geo_crt ON events.geofence_criteria_id = geo_crt.id
                                WHERE geofence_id %s 
                                AND events.record_date between date_trunc('day', current_date) - interval '%s day' 
                                AND date_trunc('day', current_date)
                                LIMIT %s;""" % (geo_check, days_to_collect, limit))

    db_geo = dict()

    for row in events_info:
        if 'coordinates' in row and row['coordinates']:
            row['coordinates'] = json.loads(row['coordinates'])
        if 'value' in row and row['value'] == '{}':
            row['value'] = None
        if row['device_id'] in db_geo:
            db_geo[row['device_id']].update({row['event_id']: row})
        else:
            db_geo[row['device_id']] = {row['event_id']: row}

    return [(k, v) for k, v in db_geo.items()]


def device_rules_link(parametrize=False, limit='ALL'):
    link_info = psg_db(sql="""SELECT
                                array_to_json(array_agg(rule.id))    as rule_ids,
                                dvc_prf.id as device_id
                              FROM iot_platform.iot_alerting_rule rule, iot_platform.iot_device_profile dvc_prf
                              WHERE dvc_prf.domain_id = rule.domain_id AND rule.deleted is FALSE 
                              GROUP BY dvc_prf.id
                              LIMIT %s;""" % limit)
    if parametrize:
        db_link = [(row['device_id'], row['rule_ids']) for row in link_info]
    else:
        db_link = {row['device_id']: row['rule_ids'] for row in link_info}

    return db_link


def rule_devices_link(parametrize=False, limit='ALL'):
    link_info = psg_db(sql="""SELECT
                                array_to_json(array_agg(dvc_prf.id)) as device_ids,
                                rule.id                              as rule_id
                              FROM iot_platform.iot_alerting_rule rule, iot_platform.iot_device_profile dvc_prf
                              WHERE dvc_prf.domain_id = rule.domain_id AND rule.deleted is FALSE
                              GROUP BY rule.id
                              LIMIT %s;""" % limit)
    if parametrize:
        db_link = [(row['rule_id'], row['device_ids']) for row in link_info]
    else:
        db_link = {row['rule_id']: row['device_ids'] for row in link_info}

    return db_link


def subscription_dto(parametrize=True, limit='ALL'):
    subs_info = psg_db(sql="""SELECT
                                  rule.id as rule_id,
                                  rule.name,
                                  rule.description,
                                  rule.created,
                                  rule.updated,
                                  to_json(ARRAY(SELECT row_to_json(thr_criteria)
                                                FROM iot_platform.iot_threshold_criteria thr_criteria
                                                WHERE thr_criteria.rule_id = rule.id AND thr_criteria.deleted is FALSE)) as thr_criteria,
                                  to_json(ARRAY(SELECT row_to_json(tm_criteria)
                                                FROM iot_platform.iot_telemetry_criteria tm_criteria
                                                WHERE tm_criteria.rule_id = rule.id AND tm_criteria.deleted is FALSE)) as tm_criteria,
                                  to_json(ARRAY(SELECT row_to_json(geo_criteria)
                                                FROM iot_platform.iot_geofence_criteria geo_criteria
                                                WHERE geo_criteria.rule_id = rule.id AND geo_criteria.deleted is FALSE)) as geo_criteria
                                FROM iot_platform.iot_alerting_rule rule
                                WHERE rule.deleted is FALSE
                                LIMIT %s;""" % limit)

    if parametrize:
        db_rule = [(row['rule_id'], row) for row in subs_info]
    else:
        db_rule = {row['rule_id']: row for row in subs_info}

    return db_rule


def subscriptions_ids_name(parametrize=True, limit='ALL'):
    subs_info = psg_db(sql="""SELECT
                                  rule.id as rule_id,
                                  rule.name
                                FROM iot_platform.iot_alerting_rule rule
                                WHERE rule.deleted is FALSE
                                LIMIT %s;""" % limit)

    if parametrize:
        db_rule = [(row['rule_id'], row['name']) for row in subs_info]
    else:
        db_rule = {row['rule_id']: row for row in subs_info}

    return db_rule


def subscriptions_info(param, limit='ALL'):
    rule_info = psg_db(sql="""SELECT
                              rule.%s                          as val,
                              (SELECT COUNT(*)
                               FROM iot_platform.iot_alerting_rule rule1
                               WHERE rule1.%s ilike CONCAT('%%', rule.%s, '%%')
                               AND rule1.deleted is FALSE) as cnt
                            FROM iot_platform.iot_alerting_rule rule
                            WHERE rule.deleted is FALSE
                            LIMIT %s;""" % (param, param, param, limit))

    db_rule = [(row['val'], row['cnt']) for row in rule_info]

    return db_rule
