__author__ = 'huanpc'

CPU_THRESHOLD_UP = 0.1
CPU_THRESHOLD_DOWN = 0.001
MEM_THRESHOLD_UP = 15700000.0
MEM_THRESHOLD_DOWN = 2097152.0
HOST = 'localhost'
PORT = 8086
USER = 'root'
PASS = 'root'
DATABASE = 'cadvisor'
SELECT_CPU = 'derivative(cpu_cumulative_usage)'
SELECT_MEMORY = 'median(memory_usage)'
SERIES = '"stats"'
APP_NAME = 'demo-server'
NAME = ''
WHERE_BEGIN = 'container_name =~ /.*'
WHERE_END = '.*/ and time>now()-5m'
GROUP_BY = "time(10s), container_name"
CONDITION = " limit 1 "
JSON_APP_DEFINE = './demo_web_server.json'
APP_ID = 'demo-server'
MARATHON_URI = 'localhost:8080'
HEADER = {'Content-Type': 'application/json'}
# scale
SCALE_LINK = '/v2/apps/' + APP_ID + '?force=true'
TIME_DELAY_LONG = 15
TIME_DELAY_SORT = 5

ROOT_PASSWORD = ''
MODEL_ENGINE = 'mysql+pymysql://root:autoscaling@secret@127.0.0.1:3306/policydb'
SCHEMA = '''
# PolicyDB
# apps.enabled: 0-not scaled, 1-scaled
# apps.locked: 0-unlocked, 1-locked
# apps.next_time: time in the future the app'll be checked for scaling
#   next_time = last success caused by policyX + policyX.cooldown_period
# policies.metric_type: 0-CPU, 1-memory
# policies.cooldown_period: in second
# policies.measurement_period: in second
# deleted: 0-active, 1-deleted
DROP DATABASE IF EXISTS policydb;
CREATE DATABASE policydb;
USE policydb;
CREATE TABLE apps(\
    Id INT AUTO_INCREMENT PRIMARY KEY, \
    app_uuid VARCHAR(255), \
    name VARCHAR(255), \
    min_instances SMALLINT UNSIGNED, \
    max_instances SMALLINT UNSIGNED, \
    enabled TINYINT UNSIGNED, \
    locked TINYINT UNSIGNED, \
    next_time INT \
);
CREATE TABLE policies(\
    Id INT AUTO_INCREMENT PRIMARY KEY, \
    app_uuid VARCHAR(255), \
    policy_uuid VARCHAR(255), \
    metric_type TINYINT UNSIGNED, \
    upper_threshold FLOAT, \
    lower_threshold FLOAT, \
    instances_out SMALLINT UNSIGNED, \
    instances_in SMALLINT UNSIGNED, \
    cooldown_period SMALLINT UNSIGNED, \
    measurement_period SMALLINT UNSIGNED, \
    deleted TINYINT UNSIGNED \

);
# tuna
CREATE TABLE crons(\
    Id INT AUTO_INCREMENT PRIMARY KEY, \
    app_uuid VARCHAR(255), \
    cron_uuid VARCHAR(255), \
    min_instances SMALLINT UNSIGNED, \
    max_instances SMALLINT UNSIGNED, \
    cron_string VARCHAR(255), \
    deleted TINYINT UNSIGNED \
);
# end tuna
-----

# Test data

# Stresser
INSERT INTO apps(app_uuid, name, min_instances, max_instances, enabled, locked, next_time) \
VALUES ("f5bfcbad-7daa-4317-97cc-e42ae46b6ad1", "java-allocateMemory", 1, 5, 1, 0, 0);
INSERT INTO policies(app_uuid, policy_uuid, metric_type, upper_threshold, lower_threshold, instances_out, instances_in, cooldown_period, measurement_period, deleted) \
VALUES ("f5bfcbad-7daa-4317-97cc-e42ae46b6ad1", "b3da4493-58f1-4d65-bf43-e52e7de62151", 1, 0.7, 0.3, 1, 1, 30, 10, 0);
# INSERT INTO policies(app_uuid, policy_uuid, metric_type, upper_threshold, lower_threshold, instances_out, instances_in, cooldown_period, measurement_period, deleted) \
# VALUES ("f5bfcbad-7daa-4317-97cc-e42ae46b6ad1", "b3da4493-58f1-4d65-bf43-e52e7dpolicy", 1, 0.7, 0.3, 1, 1, 30, 10, 0);
INSERT INTO crons(app_uuid, cron_uuid, min_instances, max_instances, cron_string, deleted) \
VALUES ("f5bfcbad-7daa-4317-97cc-e42ae46b6ad1", "b3da4493-58f1-4d65-bf43-e52eacascron", 1, 10, "* * * * * *", false);
'''


