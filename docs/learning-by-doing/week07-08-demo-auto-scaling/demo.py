__author__ = 'huanpc'

import time
from time import gmtime, strftime
from influxdb.influxdb08 import InfluxDBClient
import http.client
import os
import constant
import logging
import sys
from marathon import MarathonClient
import MySQLdb
#
logger = logging.getLogger('auto_scaling_system')
logging.basicConfig(stream=sys.stderr, level=getattr(logging, 'INFO'))
influxdb_client = InfluxDBClient(constant.HOST, constant.PORT, constant.USER, constant.PASS, constant.DATABASE)
marathon_client = MarathonClient('http://localhost:8080')
db = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="autoscaling@secret",db="policydb")
#
def getListTaskForApp():
    task_list = []
    raw_data = marathon_client.list_tasks(constant.APP_NAME)
    for id in raw_data:
        index = str(id).find('::')+2
        task_list.append(str(id)[index:])
    return task_list

def get_list_container_for_app(task_list):
    containerNameList = []
    for task_id in task_list:
        query = 'select container_name from mapping where' + ' mesos_task_id =~/.' + '*' + task_id + '.*/ limit 1'
        result = influxdb_client.query(query)
        containerName = result[0]['points'][0][2]
        logger.info(task_id + ' @@ ' + containerName)
        containerNameList.append(containerName)
    return containerNameList

def get_cpu_usage_for_containers(container_id_list):
    container_usage_list = []
    for container_id in container_id_list:
        query = "select " + constant.SELECT_CPU + " from " + constant.SERIES + " where " + constant.WHERE_BEGIN + container_id + constant.WHERE_END + " group by " + constant.GROUP_BY + constant.CONDITION
        result = influxdb_client.query(query)
        if len(result) > 0:
            cpuUsage = result[0][u'points'][0][1] / 10 ** 9 / 4
        else:
            cpuUsage = 0
        container_usage_list.append(cpuUsage)
    return container_usage_list

def get_memory_usage_for_containers(container_id_list):
    container_usage_list = []
    for container_id in container_id_list:
        query = "select " + constant.SELECT_MEMORY + " from " + constant.SERIES + " where " + constant.WHERE_BEGIN + container_id + constant.WHERE_END + " group by " + constant.GROUP_BY + constant.CONDITION
        result = influxdb_client.query(query)
        if len(result) > 0:
            memUsage = result[0]['points'][0][1]
        else:
            memUsage = 0
        container_usage_list.append(memUsage)
    return container_usage_list

def deployApplication(jsonFile):
    data = open(jsonFile)
    con = http.client.HTTPConnection(constant.MARATHON_URI)
    con.request('POST', '/v2/apps', data.read(), constant.HEADER)
    response = con.getresponse()
    logger.info(response.read().decode())
    return True


def scaling(numOfInstance):
    result = marathon_client.scale_app(constant.APP_NAME, numOfInstance)
    logger.info('scale result: '+ result)
    time.sleep(constant.TIME_DELAY_SORT)
    updateHaproxy()

def get_policies_from_policyDB(app_uuid):
    rules = dict()
    cur = db.cursor()
    cur.execute('SELECT * from policies where app_uuid ="'+app_uuid+'"')
    row = cur.fetchall()
    row = row[0]
    rules['app_uuid'] = app_uuid
    rules['policy_uuid'] = row[2]
    rules['metric_type'] = row[3]
    rules['upper_threshold'] = row[4]
    rules['lower_threshold'] = row[5]
    rules['instances_out'] = row[6]
    rules['instances_in'] = row[7]
    rules['cooldown_period'] = row[8]
    rules['measurement_period'] = row[9]
    rules['deleted'] = row[10]
    return rules

def update_policies_to_policyDB(app_uuid, rules):
    cur = db.cursor()
    cur.execute('''UPDATE policies SET metric_type=%s, upper_threshold=%s, lower_threshold=%s, instances_out=%s,
    instances_in=%s, cooldown_period=%s, measurement_period=%s, deleted=%s where app_uuid ="'''+app_uuid+'"',(rules.values()))

def create_app_to_policyDB(value = dict()):
    cur = db.cursor()
    cur.execute('''INSERT INTO apps (app_uuid,name,min_instances,max_instances,enabled,locked,next_time)
    VALUES (%s,%s,%s,%s,%s,%s,%s)''', (value.values()))

def checkMemoryBasedRule(container, mem, numOfInstance):
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if (mem > constant.MEM_THRESHOLD_UP and mem != 0):
        numOfInstance += 1
        logger.info('--------------------------------------------------------------')        
        logger.info(currentTime + '|' + container + '|MEMORY_USAGE|' + str(mem) + "|scalling up, add 1 instance")
        logger.info('App has ' + str(numOfInstance) + ' instances')
        scaling(numOfInstance)
        logger.info('--------------------------------------------------------------')
        return True
    elif (mem <= constant.MEM_THRESHOLD_DOWN and mem != 0):
        if numOfInstance > 1:
            numOfInstance -= 1
            logger.info('--------------------------------------------------------------')
            logger.info(currentTime + '|' + container + '|MEMORY_USAGE|' + str(mem) + "|scalling down, turn off 1 instance")
            logger.info('App has ' + str(numOfInstance) + ' instances')
            scaling(numOfInstance)
            logger.info('--------------------------------------------------------------')
            return True
    else:
        return False


def checkCpuBasedRule(container, Cpu, numOfInstance):
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if (Cpu > constant.CPU_THRESHOLD_UP and Cpu != 0):
        numOfInstance += 1
        logger.info('--------------------------------------------------------------')
        logger.info(currentTime + '|' + container + '|CPU_USAGE|' + str(Cpu) + "|scalling up, add 1 instance")
        logger.info('App has ' + str(numOfInstance) + ' instances')
        scaling(numOfInstance)
        logger.info('--------------------------------------------------------------')
        return True
    elif (Cpu <= constant.CPU_THRESHOLD_DOWN and Cpu != 0):
        if numOfInstance > 1:
            numOfInstance -= 1
            logger.info('--------------------------------------------------------------')
            logger.info(currentTime + '|' + container + '|CPU_USAGE|' + str(Cpu) + "|scalling down, turn off 1 instance")
            logger.info('App has ' + str(numOfInstance) + ' instances')
            scaling(numOfInstance)
            logger.info('--------------------------------------------------------------')
            return True
    else:
        return False


def updateHaproxy():

    command = 'sudo python ./servicerouter.py --marathon http://localhost:8080 --haproxy-config /etc/haproxy/haproxy.cfg'
    os.system('echo %s|sudo -S %s' % (constant.ROOT_PASSWORD, command))

def connect_database():
    db = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="autoscaling@secret",db="policydb")
    cur = db.cursor()
    cur.execute(constant.SCHEMA)

def main():
    connect_database()
    updateHaproxy()
    while True:
        taskIdList = getListTaskForApp()
        num = len(taskIdList)
        #
        logger.info('################')
        logger.info(str(num) + " instances")
        logger.info('TASK_ID @@ CONTAINER_ID')
        #
        containerNameList = get_list_container_for_app(taskIdList)
        containerCpuUsageList = get_cpu_usage_for_containers(containerNameList)
        containerMemUsageList = get_memory_usage_for_containers(containerNameList)
        # CHECK INSTANCES ONE BY ONE AND SCALE
        logger.info('################')
        numOfInstance = num
        for i in range(num):
            if (checkMemoryBasedRule(containerNameList[i], containerMemUsageList[i], numOfInstance)):
                continue
            else:
                checkCpuBasedRule(containerNameList[i], containerCpuUsageList[i], numOfInstance)
        time.sleep(constant.TIME_DELAY_LONG)

if __name__ == '__main__':
    main()
